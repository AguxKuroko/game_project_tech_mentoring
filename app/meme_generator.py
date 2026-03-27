import base64
from pathlib import Path

from openai import OpenAI

from app.api_keys_config import api_game_key
from app.models import RawgApiData
from app.utils import extract_screenshots, prepare_images_for_openai


def generate_game_meme(game_data: RawgApiData):
    client = OpenAI(api_key=api_game_key.OPEN_AI_API_KEY)
    prompt_for_openai = f"""
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

    result = client.images.edit(
        model="gpt-image-1",
        image=prepare_images_for_openai(extract_screenshots(game_data.game_screenhosts)),
        prompt=prompt_for_openai,
        size="1024x1024",
    )

    image_base64 = result.data[0].b64_json

    file_path = Path("app") / "memes" / f"{game_data.game_name}_{game_data.game_release_year}.png"
    file_path.write_bytes(base64.b64decode(image_base64))


testing = RawgApiData(
    game_name="Footbal",
    game_id=1,
    game_release_year="2023",
    game_meta_score=46,
    game_genre=["rpg", "fantasy"],
    game_dropped_count=20,
    game_screenhosts=[
        {
            "id": -1,
            "image": "https://media.rawg.io/media/games/eb1/eb1ff1ffdab179ff7f0987d0266d4fe5.jpg",
        },
        {
            "id": 3041606,
            "image": "https://media.rawg.io/media/screenshots/892/892482b5c321ad3a50e326a7590e600d.jpg",
        },
        {
            "id": 3041607,
            "image": "https://media.rawg.io/media/screenshots/2c5/2c5320d66d2ea60e3890a826062c3a48.jpg",
        },
        {
            "id": 3041611,
            "image": "https://media.rawg.io/media/screenshots/d90/d90b65cb2ba72a999b09d05347d9f1e0_xb1sBfq.jpg",
        },
    ],
)

generate_game_meme(testing)
