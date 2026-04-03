from datetime import datetime

from db_utils import get_time
from sqlmodel import Field, SQLModel


class Meme(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    game_name: str
    file_path: str
    year: int
    created_at: datetime = Field(default_factory=get_time)


class MemeStats(SQLModel, table=True):
    meme_id: int = Field(primary_key=True, foreign_key="meme.id")
    access_count: int = 0
    last_accessed: datetime | None = None
