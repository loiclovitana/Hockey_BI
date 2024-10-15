from typing import Type

from sqlalchemy.orm import Session

from HMDatabase import models, database


def create_repository_session_maker(database_url: str):
    session_maker = database.init_session_maker(database_url)
    return lambda: RepositorySession(session_maker())


class RepositorySession:
    session: Session = None

    def __init__(self, session: Session):
        self.session = session

    def __str__(self):
        return f"""RepositorySession(session = {self.session})"""

    def __del__(self):
        self.end_session()

    def end_session(self):
        self.session.commit()
        self.session.close()

    def get_current_season(self) -> models.Season | None:
        return self.session.query(models.Season).filter(models.Season.is_current).first()

    def get_player(self, player_id: int, season_id: int) -> models.HockeyPlayer | None:
        return self.session.query(models.HockeyPlayer).get((player_id, season_id))

    def get_players(self, player_ids: list, season_id: int) -> list[Type[models.HockeyPlayer]]:
        return self.session.query(models.HockeyPlayer) \
            .filter(models.HockeyPlayer.season_id == season_id
                    , models.HockeyPlayer.id.in_(player_ids)
                    ) \
            .all()

    def get_imported_stats_dates(self):
        return self.session.query(models.StatImport).all()