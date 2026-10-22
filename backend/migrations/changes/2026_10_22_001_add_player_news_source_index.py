from sqlalchemy import text
from sqlalchemy.orm import Session

from hmtracker.database.base import Migration


class AddPlayerNewsSourceIndexMigration(Migration):
    """Index article URLs for small-batch existence lookups."""

    @property
    def version(self) -> str:
        return "2026_10_22_001"

    @property
    def description(self) -> str:
        return "Add Player News source index"

    def up(self, session: Session) -> None:
        session.execute(
            text('CREATE INDEX "ix_PLAYER_NEWS_source" ON "PLAYER_NEWS" (source)')
        )

    def down(self, session: Session) -> None:
        session.execute(text('DROP INDEX "ix_PLAYER_NEWS_source"'))
