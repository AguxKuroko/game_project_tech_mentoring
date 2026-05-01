import base64
import logging
from pathlib import Path

from openai import BadRequestError, OpenAI

from app.api_keys_config import api_game_key
from app.app_config import ConfigAppMode, app_paths
from app.models import RawgApiData
from app.utils import build_prompt, clean_filename, extract_screenshots, generate_meme_without_images, prepare_images_for_openai

logger = logging.getLogger(__name__)


def generate_game_meme(game_data: RawgApiData, meme_mode: ConfigAppMode, save: bool = True) -> Path | bytes:
    logger.info("Initializing OpenAI client")
    client = OpenAI(api_key=api_game_key.OPEN_AI_API_KEY)

    images = prepare_images_for_openai(extract_screenshots(game_data.game_screenhosts))

    if not images:  # when we do not have screenshots, otherwise app will crash
        logger.info("No screenshots available | using fallback generation")
        result = generate_meme_without_images(game_data, meme_mode, client)

    else:
        try:
            logger.info("Generating meme with screenshots")
            result = client.images.edit(
                model="gpt-image-1",
                image=images,
                prompt=build_prompt(game_data, meme_mode),
                size="1024x1024",
            )

        except BadRequestError:
            logger.warning("OpenAI image edit failed | falling back to generation without screenshots", exc_info=True)
            result = generate_meme_without_images(game_data, meme_mode, client)

    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    if save:
        logger.info(f"Saving meme | game={game_data.game_name}")
        file_path = app_paths.memes_dir / f"{clean_filename(game_data.game_name)}_{game_data.game_release_year}.png"
        file_path.write_bytes(image_bytes)
        return file_path

    logger.info("Meme generated | mode=dog | not saved")
    return image_bytes
