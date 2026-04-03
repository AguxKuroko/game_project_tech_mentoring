from datetime import datetime

from sqlmodel import Field, SQLModel


class Meme(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    file_path: str
    year: int
    created_at: datetime = Field(default_factory=datetime.timezone.utc)


class MemeStats(SQLModel, table=True):
    meme_id: int = Field(primary_key=True, foreign_key="meme.id")
    access_count: int = 0
    last_accessed: datetime | None = None
