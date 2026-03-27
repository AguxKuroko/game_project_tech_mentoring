from enum import StrEnum

from pydantic import BaseModel


class RawgApiData(BaseModel):
    game_name: str
    game_id: int
    game_release_year: str
    game_meta_score: int
    game_genre: list
    game_dropped_count: int
    game_screenhosts: list


class ResponseFormat(StrEnum):
    image = "image"
    json = "json"
