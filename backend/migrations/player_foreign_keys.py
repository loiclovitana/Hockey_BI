from sqlalchemy import ForeignKeyConstraint, MetaData, Table, text
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable


def rebuild_player_foreign_keys(
    session: Session, table_name: str, constraint_name: str, *, composite: bool
) -> None:
    """Rebuild one SQLite table while preserving its data and schema objects."""
    if composite:
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
    elif session.scalar(text("PRAGMA foreign_keys")):
        raise ValueError(
            "Rolling back restores invalid single-column foreign keys; "
            "use a connection with PRAGMA foreign_keys = OFF"
        )

    # A savepoint makes SQLite DDL transactional if the rebuild fails.
    with session.begin_nested():
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
                    ForeignKeyConstraint(["season_id"], ["HOCKEY_PLAYERS.season_id"])
                )

        # Preserve custom indexes and triggers along with reflected columns,
        # defaults, primary keys and unrelated constraints.
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
        session.execute(text(f'ALTER TABLE "{table.name}" RENAME TO "{table_name}"'))
        for sql in schema_objects:
            session.execute(text(sql))
