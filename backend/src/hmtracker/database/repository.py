import datetime

from sqlalchemy import Column
from sqlalchemy.orm import Session

from hmtracker.database import models, database


def create_repository_session_maker(database_url: str):
    session_maker = database.init_session_maker(database_url)
    return lambda: RepositorySession(session_maker())


class RepositorySession:
    def __init__(self, session: Session):
        self.session: Session = session

    def __str__(self):
        return f"""RepositorySession(session = {self.session})"""

    def __del__(self):
        self.end_session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_session()

    def end_session(self):
        self.session.commit()
        self.session.close()

    def get_current_season(self, arcade: bool = False) -> models.Season | None:
        return self.find_season(datetime.datetime.now(), arcade)

    def get_season(self, season_id: int) -> models.Season | None:
        if season_id is None:
            return self.get_current_season()
        return self.session.query(models.Season).get(season_id)

    def get_player(self, player_id: int, season_id: int) -> models.HockeyPlayer | None:
        return self.session.get(models.HockeyPlayer, (player_id, season_id))

    def get_players(
        self, player_ids: list | None = None, season_id: int | Column[int] | None = None
    ) -> list[models.HockeyPlayer]:
        if season_id is None:
            current_season = self.get_current_season()
            if current_season is None:
                return []
            season_id = current_season.id

        if player_ids is None:
            return (
                self.session.query(models.HockeyPlayer)
                .filter(models.HockeyPlayer.season_id == season_id)
                .all()
            )

        return (
            self.session.query(models.HockeyPlayer)
            .filter(
                models.HockeyPlayer.season_id == season_id,
                models.HockeyPlayer.id.in_(player_ids),
            )
            .all()
        )

    def get_imported_stats_dates(self):
        return self.session.query(models.StatImport).all()

    def find_season(
        self, validity_date: datetime.datetime, arcade: bool = False
    ) -> models.Season:
        return (
            self.session.query(models.Season)
            .filter(
                models.Season.start <= validity_date,
                models.Season.end >= validity_date,
                models.Season.arcade == arcade,
            )
            .one()
        )

    def get_team(
        self, manager: int | models.Manager, season: int | models.Season, team_code: str
    ) -> list[models.Team]:
        manager_id = manager if isinstance(manager, int) else manager.id
        season_id = season if isinstance(season, int) else season.id
        return (
            self.session.query(models.Team)
            .filter(
                models.Team.manager_id == manager_id,
                models.Team.season_id == season_id,
                models.Team.team == team_code,
            )
            .all()
        )

    def get_teams(
        self, manager: int | models.Manager, season: int | models.Season | None = None
    ) -> list[models.Team]:
        manager_id = manager if isinstance(manager, int) else manager.id
        if season is None:
            return ( self.session.query(models.Team)
                .filter(
                    models.Team.manager_id == manager_id,
                )
                .all()
            )
        season_id = season if isinstance(season, int) else season.id
        return (
            self.session.query(models.Team)
            .filter(
                models.Team.manager_id == manager_id,
                models.Team.season_id == season_id,
            )
            .all()
        )

    def get_manager_by_email(self, email: str):
        return (
            self.session.query(models.Manager)
            .filter(models.Manager.email == email)
            .one_or_none()
        )

    def get_player_stats(self, player_ids: list[int], season_id: int | None = None):
        season = (
            self.get_current_season()
            if season_id is None
            else self.get_season(season_id)
        )
        if season is None:
            return None

        return (
            self.session.query(models.HockeyPlayerStats)
            .filter(
                models.HockeyPlayerStats.validity_date.between(
                    season.start, season.end
                ),
                models.HockeyPlayerStats.player_id.in_(player_ids),
            )
            .all()
        )
