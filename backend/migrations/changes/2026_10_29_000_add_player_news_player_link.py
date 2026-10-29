from sqlalchemy import text
from sqlalchemy.orm import Session

from hmtracker.database.base import Migration


class AddPlayerNewsPlayerLinkMigration(Migration):
    """Allow news to reference a player in a specific season."""

    @property
    def version(self) -> str:
        return "2026_10_29_000"

    @property
    def description(self) -> str:
        return "Add nullable season and player IDs to Player News"

    def up(self, session: Session) -> None:
        self._rebuild_table(session, include_player_link=True)

    def down(self, session: Session) -> None:
        self._rebuild_table(session, include_player_link=False)

    def _rebuild_table(self, session: Session, include_player_link: bool) -> None:
        # SQLite requires rebuilding the table to add a composite foreign key.
        player_columns = ""
        player_constraint = ""
        if include_player_link:
            player_columns = "season_id INTEGER NULL, player_id INTEGER NULL,"
            player_constraint = """,
                CONSTRAINT player_news_player
                    FOREIGN KEY (player_id, season_id)
                    REFERENCES HOCKEY_PLAYERS (id, season_id)
            """

        session.execute(
            text(f"""
            CREATE TABLE PLAYER_NEWS_replacement (
                id INTEGER PRIMARY KEY,
                {player_columns}
                source VARCHAR NOT NULL,
                news_date DATE NOT NULL,
                player_name VARCHAR NOT NULL,
                title VARCHAR NOT NULL,
                confirmed BOOLEAN NOT NULL DEFAULT FALSE,
                info_type VARCHAR(10) NOT NULL,
                current_team VARCHAR NULL,
                new_team VARCHAR NULL,
                availability_time VARCHAR NOT NULL,
                CONSTRAINT player_news_info_type
                    CHECK (info_type IN ('Injury', 'Suspension', 'Absence', 'Transfert', 'Return')),
                CONSTRAINT player_news_new_team_transfer_only
                    CHECK (new_team IS NULL OR info_type = 'Transfert')
                {player_constraint}
            )
            """)
        )
        columns = (
            "id, source, news_date, player_name, title, confirmed, info_type, "
            "current_team, new_team, availability_time"
        )
        session.execute(
            text(
                f"INSERT INTO PLAYER_NEWS_replacement ({columns}) "
                f"SELECT {columns} FROM PLAYER_NEWS"
            )
        )
        session.execute(text("DROP TABLE PLAYER_NEWS"))
        session.execute(
            text("ALTER TABLE PLAYER_NEWS_replacement RENAME TO PLAYER_NEWS")
        )
        session.execute(
            text('CREATE INDEX "ix_PLAYER_NEWS_source" ON "PLAYER_NEWS" (source)')
        )
