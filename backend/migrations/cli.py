#!/usr/bin/env python3
"""
Migration CLI tool for Hockey BI database.

Usage:
    python -m migrations.cli migrate      # Run all pending migrations
    python -m migrations.cli rollback     # Rollback last migration
    python -m migrations.cli rollback VERSION  # Rollback to specific version
    python -m migrations.cli status       # Show migration status
"""

import sys
import os
from typing import Optional

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from migrations.migration_runner import MigrationRunner


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    database_url = os.getenv("HM_DATABASE_URL", "")

    if not database_url:
        print("No database set", file=sys.stderr)
        sys.exit(-1)

    runner = MigrationRunner(database_url)

    if command == "migrate":
        runner.migrate()
    elif command == "rollback":
        target_version: Optional[str] = None
        if len(sys.argv) > 2:
            target_version = sys.argv[2]
        runner.rollback(target_version)
    elif command == "status":
        runner.status()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
