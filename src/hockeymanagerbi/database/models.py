import enum

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Date, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func

HMDatabaseObject = declarative_base()


class Season(HMDatabaseObject):
    __tablename__ = 'SEASONS'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    start = Column(Date, nullable=False)
    end = Column(Date, nullable=False)
    arcade = Column(Boolean, nullable=False, default=False)


class HockeyPlayer(HMDatabaseObject):
    __tablename__ = "HOCKEY_PLAYERS"

    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey('SEASONS.id'), primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    foreigner = Column(Boolean, nullable=False)

    season = relationship("Season")


class HockeyPlayerStats(HMDatabaseObject):
    __tablename__ = "HOCKEY_PLAYER_STATS"

    player_id = Column(Integer, ForeignKey('HOCKEY_PLAYERS.id'), primary_key=True, nullable=False)
    season_id = Column(Integer, ForeignKey('SEASONS.id'), primary_key=True, nullable=False)
    validity_date = Column(DateTime, primary_key=True, nullable=False)

    import_id = Column(Integer, ForeignKey('STATS_IMPORT.id'), nullable=True)
    price = Column(Float, nullable=False)
    club = Column(String, nullable=False)
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
    import_date = Column(DateTime, nullable=False, server_default=func.now())
    origin = Column(String, nullable=False, server_default='Unknown')
    comment = Column(String, server_default="", nullable=False)

    stats = relationship("HockeyPlayerStats", back_populates="importation")


class Manager(HMDatabaseObject):
    __tablename__ = "MANAGER"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)


class Team(HMDatabaseObject):
    __tablename__ = "TEAM"
    id = Column(Integer, primary_key=True)
    team = Column(String, unique=False, nullable=False)
    manager_id = Column(Integer, ForeignKey("MANAGER.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("HOCKEY_PLAYERS.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("HOCKEY_PLAYERS.season_id"), nullable=False)

    from_datetime = Column(DateTime, nullable=True)
    to_datetime = Column(DateTime, nullable=True)

    manager = relationship('Manager')
