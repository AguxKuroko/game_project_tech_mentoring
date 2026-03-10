from pydantic import BaseModel


class RawgApiData(BaseModel):
    game_name: str
    game_id: int
    game_release_year: str
    game_meta_score: int | None
    game_screenhosts: list
