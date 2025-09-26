from sqlalchemy import text
from sqlalchemy.orm import Session

from hmtracker.database.base import Migration


class AddAutolineupMigration(Migration):
    """Add autolineup column to MANAGER table."""

    @property
    def version(self) -> str:
        return "2025_09_26_000"

    @property
    def description(self) -> str:
        return "Add autolineup column to MANAGER table"

    def up(self, session: Session) -> None:
        session.execute(text("""
            ALTER TABLE MANAGER
            ADD COLUMN autolineup BIT NULL
        """))

    def down(self, session: Session) -> None:
        """Remove the encrypted_password column."""
        session.execute(text("""
            ALTER TABLE MANAGER
            DROP COLUMN autolineup
        """))