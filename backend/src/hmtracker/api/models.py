from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


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


class StatImport(BaseModel):
    id: int
    import_date: datetime
    origin: str = "Unknown"
    comment: str = ""


class Manager(BaseModel):
    id: int
    email: Optional[str] = None


class Team(BaseModel):
    id: int
    team: str
    manager_id: int
    player_id: int
    season_id: int
    from_datetime: Optional[datetime] = None
    to_datetime: Optional[datetime] = None