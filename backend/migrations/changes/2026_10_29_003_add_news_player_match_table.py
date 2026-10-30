from sqlalchemy import text
from sqlalchemy.orm import Session

from hmtracker.database.base import Migration


class AddNewsPlayerMatchTableMigration(Migration):
    @property
    def version(self) -> str:
        return "2026_10_29_003"

    @property
    def description(self) -> str:
        return "Store reusable LLM player news matches"

    def up(self, session: Session) -> None:
        session.execute(
            text("""
            CREATE TABLE NEWS_PLAYER_MATCH (
                player_name VARCHAR NOT NULL,
                team_code VARCHAR NOT NULL,
                season_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                PRIMARY KEY (player_name, team_code, season_id),
                CONSTRAINT news_player_match_player
                    FOREIGN KEY (player_id, season_id)
                    REFERENCES HOCKEY_PLAYERS (id, season_id)
            )
        """)
        )

    def down(self, session: Session) -> None:
        session.execute(text("DROP TABLE NEWS_PLAYER_MATCH"))
