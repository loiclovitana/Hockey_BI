from sqlalchemy import text
from sqlalchemy.orm import Session

from hmtracker.database.base import Migration


class AddMatchesTableMigration(Migration):
    """Add Matches table."""

    @property
    def version(self) -> str:
        return "2025_10_11_000"

    @property
    def description(self) -> str:
        return "Add Matches table"

    def up(self, session: Session) -> None:
        session.execute(
            text("""
            CREATE TABLE MATCHES (
                id INTEGER PRIMARY KEY,
                home_club VARCHAR NOT NULL,
                away_club VARCHAR NOT NULL,
                match_datetime DATETIME NOT NULL
            )
        """)
        )

    def down(self, session: Session) -> None:
        """Remove the Matches table."""
        session.execute(
            text("""
            DROP TABLE MATCHES
        """)
        )
