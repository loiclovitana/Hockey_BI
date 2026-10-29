from sqlalchemy import ForeignKeyConstraint, MetaData, Table, text
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable

from hmtracker.database.base import Migration


class FixPlayerForeignKeysMigration(Migration):
    """Reference a hockey player using both their ID and season."""

    @property
    def version(self) -> str:
        return "2026_10_29_001"

    @property
    def description(self) -> str:
        return "Use composite player foreign keys in stats and teams"

    def up(self, session: Session) -> None:
        # Check both tables before changing either; never discard invalid rows.
        for table_name in ("HOCKEY_PLAYER_STATS", "TEAM"):
            invalid_count = session.scalar(
                text(f"""
                    SELECT COUNT(*) FROM {table_name} child
                    WHERE NOT EXISTS (
                        SELECT 1 FROM HOCKEY_PLAYERS player
                        WHERE player.id = child.player_id
                          AND player.season_id = child.season_id
                    )
                """)
            )
            if invalid_count:
                raise ValueError(
                    f"{table_name} has {invalid_count} rows with invalid "
                    "player/season pairs; repair them before migrating"
                )
        self._rebuild_tables(session, composite=True)

    def down(self, session: Session) -> None:
        # The old schema contains invalid single-column player references.
        if session.scalar(text("PRAGMA foreign_keys")):
            raise ValueError(
                "Rolling back restores invalid single-column foreign keys; "
                "use a connection with PRAGMA foreign_keys = OFF"
            )
        self._rebuild_tables(session, composite=False)

    def _rebuild_tables(self, session: Session, composite: bool) -> None:
        # A savepoint makes SQLite DDL transactional if either rebuild fails.
        with session.begin_nested():
            for table_name, constraint_name in (
                ("HOCKEY_PLAYER_STATS", "hockey_player_stats_player"),
                ("TEAM", "team_player"),
            ):
                connection = session.connection()
                table = Table(table_name, MetaData(), autoload_with=connection)
                for constraint in list(table.foreign_key_constraints):
                    if constraint.referred_table.name == "HOCKEY_PLAYERS":
                        table.constraints.remove(constraint)

                if composite:
                    table.append_constraint(
                        ForeignKeyConstraint(
                            ["player_id", "season_id"],
                            ["HOCKEY_PLAYERS.id", "HOCKEY_PLAYERS.season_id"],
                            name=constraint_name,
                        )
                    )
                else:
                    table.append_constraint(
                        ForeignKeyConstraint(["player_id"], ["HOCKEY_PLAYERS.id"])
                    )
                    if table_name == "TEAM":
                        table.append_constraint(
                            ForeignKeyConstraint(
                                ["season_id"], ["HOCKEY_PLAYERS.season_id"]
                            )
                        )

                # Preserve custom indexes and triggers along with reflected
                # columns, defaults, primary keys and unrelated constraints.
                schema_objects = session.scalars(
                    text("""
                        SELECT sql FROM sqlite_master
                        WHERE tbl_name = :table_name
                          AND type IN ('index', 'trigger') AND sql IS NOT NULL
                    """),
                    {"table_name": table_name},
                ).all()
                table.name = f"{table_name}_replacement"
                session.execute(CreateTable(table))
                columns = ", ".join(
                    connection.dialect.identifier_preparer.quote(column.name)
                    for column in table.columns
                )
                session.execute(
                    text(
                        f'INSERT INTO "{table.name}" ({columns}) '
                        f'SELECT {columns} FROM "{table_name}"'
                    )
                )
                session.execute(text(f'DROP TABLE "{table_name}"'))
                session.execute(
                    text(f'ALTER TABLE "{table.name}" RENAME TO "{table_name}"')
                )
                for sql in schema_objects:
                    session.execute(text(sql))
