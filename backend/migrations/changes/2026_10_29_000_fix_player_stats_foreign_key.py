from sqlalchemy.orm import Session

from hmtracker.database.base import Migration
from migrations.player_foreign_keys import rebuild_player_foreign_keys


class FixPlayerStatsForeignKeyMigration(Migration):
    @property
    def version(self) -> str:
        return "2026_10_29_000"

    @property
    def description(self) -> str:
        return "Use a composite player foreign key in Hockey Player Stats"

    def up(self, session: Session) -> None:
        rebuild_player_foreign_keys(
            session, "HOCKEY_PLAYER_STATS", "hockey_player_stats_player", composite=True
        )

    def down(self, session: Session) -> None:
        rebuild_player_foreign_keys(
            session,
            "HOCKEY_PLAYER_STATS",
            "hockey_player_stats_player",
            composite=False,
        )
