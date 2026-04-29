import logging
from logging.handlers import RotatingFileHandler

from app_config import app_paths


def setup_logging():
    logger = logging.getLogger()

    if logger.handlers:
        return

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")

    # Rotating file handler (ONLY one file handler)
    file_handler = RotatingFileHandler(app_paths.logs_dir / "worst_game_meme_app.log", maxBytes=1_000_000, backupCount=3)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


setup_logging()
logger = logging.getLogger(__name__)

logger.info("Something happened")
