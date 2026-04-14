from enum import StrEnum, auto
from pathlib import Path


class ConfigPath:
    def __init__(self):
        self._app_base_dir = Path(__file__).resolve().parent

    @property
    def home_image(self) -> Path:
        return self._app_base_dir / "home_endpoint_image" / "welcome.png"

    @property
    def db_dir(self):
        return self._app_base_dir / "db"

    @property
    def memes_dir(self) -> Path:
        return self.db_dir / "memes"


app_paths = ConfigPath()


class ConfigResponseFormat(StrEnum):
    image = auto()
    json = auto()


class ConfigAppMode(StrEnum):
    dog = auto()
    normal = auto()
