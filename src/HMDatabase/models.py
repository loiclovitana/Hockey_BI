import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.functions import func

from HMDatabase.database import HMDatabaseObject


class Season(HMDatabaseObject):
    __tablename__ = 'SEASONS'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_current = Column(Boolean)
    start = Column(Date, nullable=False)
    end = Column(Date, nullable=False)


class HockeyPlayer(HMDatabaseObject):
    __tablename__ = "HOCKEY_PLAYERS"

    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey('SEASONS.id'), primary_key=True, nullable=False)
    name = Column(String)
    club = Column(String)
    role = Column(String)

    season = relationship("Season")


class HockeyPlayerStats(HMDatabaseObject):
    __tablename__ = "HOCKEY_PLAYER_STATS"

    player_id = Column(Integer, ForeignKey('HOCKEY_PLAYERS.id'), primary_key=True, nullable=False)
    import_id = Column(Integer, ForeignKey('STATS_IMPORT.id'), primary_key=True, nullable=False)
    validity_date = Column(DateTime, nullable=False)

    price = Column(Float, nullable=False)
    ownership = Column(Float)
    hm_points = Column(Integer)
    appearances = Column(Integer)
    goal = Column(Integer)
    assists = Column(Integer)
    penalties = Column(Integer)
    plus_minus = Column(Integer)

    player = relationship("HockeyPlayer")
    importation = relationship("StatImport", back_populates="stats")


class StatImport(HMDatabaseObject):
    __tablename__ = "STATS_IMPORT"
    id = Column(Integer, primary_key=True)
    validity_date = Column(DateTime, nullable=False)
    import_date = Column(DateTime, nullable=False, server_default=func.now())
    origin = Column(String, nullable=False, server_default='Unknown')
    comment = Column(String, server_default="", nullable=False)

    stats = relationship("HockeyPlayerStats", back_populates="importation")
