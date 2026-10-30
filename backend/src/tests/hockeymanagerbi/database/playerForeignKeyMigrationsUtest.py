import unittest

from sqlalchemy import ForeignKeyConstraint, MetaData, create_engine, inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from hmtracker.database.models import (
    HockeyPlayer,
    HockeyPlayerStats,
    Manager,
    Season,
    StatImport,
    Team,
)
from migrations.migration_runner import MigrationRunner


class TestPlayerForeignKeyMigrations(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        self.addCleanup(self.engine.dispose)
        metadata = MetaData()
        for model in (
            Season,
            HockeyPlayer,
            StatImport,
            Manager,
            HockeyPlayerStats,
            Team,
        ):
            model.__table__.to_metadata(metadata)
        for table_name in ("HOCKEY_PLAYER_STATS", "TEAM"):
            table = metadata.tables[table_name]
            for constraint in list(table.foreign_key_constraints):
                if constraint.referred_table.name == "HOCKEY_PLAYERS":
                    table.constraints.remove(constraint)
            table.append_constraint(
                ForeignKeyConstraint(["player_id"], ["HOCKEY_PLAYERS.id"])
            )
            if table_name == "TEAM":
                table.append_constraint(
                    ForeignKeyConstraint(["season_id"], ["HOCKEY_PLAYERS.season_id"])
                )
        metadata.create_all(self.engine)
        with self.engine.begin() as connection:
            for sql in (
                "INSERT INTO SEASONS VALUES (1, 'Current', '2026-01-01', '2026-12-31', 0)",
                "INSERT INTO HOCKEY_PLAYERS VALUES (1, 1, 'Player', 'FW', 0)",
                "INSERT INTO MANAGER (id) VALUES (1)",
                "INSERT INTO HOCKEY_PLAYER_STATS "
                "(player_id, season_id, validity_date, price, club) "
                "VALUES (1, 1, '2026-10-30', 10, 'ZSC')",
                "INSERT INTO TEAM (id, team, manager_id, player_id, season_id) "
                "VALUES (1, 'My team', 1, 1, 1)",
            ):
                connection.execute(text(sql))
            for table_name in ("HOCKEY_PLAYER_STATS", "TEAM"):
                connection.execute(
                    text(
                        f'CREATE INDEX "ix_{table_name}_player" ON {table_name} (player_id)'
                    )
                )
                connection.execute(
                    text(f"""
                        CREATE TRIGGER "{table_name}_positive_player"
                        BEFORE INSERT ON {table_name} WHEN NEW.player_id < 0
                        BEGIN SELECT RAISE(ABORT, 'invalid player'); END
                    """)
                )
        self.session = Session(self.engine)
        self.addCleanup(self.session.close)
        runner = MigrationRunner("sqlite://")
        self.addCleanup(runner.engine.dispose)
        migrations = {
            migration.version: migration for migration in runner._load_migrations()
        }
        self.migrations = {
            "HOCKEY_PLAYER_STATS": migrations["2026_10_29_000"],
            "TEAM": migrations["2026_10_29_001"],
        }

    def schema_objects(self, table_name):
        return self.session.execute(
            text("SELECT type, name, sql FROM sqlite_master WHERE tbl_name = :table"),
            {"table": table_name},
        ).all()

    def test_up_preserves_rows_schema_objects_and_unrelated_tables(self):
        self.session.execute(text("PRAGMA foreign_keys = ON"))
        for table_name, migration in self.migrations.items():
            with self.subTest(table=table_name):
                rows = self.session.execute(text(f"SELECT * FROM {table_name}")).all()
                objects = [
                    obj for obj in self.schema_objects(table_name) if obj[0] != "table"
                ]
                other_table = (
                    "TEAM"
                    if table_name == "HOCKEY_PLAYER_STATS"
                    else "HOCKEY_PLAYER_STATS"
                )
                other_schema = self.schema_objects(other_table)
                migration.up(self.session)
                self.session.commit()
                self.assertEqual(
                    self.session.execute(text(f"SELECT * FROM {table_name}")).all(),
                    rows,
                )
                self.assertEqual(
                    [
                        obj
                        for obj in self.schema_objects(table_name)
                        if obj[0] != "table"
                    ],
                    objects,
                )
                self.assertEqual(self.schema_objects(other_table), other_schema)
                foreign_keys = inspect(self.engine).get_foreign_keys(table_name)
                player_keys = [
                    fk
                    for fk in foreign_keys
                    if fk["referred_table"] == "HOCKEY_PLAYERS"
                ]
                self.assertEqual(len(player_keys), 1)
                self.assertEqual(
                    player_keys[0]["constrained_columns"], ["player_id", "season_id"]
                )
                self.assertEqual(
                    player_keys[0]["referred_columns"], ["id", "season_id"]
                )
                self.assertEqual(
                    self.session.execute(
                        text(f"PRAGMA foreign_key_check({table_name})")
                    ).all(),
                    [],
                )
                with self.assertRaises(IntegrityError):
                    self.session.execute(text(f"UPDATE {table_name} SET season_id = 2"))
                self.session.rollback()

    def test_up_rejects_invalid_pairs_without_changing_data_or_schema(self):
        for table_name, migration in self.migrations.items():
            with self.subTest(table=table_name):
                self.session.execute(text(f"UPDATE {table_name} SET season_id = 2"))
                self.session.commit()
                objects = self.schema_objects(table_name)
                with self.assertRaisesRegex(ValueError, f"{table_name} has 1 rows"):
                    migration.up(self.session)
                self.assertEqual(self.schema_objects(table_name), objects)
                self.assertEqual(
                    self.session.scalar(text(f"SELECT season_id FROM {table_name}")), 2
                )

    def test_down_restores_only_its_original_table_schema(self):
        for table_name, migration in self.migrations.items():
            with self.subTest(table=table_name):
                original_keys = inspect(self.engine).get_foreign_keys(table_name)
                original_objects = [
                    obj for obj in self.schema_objects(table_name) if obj[0] != "table"
                ]
                rows = self.session.execute(text(f"SELECT * FROM {table_name}")).all()
                other_table = (
                    "TEAM"
                    if table_name == "HOCKEY_PLAYER_STATS"
                    else "HOCKEY_PLAYER_STATS"
                )
                other_schema = self.schema_objects(other_table)
                migration.up(self.session)
                migration.down(self.session)
                self.session.commit()
                self.assertCountEqual(
                    inspect(self.engine).get_foreign_keys(table_name), original_keys
                )
                self.assertEqual(
                    [
                        obj
                        for obj in self.schema_objects(table_name)
                        if obj[0] != "table"
                    ],
                    original_objects,
                )
                self.assertEqual(self.schema_objects(other_table), other_schema)
                self.assertEqual(
                    self.session.execute(text(f"SELECT * FROM {table_name}")).all(),
                    rows,
                )

    def test_down_requires_foreign_keys_disabled(self):
        self.session.execute(text("PRAGMA foreign_keys = ON"))
        for table_name, migration in self.migrations.items():
            with self.subTest(table=table_name):
                migration.up(self.session)
                self.session.commit()
                objects = self.schema_objects(table_name)
                with self.assertRaisesRegex(ValueError, "PRAGMA foreign_keys = OFF"):
                    migration.down(self.session)
                self.assertEqual(self.schema_objects(table_name), objects)
