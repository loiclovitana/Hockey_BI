from sqlalchemy import text
from sqlalchemy.orm import Session

from hmtracker.database.base import Migration


class AddPlayerNewsTableMigration(Migration):
    """Add player news with optional player links and availability timing."""

    @property
    def version(self) -> str:
        return "2026_10_22_000"

    @property
    def description(self) -> str:
        return "Add Player News table"

    def up(self, session: Session) -> None:
        session.execute(
            text("""
            CREATE TABLE PLAYER_NEWS (
                id INTEGER PRIMARY KEY,
                season_id INTEGER NULL,
                player_id INTEGER NULL,
                source VARCHAR NOT NULL,
                news_date DATE NOT NULL,
                player_name VARCHAR NOT NULL,
                title VARCHAR NOT NULL,
                confirmed BOOLEAN NOT NULL DEFAULT FALSE,
                info_type VARCHAR(10) NOT NULL,
                current_team VARCHAR NULL,
                new_team VARCHAR NULL,
                availability_time VARCHAR NULL,
                CONSTRAINT player_news_info_type
                    CHECK (info_type IN ('Injury', 'Suspension', 'Absence', 'Transfert', 'Return')),
                CONSTRAINT player_news_new_team_transfer_only
                    CHECK (new_team IS NULL OR info_type = 'Transfert'),
                CONSTRAINT player_news_player
                    FOREIGN KEY (player_id, season_id)
                    REFERENCES HOCKEY_PLAYERS (id, season_id)
            )
        """)
        )
        session.execute(
            text('CREATE INDEX "ix_PLAYER_NEWS_source" ON "PLAYER_NEWS" (source)')
        )

    def down(self, session: Session) -> None:
        session.execute(text("DROP TABLE PLAYER_NEWS"))
