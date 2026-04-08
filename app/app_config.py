from enum import StrEnum
from pathlib import Path


class ConfigPath:
    def __init__(self):
        self._app_base_dir = Path(__file__).parent

    @property
    def home_dir(self) -> Path:
        return self._app_base_dir / "home_endpoint_image" / "welcome.png"

    @property
    def memes_dir(self) -> Path:
        return self._app_base_dir / "memes"


app_paths = ConfigPath()


class ConfigResponseFormat(StrEnum):
    image = "image"
    json = "json"
