import logging
from logging.handlers import RotatingFileHandler

import logfire

from app.api_keys_config import get_api_keys
from app.app_config import app_paths


def setup_logging():
    logger = logging.getLogger()

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        app_paths.logs_dir.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s | %(filename)s:%(lineno)d (%(funcName)s)")

        file_handler = RotatingFileHandler(
            app_paths.logs_dir / "worst_game_meme_app.log",
            maxBytes=1_000_000,
            backupCount=3,
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.addHandler(logfire.LogfireLoggingHandler())

        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logfire.configure(
        service_name="worst-game-meme-app",
        token=get_api_keys().LOGFIRE_TOKEN,
    )
