import os
import importlib.util
import inspect
from datetime import datetime
from typing import List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import ProgrammingError

from hmtracker.database.base import Migration


class MigrationRunner:
    """Handles running database migrations."""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._ensure_migration_table()

    def _ensure_migration_table(self) -> None:
        """Create the migration tracking table if it doesn't exist."""
        with self.engine.begin() as conn:
            try:
                conn.execute(
                    text("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version VARCHAR(14) PRIMARY KEY,
                        description TEXT NOT NULL,
                        applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                )
            except Exception as e:
                print(f"Error creating migration table: {e}")

    def _get_applied_migrations(self, session: Session) -> List[str]:
        """Get list of already applied migration versions."""
        try:
            result = session.execute(
                text("SELECT version FROM schema_migrations ORDER BY version")
            )
            return [row[0] for row in result.fetchall()]
        except ProgrammingError:
            return []

    def _load_migrations(self) -> List[Migration]:
        """Load all migration classes from the migrations directory."""
        migrations = []
        migrations_dir = os.path.dirname(__file__) + "/changes/"

        for filename in os.listdir(migrations_dir):
            if not filename.startswith("__") and filename.endswith(".py"):
                module_path = os.path.join(migrations_dir, filename)
                spec = importlib.util.spec_from_file_location(
                    f"migrations.{filename[:-3]}", module_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, Migration)
                            and obj is not Migration
                        ):
                            migrations.append(obj())

        return sorted(migrations, key=lambda m: m.version)

    def _record_migration(self, session: Session, migration: Migration) -> None:
        """Record that a migration has been applied."""
        session.execute(
            text("""
            INSERT INTO schema_migrations (version, description, applied_at)
            VALUES (:version, :description, :applied_at)
        """),
            {
                "version": migration.version,
                "description": migration.description,
                "applied_at": datetime.now(),
            },
        )

    def _remove_migration_record(self, session: Session, version: str) -> None:
        """Remove migration record when rolling back."""
        session.execute(
            text("DELETE FROM schema_migrations WHERE version = :version"),
            {"version": version},
        )

    def migrate(self) -> None:
        """Run all pending migrations."""
        migrations = self._load_migrations()

        with self.SessionLocal() as session:
            applied_versions = self._get_applied_migrations(session)
            pending_migrations = [
                m for m in migrations if m.version not in applied_versions
            ]

            if not pending_migrations:
                print("No pending migrations.")
                return

            print(f"Running {len(pending_migrations)} migration(s)...")

            for migration in pending_migrations:
                try:
                    print(f"Applying: {migration}")
                    migration.up(session)
                    self._record_migration(session, migration)
                    session.commit()
                    print(f"✓ Applied: {migration}")
                except Exception as e:
                    session.rollback()
                    print(f"✗ Failed to apply {migration}: {e}")
                    break

    def rollback(self, target_version: str | None = None) -> None:
        """Rollback migrations to a specific version or the previous one."""
        migrations = self._load_migrations()

        with self.SessionLocal() as session:
            applied_versions = self._get_applied_migrations(session)

            if not applied_versions:
                print("No migrations to rollback.")
                return

            if target_version:
                if target_version not in applied_versions:
                    print(f"Version {target_version} is not applied.")
                    return
                rollback_versions = [v for v in applied_versions if v > target_version]
            else:
                rollback_versions = [applied_versions[-1]]

            rollback_migrations = [
                m for m in reversed(migrations) if m.version in rollback_versions
            ]

            print(f"Rolling back {len(rollback_migrations)} migration(s)...")

            for migration in rollback_migrations:
                try:
                    print(f"Rolling back: {migration}")
                    migration.down(session)
                    self._remove_migration_record(session, migration.version)
                    session.commit()
                    print(f"✓ Rolled back: {migration}")
                except Exception as e:
                    session.rollback()
                    print(f"✗ Failed to rollback {migration}: {e}")
                    break

    def status(self) -> None:
        """Show migration status."""
        migrations = self._load_migrations()

        with self.SessionLocal() as session:
            applied_versions = self._get_applied_migrations(session)

            print("Migration Status:")
            print("-" * 50)

            for migration in migrations:
                status = (
                    "✓ Applied"
                    if migration.version in applied_versions
                    else "✗ Pending"
                )
                print(f"{status} {migration}")

            if not migrations:
                print("No migrations found.")
