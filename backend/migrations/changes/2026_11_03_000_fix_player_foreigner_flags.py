from sqlalchemy import text
from sqlalchemy.orm import Session

from hmtracker.database.base import Migration


class FixPlayerForeignerFlagsMigration(Migration):
    """Correct existing records imported by the scraper before its flag fix."""

    @property
    def version(self) -> str:
        return "2026_11_03_000"

    @property
    def description(self) -> str:
        return "Correct inverted player foreigner flags"

    def up(self, session: Session) -> None:
        # Keep original values so rollback cannot invert players imported later.
        session.execute(
            text("""
                CREATE TABLE PLAYER_FOREIGNER_BACKUP_20261103 (
                    id INTEGER NOT NULL,
                    season_id INTEGER NOT NULL,
                    foreigner BOOLEAN NOT NULL,
                    PRIMARY KEY (id, season_id)
                )
            """)
        )
        session.execute(
            text("""
                INSERT INTO PLAYER_FOREIGNER_BACKUP_20261103 (id, season_id, foreigner)
                SELECT id, season_id, foreigner FROM HOCKEY_PLAYERS
            """)
        )
        session.execute(text("UPDATE HOCKEY_PLAYERS SET foreigner = NOT foreigner"))

    def down(self, session: Session) -> None:
        session.execute(
            text("""
                UPDATE HOCKEY_PLAYERS
                SET foreigner = (
                    SELECT original.foreigner
                    FROM PLAYER_FOREIGNER_BACKUP_20261103 AS original
                    WHERE original.id = HOCKEY_PLAYERS.id
                      AND original.season_id = HOCKEY_PLAYERS.season_id
                )
                WHERE EXISTS (
                    SELECT 1 FROM PLAYER_FOREIGNER_BACKUP_20261103 AS original
                    WHERE original.id = HOCKEY_PLAYERS.id
                      AND original.season_id = HOCKEY_PLAYERS.season_id
                )
            """)
        )
        session.execute(text("DROP TABLE PLAYER_FOREIGNER_BACKUP_20261103"))
