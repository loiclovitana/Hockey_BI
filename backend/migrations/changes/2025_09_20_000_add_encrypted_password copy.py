from sqlalchemy import text
from sqlalchemy.orm import Session

from hmtracker.database.base import Migration


class AddEncryptedPasswordMigration(Migration):
    """Add encrypted_password column to MANAGER table."""

    @property
    def version(self) -> str:
        return "2025_09_20_000"

    @property
    def description(self) -> str:
        return "Add encrypted_password column to MANAGER table"

    def up(self, session: Session) -> None:
        """Add the encrypted_password column."""
        session.execute(text("""
            ALTER TABLE MANAGER
            ADD COLUMN encrypted_password VARCHAR(255) NULL
        """))

    def down(self, session: Session) -> None:
        """Remove the encrypted_password column."""
        session.execute(text("""
            ALTER TABLE MANAGER
            DROP COLUMN encrypted_password
        """))