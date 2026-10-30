from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, computed_field, field_validator

from hmtracker.database.models import PlayerInfoType


class Season(BaseModel):
    id: int
    name: str
    start: date
    end: date
    arcade: bool = False


class HockeyPlayer(BaseModel):
    id: int
    season_id: int
    name: str
    role: str
    foreigner: bool


class NewsArticle(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    base_url: str
    article_url: str
    article_date: date
    title: str
    processed_by: str | None
    processed_date: datetime | None


class PlayerNews(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    season_id: int | None
    player_id: int | None
    article_id: int
    player_name: str
    confirmed: bool
    info_type: PlayerInfoType
    current_team: str | None
    new_team: str | None
    availability_time: str | None
    article: NewsArticle


class HockeyPlayerStats(BaseModel):
    player_id: int
    season_id: int
    validity_date: datetime
    import_id: Optional[int] = None
    price: float
    club: str
    ownership: Optional[float] = None
    hm_points: Optional[int] = None
    appearances: Optional[int] = None
    goal: Optional[int] = None
    assists: Optional[int] = None
    penalties: Optional[int] = None
    plus_minus: Optional[int] = None

    @computed_field
    def estimated_value(self) -> Optional[float]:
        if self.appearances is None or self.hm_points is None:
            return None
        return self.hm_points / self.appearances


class StatImport(BaseModel):
    id: int
    import_date: datetime
    origin: str = "Unknown"
    comment: str = ""


class Manager(BaseModel):
    id: int
    email: Optional[str] = None
    last_import: Optional[datetime] = None
    autolineup: bool = False

    @field_validator("autolineup", mode="before")
    @classmethod
    def convert_none_to_default(cls, autolineup):
        if autolineup is None:
            return False
        return autolineup


class Team(BaseModel):
    id: int
    team: str
    manager_id: int
    player_id: int
    season_id: int
    from_datetime: Optional[datetime] = None
    to_datetime: Optional[datetime] = None


class Task(BaseModel):
    id: int
    name: str
    start_at: datetime
    end_at: datetime
    error: Optional[str] = None
    stacktrace: Optional[str] = None
