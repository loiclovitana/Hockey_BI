from sqlalchemy.orm import Session

from hmtracker.database.base import Migration
from migrations.player_foreign_keys import rebuild_player_foreign_keys


class FixTeamPlayerForeignKeyMigration(Migration):
    @property
    def version(self) -> str:
        return "2026_10_29_001"

    @property
    def description(self) -> str:
        return "Use a composite player foreign key in Team"

    def up(self, session: Session) -> None:
        rebuild_player_foreign_keys(session, "TEAM", "team_player", composite=True)

    def down(self, session: Session) -> None:
        rebuild_player_foreign_keys(session, "TEAM", "team_player", composite=False)
