from sqlalchemy import text
from sqlalchemy.orm import Session

from hmtracker.database.base import Migration


class AddTaskTableMigration(Migration):
    """Add Task table."""

    @property
    def version(self) -> str:
        return "2025_09_26_001"

    @property
    def description(self) -> str:
        return "Add Task table"

    def up(self, session: Session) -> None:
        session.execute(
            text("""
            CREATE TABLE TASK (
                id INTEGER PRIMARY KEY,
                name VARCHAR NOT NULL DEFAULT 'Unknown',
                start DATETIME NOT NULL,
                end_ DATETIME NOT NULL,
                error VARCHAR NULL,
                stacktrace VARCHAR NULL
            )
        """)
        )

    def down(self, session: Session) -> None:
        """Remove the Task table."""
        session.execute(
            text("""
            DROP TABLE TASK
        """)
        )
