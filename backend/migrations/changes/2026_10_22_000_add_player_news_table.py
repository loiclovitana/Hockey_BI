from sqlalchemy import text
from sqlalchemy.orm import Session

from hmtracker.database.base import Migration


class AddPlayerNewsTableMigration(Migration):
    """Add processed articles and player news with optional roster links."""

    @property
    def version(self) -> str:
        return "2026_10_22_000"

    @property
    def description(self) -> str:
        return "Add News Article and Player News tables"

    def up(self, session: Session) -> None:
        session.execute(
            text("""
            CREATE TABLE NEWS_ARTICLE (
                id INTEGER PRIMARY KEY,
                base_url VARCHAR NOT NULL,
                article_url VARCHAR NOT NULL,
                article_date DATE NOT NULL,
                title VARCHAR NOT NULL,
                processed_by VARCHAR NULL,
                processed_date DATETIME NULL,
                UNIQUE (base_url, article_url)
            )
        """)
        )
        session.execute(
            text("""
            CREATE TABLE PLAYER_NEWS (
                id INTEGER PRIMARY KEY,
                season_id INTEGER NULL,
                player_id INTEGER NULL,
                article_id INTEGER NOT NULL REFERENCES NEWS_ARTICLE (id),
                player_name VARCHAR NOT NULL,
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
            text(
                'CREATE INDEX "ix_PLAYER_NEWS_article_id" ON "PLAYER_NEWS" (article_id)'
            )
        )

    def down(self, session: Session) -> None:
        session.execute(text("DROP TABLE PLAYER_NEWS"))
        session.execute(text("DROP TABLE NEWS_ARTICLE"))
