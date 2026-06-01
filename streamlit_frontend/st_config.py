from pathlib import Path


class FrontendPaths:
    def __init__(self):
        self._frontend_base_dir = Path(__file__).resolve().parent

    @property
    def assets_dir(self):
        return self._frontend_base_dir / "assets"

    @property
    def welcome_image(self):
        return self.assets_dir / "welcome.png"


frontend_paths = FrontendPaths()
