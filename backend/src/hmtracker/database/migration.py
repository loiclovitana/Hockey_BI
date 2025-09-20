from abc import ABC, abstractmethod
from sqlalchemy.orm import Session


class Migration(ABC):
    """Base class for all database migrations."""

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the migration version (timestamp format: YYYYMMDDHHMMSS)."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what this migration does."""
        pass

    @abstractmethod
    def up(self, session: Session) -> None:
        """Apply the migration."""
        pass

    @abstractmethod
    def down(self, session: Session) -> None:
        """Rollback the migration."""
        pass

    def __str__(self) -> str:
        return f"{self.version} - {self.description}"