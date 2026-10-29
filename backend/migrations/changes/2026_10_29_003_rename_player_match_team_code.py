from sqlalchemy import text
from sqlalchemy.orm import Session

from hmtracker.database.base import Migration


class RenamePlayerMatchTeamCodeMigration(Migration):
    @property
    def version(self) -> str:
        return "2026_10_29_003"

    @property
    def description(self) -> str:
        return "Name the player news match team key team_code"

    def up(self, session: Session) -> None:
        session.execute(
            text("ALTER TABLE NEWS_PLAYER_MATCH RENAME COLUMN team_name TO team_code")
        )

    def down(self, session: Session) -> None:
        session.execute(
            text("ALTER TABLE NEWS_PLAYER_MATCH RENAME COLUMN team_code TO team_name")
        )
