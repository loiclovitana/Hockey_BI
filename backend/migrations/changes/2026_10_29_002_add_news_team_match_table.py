from sqlalchemy import text
from sqlalchemy.orm import Session

from hmtracker.database.base import Migration


class AddNewsTeamMatchTableMigration(Migration):
    @property
    def version(self) -> str:
        return "2026_10_29_002"

    @property
    def description(self) -> str:
        return "Store reusable LLM team news matches"

    def up(self, session: Session) -> None:
        session.execute(
            text("""
            CREATE TABLE NEWS_TEAM_MATCH (
                team_name VARCHAR PRIMARY KEY NOT NULL,
                team_code VARCHAR NOT NULL
            )
        """)
        )

    def down(self, session: Session) -> None:
        session.execute(text("DROP TABLE NEWS_TEAM_MATCH"))
