import base64
from pathlib import Path

from openai import OpenAI

from app.api_keys_config import api_game_key
from app.app_config import app_paths
from app.models import RawgApiData
from app.utils import build_prompt, clean_filename, extract_screenshots, prepare_images_for_openai


def generate_game_meme(game_data: RawgApiData, meme_mode: str, save: bool = True) -> Path | bytes:
    client = OpenAI(api_key=api_game_key.OPEN_AI_API_KEY)

    result = client.images.edit(
        model="gpt-image-1",
        image=prepare_images_for_openai(extract_screenshots(game_data.game_screenhosts)),
        prompt=build_prompt(game_data, meme_mode),
        size="1024x1024",
    )

    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    if save:
        file_path = app_paths.memes_dir / f"{clean_filename(game_data.game_name)}_{game_data.game_release_year}.png"
        file_path.write_bytes(image_bytes)
        return file_path

    return image_bytes
