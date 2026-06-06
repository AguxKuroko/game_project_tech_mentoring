import logging
import random
import re
from contextlib import asynccontextmanager
from io import BytesIO

import requests
from fastapi import FastAPI, HTTPException, status
from openai import BadRequestError, OpenAI
from openai.types.images_response import ImagesResponse
from sqlmodel import SQLModel

from app.app_config import ConfigAppMode, app_paths
from app.db.db_models import Meme, MemeStats  # noqa: F401
from app.db.engine import get_engine
from app.models import RawgApiData

logger = logging.getLogger(__name__)

CAPTION_STYLES = [
    "ROAST: brutal one-liner insulting the game's quality directly, like a comedy roast set",
    "ANCESTRAL SHAME: claim the game is a generational disgrace — ancestors, bloodline, family curse",
    "CRIME SCENE: frame playing this game as a criminal act or war crime — lawyers, witnesses, evidence",
    "RELATIONSHIP RUIN: this game ended a marriage, friendship, or family — be specific about the damage",
    "OVER-THE-TOP COMPARISON: compare playing this to something WORSE than a real disaster — "
    "the comparison must be COHERENT and tied to suffering or bad experiences, NOT random nonsense words",
    "REGRET SPIRAL: list specific awful life consequences this game caused — be petty and detailed",
    "MEDICAL DIAGNOSIS: treat the game as a diagnosable illness, curse, or psychological condition",
    "FAKE 1-STAR REVIEW: bitter user review distilled into a meme caption — like Yelp meets a breakup text",
    "REVERSE FLEX: pretend to brag about something that's actually devastating about playing the game",
    "DARK CONFESSION: someone confessing the game ruined a very specific part of their life",
]


def extract_release_year(release_year_from_api: dict) -> str:
    """Extract YEAR from full datetime str or int"""
    year = release_year_from_api.get("released")

    if not year:  # covers None, empty string, and invalid 0 values
        return "Data not provided"

    if isinstance(year, int):
        return str(year)
    elif isinstance(year, str):
        return year.split("-")[0]

    return "Data not provided"


def extract_genres(genres: list[dict]) -> list[str]:
    """Extract all genre names for the worst game of a given year."""
    return [result for genre in genres if (result := genre.get("name"))]


def extract_screenshots(screenshots_raw: list[dict]) -> list[str]:
    """Extract and normalize valid screenshot URLs for the meme generator."""
    return [image for screenshot in screenshots_raw if (image := screenshot.get("image"))]


def prepare_images_for_openai(screenshots: list[str]) -> list[BytesIO]:
    """Fetch images from URLs and transform them into BytesIO objects compatible with OpenAI API."""
    image_files = []

    for number, url in enumerate(screenshots[:3]):
        try:
            logger.info(f"Fetching screenshot | index={number}", extra={"index": number, "step": "fetch_screenshot"})
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            logger.error(f"Screenshot download failed | url={url}", extra={"url": url, "step": "download_error"}, exc_info=True)
            raise HTTPException(  # noqa: B904
                status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Failed to download screenshot: {url}"
            )

        img = BytesIO(response.content)
        img.name = f"image_{number}.jpg"

        image_files.append(img)

    logger.info(f"Prepared images for OpenAI | count={len(image_files)}", extra={"count": len(image_files), "step": "prepare_images"})
    return image_files


def build_prompt(game_data: RawgApiData, mode: str) -> str:
    """Create a dynamic prompt for the OpenAI model based on game data.

    The game_data object is a model that stores information retrieved from the game API.
    This data is injected into the prompt, so each prompt is built dynamically
    (e.g., game name, genre, release year, etc.).
    """
    caption_style = random.choice(CAPTION_STYLES)

    base_prompt = f"""
Create a 1024x1024 internet meme image — cartoon video game aesthetic, with text.

ABSOLUTE PRIORITY: ALL TEXT MUST BE CLEARLY VISIBLE AND READABLE. Nothing cut off, nothing faded, nothing blurry.

Game data:
- Title: "{game_data.game_name}"
- Genre: {", ".join(game_data.game_genre)}
- Metascore: {game_data.game_meta_score} (out of 100 — lower is worse)
- Players who quit: {game_data.game_dropped_count}

IMAGE vs TEXT BALANCE: the cartoon ARTWORK fills 65-70% of the image. Text is small support — never dominating.

LAYOUT — three strict non-overlapping zones:
1. TOP STRIP (top ~15% of image only): GAME TITLE "{game_data.game_name}" — bold, centered, ONE line, MEDIUM size (not giant)
2. MIDDLE: ARTWORK takes the whole middle. Caption sits over the artwork around 55-65% height — small-to-medium bold text, 4-7 words, ONE line
3. BOTTOM-RIGHT CORNER ONLY: METASCORE badge "METASCORE: {game_data.game_meta_score}" — small red/dark red sticker with paint-drip effect, max 15% of image width

TEXT SIZING (very important — keep text PROPORTIONATE):
- Title height: about 10-12% of image height (medium, not huge)
- Caption height: about 7-9% of image height (smaller than title)
- Badge text: small, fits inside the badge
- The image / artwork is the star; the text is a label, not the subject
- Bold meme font with thick black outline + drop shadow for readability
- If words don't fit, SHORTEN the caption — do not enlarge the text

CAPTION — this is the joke. Style for this meme: {caption_style}

The caption must be a BRUTAL ROAST. Mean, petty, specific, cringe-funny.
Stand-up comedy insult energy. Make fun of the game directly.

WHAT MAKES A CAPTION ACTUALLY FUNNY (read carefully):
- Be SPECIFIC and SURPRISING — lean into THIS game's genre, characters, setting, or context for the joke
- Lazy "worse than [thing]" comparisons are the WEAKEST kind of roast — AVOID them
  * "Worse than eating glass" / "worse than X" patterns are banned unless the X is unexpected, specific, and game-relevant
- A weird, petty, surprising angle beats a safe one every time
- Land the joke with setup + punchline rhythm — even in a short line
- Length: 4-9 words, ONE line (a few extra words are fine if they make the joke land harder)

JOKE MECHANISMS (use AT LEAST ONE — flat factual statements are NOT jokes):
- PERSONIFICATION: treat game elements as if they're human ("Even the NPCs logged off", "The dragon filed a complaint")
- ABSURD EXAGGERATION: take suffering to a ridiculous extreme ("Made my therapist need a therapist")
- SUBVERTED EXPECTATION: setup makes reader expect X, punchline delivers Y
- SPECIFIC DETAIL: the more concrete, the funnier ("11 minutes in" beats "minutes in")
- IRONY: the result is the opposite of what should happen ("Speedrunning the uninstall button")

DO NOT just describe what happens in the game — that's a fact, not a joke.
BAD (flat fact): "Six player characters quit" — true, but no joke mechanism
GOOD (same idea, with mechanism): "Even the NPCs took a personal day" (personification + irony)

FLAT vs FUNNY transformations (study these patterns):
- FLAT: "The graphics are bad"
  FUNNY: "My retinas filed a workplace injury claim" (exaggeration + personification)
- FLAT: "Players hated it"
  FUNNY: "Players speedrunning the uninstall button" (specific + ironic)
- FLAT: "This game has bugs"
  FUNNY: "Bugs filed bugs about the bugs" (recursion + personification)
- FLAT: "Six player characters quit"
  FUNNY: "Even the NPCs called in sick" (personification + workplace humor)

COMPREHENSIBILITY RULE (CRITICAL — do not skip):
- The caption MUST be a joke that ANY reader immediately understands
- "Surprising" means unexpected angle, NOT random words
- BAD: "Installed quaker oats on a zeppelin" — random nonsense, no joke
- GOOD: "Mothership demanded a refund" — unexpected but you get it
- Test: would a stranger glancing at this caption think "lol, fair" or "huh, what?"
- If "huh, what?" → start over. Random absurdity is NOT funny.

GAME-CONTEXT MATCH (CRITICAL — the joke must fit THIS specific game):
- The caption MUST land in the context of this game's genre, characters, setting, or vibe
- The chosen caption style above is a STARTING HINT — adapt it (or pivot to a different angle) if it doesn't naturally fit this game
- Self-check: if you swapped this game with a completely different one, would the joke still land?
  * If YES → the caption is too generic. Redo with a game-aware angle.
- Examples of GOOD context-fit:
  * Fantasy/dragon game → "Even the dragon filed for early retirement"
  * Racing game → "Cars filed a class action"
  * Shooter → "Enemies started ghosting me"
  * Sports → "Refs requested a transfer"
  * Alien game → "Mothership demanded a refund"
  * City builder → "Made urban planners cry actual tears"
- Examples of BAD context-fit (would FAIL this rule):
  * "Six witnesses called my attorney" on a dragon fantasy game (zero connection)
  * Any caption that could apply to literally any bad game

BANNED words: discover, experience, moments, vibes, journey, romance, adventure, explore, feel, magical, epic.
BANNED phrases: "this game though", "what an experience", "is this even", "moments like these", "worse than eating glass", lazy "worse than X" generic comparisons.

GOOD caption energy (inspiration only — generate ORIGINAL, do NOT copy):
- "Made my ancestors quit gaming"
- "Played once, called my lawyer"
- "If pain had a save file"
- "10 minutes in, divorce filed"
- "Diagnosed me with regret"
- "Even the aliens filed restraining orders" (alien game = specific)
- "Wikipedia refused to write an article"
- "Made urban planners cry actual tears" (city game = specific)
- "My ancestors saw better graphics"
- "Speedrun world record: closing the game"

ARTWORK STYLE (this is the main visual — expressive, original, with a light retro vibe):
- Create a NEW original cartoon illustration — do NOT use the input screenshots as the image itself
- Take only colors, characters, and themes from the screenshots; redraw them in a stylized cartoon comic style
- Light retro video-game atmosphere (subtle, not overwhelming):
  * Faint CRT scanline texture in the background
  * Slightly distorted "buggy" colors, hint of chromatic aberration on edges
  * Vibrant but slightly off color palette — like a TV with the colors a bit wrong
- Optional atmospheric details (use sparingly — ONE or TWO, not plastered everywhere): a single "WARNING" sign, a small HUD element, a faint health bar in a corner
- DO NOT cover the image with "ERROR" / "GAME OVER" / random text overlays — keep retro effects atmospheric, not literal
- Stylized cartoon characters with exaggerated proportions, dramatic facial expressions, dynamic poses
- The scene should feel like a cursed broken video game — atmospheric retro vibe, joke first
- The scene should be funny ON ITS OWN, before you even read the caption
- Dynamic and detailed but NOT cluttered — leave room for the text zones to sit cleanly

GOAL: a meme that's a real cartoon illustration with small text labels. Caption nasty, art does most of the work.
"""

    if mode == "dog":
        base_prompt += "\nSecret 'DOG' mode: \nTransform each character into a unique dog breed."

    return base_prompt


def clean_filename(game_data_name: str) -> str:
    """Sanitize a game name string to create a safe filename"""
    return re.sub(r"[^\w\s-]", "", game_data_name).strip().replace(" ", "_")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting app", extra={"event": "startup"})
    print('🎮 Booting up the "Worst Game Meme Generator"... Brace yourself for terrible games! 🎮')
    print("🌐 Open http://localhost:8000/docs in your browser")
    app_paths.memes_dir.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(get_engine())
    yield
    logger.info("Shutting down app", extra={"event": "shutdown"})
    print("💀 The meme machine rests... until next time. 💀'")


def generate_meme_without_images(game_data: RawgApiData, meme_mode: ConfigAppMode, client: OpenAI) -> ImagesResponse:
    """Fallback: generates a meme using only a prompt when no screenshots are provided."""
    logger.info("Generating meme without screenshots", extra={"step": "generate_without_images"})
    try:
        return client.images.generate(
            model="gpt-image-1",
            prompt=build_prompt(game_data, meme_mode),
            size="1024x1024",
        )
    except BadRequestError:
        logger.error("Prompt blocked by OpenAI moderation", extra={"step": "generation_blocked"}, exc_info=True)

        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Meme generation failed due to content restrictions."
        )
