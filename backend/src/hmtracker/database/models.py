from datetime import date, datetime
from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    DateTime,
    Float,
    Date,
    Boolean,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy.sql.functions import func


class HMDatabaseObject(DeclarativeBase):
    pass


def to_json(dbObject: HMDatabaseObject) -> dict:
    return {c.name: getattr(dbObject, c.name) for c in dbObject.__table__.columns}


class Season(HMDatabaseObject):
    __tablename__ = "SEASONS"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    start: Mapped[date] = mapped_column(Date, nullable=False)
    end: Mapped[date] = mapped_column(Date, nullable=False)
    arcade: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class HockeyPlayer(HMDatabaseObject):
    __tablename__ = "HOCKEY_PLAYERS"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("SEASONS.id"), primary_key=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    foreigner: Mapped[bool] = mapped_column(Boolean, nullable=False)

    season = relationship("Season")


class HockeyPlayerStats(HMDatabaseObject):
    __tablename__ = "HOCKEY_PLAYER_STATS"

    player_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("HOCKEY_PLAYERS.id"), primary_key=True, nullable=False
    )
    season_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("SEASONS.id"), primary_key=True, nullable=False
    )
    validity_date: Mapped[datetime] = mapped_column(
        DateTime, primary_key=True, nullable=False
    )

    import_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("STATS_IMPORT.id"), nullable=True
    )
    price: Mapped[float] = mapped_column(Float, nullable=False)
    club: Mapped[str] = mapped_column(String, nullable=False)
    ownership: Mapped[float | None] = mapped_column(Float)
    hm_points: Mapped[int | None] = mapped_column(Integer)
    appearances: Mapped[int | None] = mapped_column(Integer)
    goal: Mapped[int | None] = mapped_column(Integer)
    assists: Mapped[int | None] = mapped_column(Integer)
    penalties: Mapped[int | None] = mapped_column(Integer)
    plus_minus: Mapped[int | None] = mapped_column(Integer)

    player = relationship("HockeyPlayer")
    importation = relationship("StatImport", back_populates="stats")


class StatImport(HMDatabaseObject):
    __tablename__ = "STATS_IMPORT"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    import_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    origin: Mapped[str] = mapped_column(
        String, nullable=False, server_default="Unknown"
    )
    comment: Mapped[str] = mapped_column(String, server_default="", nullable=False)

    stats = relationship("HockeyPlayerStats", back_populates="importation")


class Manager(HMDatabaseObject):
    __tablename__ = "MANAGER"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str | None] = mapped_column(String, unique=True)


class Team(HMDatabaseObject):
    __tablename__ = "TEAM"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team: Mapped[str] = mapped_column(String, unique=False, nullable=False)
    manager_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("MANAGER.id"), nullable=False
    )
    player_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("HOCKEY_PLAYERS.id"), nullable=False
    )
    season_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("HOCKEY_PLAYERS.season_id"), nullable=False
    )

    from_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    to_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    manager = relationship("Manager")
