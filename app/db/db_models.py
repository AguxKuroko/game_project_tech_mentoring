from datetime import datetime

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

from app.db.db_utils import get_time


class Meme(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    game_name: str
    metascore: int
    file_path: str = Field(index=True, unique=True)
    year: int
    created_at: datetime = Field(default_factory=get_time)


class MemeStats(SQLModel, table=True):
    meme_id: int = Field(primary_key=True, foreign_key="meme.id")
    access_count: int = 0
    last_accessed: datetime | None = None


class MemeTopResponse(BaseModel):
    game_name: str
    game_metascore: int
    year: int
    image_url: str
    access_count: int
