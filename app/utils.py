import re
from contextlib import asynccontextmanager
from io import BytesIO

import requests
from fastapi import FastAPI, HTTPException, status
from openai import OpenAI
from openai.types.images_response import ImagesResponse
from sqlmodel import SQLModel

from app.app_config import ConfigAppMode
from app.db.db_models import Meme, MemeStats  # noqa: F401
from app.db.engine import get_engine
from app.models import RawgApiData


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
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            raise HTTPException(  # noqa: B904
                status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to download screenshot: {url}"
            )

        img = BytesIO(response.content)
        img.name = f"image_{number}.jpg"

        image_files.append(img)

    return image_files


def build_prompt(game_data: RawgApiData, mode: str) -> str:
    """Create a dynamic prompt for the OpenAI model based on game data.

    The game_data object is a model that stores information retrieved from the game API.
    This data is injected into the prompt, so each prompt is built dynamically
    (e.g., game name, genre, release year, etc.).
    """
    base_prompt = f"""
Create a funny and visually engaging internet meme with a stylized,
cartoon-like video game aesthetic.

Context:
You are given images from a video game. Use them only as visual inspiration (colors, characters,
environment), but transform them into a new, original and exaggerated scene.

Game data:
- Title: "{game_data.game_name}"
- Genre: {", ".join(game_data.game_genre)}
- Release year: {game_data.game_release_year}
- Review score: {game_data.game_meta_score}
- Number of players who stopped playing: {game_data.game_dropped_count}

Visual style:
- Use vibrant but slightly distorted or “buggy” colors, like a poorly designed or broken game
- Add noticeable gaming effects such as glitch artifacts, pixelation, scanlines, UI overlays,
or fake HUD elements (health bars, menus, warning text)
- Slightly exaggerate proportions or expressions to enhance humor
- Make the image visually striking and dynamic, but not cluttered
- Strongly reflect the game genre in the entire scene:
- Sports → stadium, players, scoreboard, dynamic action
- Fantasy → magic, dark atmosphere, mythical elements
- Shooter → weapons, chaos, explosions, tactical UI
- RPG → characters, dialogue UI, quest-like elements

Text (VERY IMPORTANT):
- All text must be fully visible, centered, and NEVER cut off
- Keep large safe margins from all edges (at least 15–20%)
- Prefer placing text in the upper and middle areas (avoid bottom edge)
- Use short text (max 6–10 words per line)
- Break text into multiple lines if needed
- Use bold, large, high-contrast meme-style font
- Add strong outline or shadow for readability

Text content:
- Clearly highlight the game title "{game_data.game_name}" (larger font, strong emphasis)
- Include the release year "{game_data.game_release_year}" in a clean, readable way
- Add a short, punchy meme caption (simple setup → punchline)
- Keep the caption simple, bold, and instantly understandable in under 2 seconds

Metascore display (VERY IMPORTANT):
- Display the metascore clearly as text: "METASCORE: {game_data.game_meta_score}"
- Place it inside a bold, visible frame or badge
- The badge should be red or dark red
- Add a dripping or melting effect (like paint dripping) for dramatic and humorous effect
- Make this element stand out visually, like a warning or failure indicator in a game UI

Humor logic:
- Convert the data into a relatable or absurd gaming situation
- Focus on player experience, expectations vs reality, or surprising outcomes
- Use exaggeration and irony

How to use the data:
- Use the metascore to imply player experience (confusion, struggle, chaos)
- Use the dropped player count to suggest behavior (leaving early, unexpected reactions)
- Use genre and visuals to shape the joke
- Use release year to create contrast (modern vs outdated feeling)

Important rules:
- Do NOT clutter the image with too much text
- Do NOT place text near edges where it could be cut off
- Do NOT distort or obscure readability
- Do NOT simply repeat raw data as the joke
- If text does not fit clearly, reduce text instead of shrinking it

Tone:
- Ironic, playful, chaotic, slightly cursed
- Feels like a parody of a strange or broken video game

Goal:
Create ONE cohesive meme image that is visually strong, readable, and instantly understandable.
"""

    if mode == "dog":
        base_prompt += "\nSecret 'DOG' mode: \nTransform each character into a unique dog breed."

    return base_prompt


def clean_filename(game_data_name: str) -> str:
    """Sanitize a game name string to create a safe filename"""
    return re.sub(r"[^\w\s-]", "", game_data_name).strip().replace(" ", "_")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('🎮 Booting up the "Worst Game Meme Generator"... Brace yourself for terrible games! 🎮')
    SQLModel.metadata.create_all(get_engine())
    yield
    print("💀 The meme machine rests... until next time. 💀'")


def generate_meme_without_images(game_data: RawgApiData, meme_mode: ConfigAppMode, client: OpenAI) -> ImagesResponse:
    """Fallback: generates a meme using only a prompt when no screenshots are provided."""
    try:
        return client.images.generate(
            model="gpt-image-1",
            prompt=build_prompt(game_data, meme_mode),
            size="1024x1024",
        )
    except Exception:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate meme"
        )
