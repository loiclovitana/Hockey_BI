from typing import Type

from sqlalchemy.orm import Session

from HMDatabase import models


def get_current_season(db: Session) -> models.Season | None:
    return db.query(models.Season).filter(models.Season.is_current).first()


def get_player(db: Session, player_id: int, season_id: int) -> models.HockeyPlayer | None:
    return db.query(models.HockeyPlayer).get((player_id, season_id))


def get_players(db: Session, player_ids: list, season_id: int) -> list[Type[models.HockeyPlayer]]:
    return db.query(models.HockeyPlayer)\
        .filter(models.HockeyPlayer.season_id == season_id
                , models.HockeyPlayer.id.in_(player_ids)
                )\
        .all()


def get_imported_stats_dates(db: Session):
    return db.query(models.StatImport).all()
