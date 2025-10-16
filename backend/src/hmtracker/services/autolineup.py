import logging
import traceback
from datetime import datetime

from hmtracker.parser.hmparser import HMAjaxScrapper
from hmtracker.database import repository, models
from hmtracker.services import encryption


def autolineup(user_email: str, password: str):
    parser = HMAjaxScrapper()
    try:
        parser.connect_to_hm(user_email, password)

        teams = parser.get_teams()

        for team in teams:
            team_id = team["id"]
            parser.select_team(team_id)
            parser.auto_lineup()

    finally:
        parser.close_session()


def _process_manager(manager: models.Manager) -> bool:
    """Process autolineup for a single manager. Returns True if successful."""
    if not manager.email or not manager.encrypted_password:
        logging.warning(f"Skipping manager {manager.id}: missing email or password")
        return False

    try:
        decrypted_password = encryption.decrypt(manager.encrypted_password)
        autolineup(manager.email, decrypted_password)
        manager.last_autolineup = datetime.now()
        return True
    except Exception as e:
        logging.error(
            f"Failed to align teams for manager {manager.email}: {str(e)}\n{traceback.format_exc()}"
        )
        return False


def _process_manager_batch(
    database_url: str,
    batch_size: int,
    offset: int,
    last_autolineup_before: datetime | None = None,
) -> tuple[int, int, bool]:
    """
    Process a batch of managers with autolineup enabled.
    Returns (success_count, fail_count, has_more_batches).
    """
    connection = repository.create_repository_session_maker(database_url)()
    try:
        managers = connection.get_managers_with_autolineup(
            limit=batch_size,
            offset=offset,
            last_autolineup_before=last_autolineup_before,
        )

        if not managers:
            return (0, 0, False)

        success_count = 0
        fail_count = 0

        for manager in managers:
            if _process_manager(manager):
                success_count += 1
            else:
                fail_count += 1

        return (success_count, fail_count, True)
    finally:
        connection.end_session()


def process_all_managers_autolineup(
    database_url: str, last_autolineup_before: datetime | None = None
) -> tuple[int, int]:
    """
    Process autolineup for all managers with autolineup enabled.

    Args:
        database_url: Database connection URL
        last_autolineup_before: Optional datetime to filter managers that haven't been
                                autolined up since this time (or never)

    Returns (total_success_count, total_fail_count).
    """
    total_success = 0
    total_fail = 0
    batch_size = 50
    offset = 0

    while True:
        success, fail, has_more = _process_manager_batch(
            database_url, batch_size, offset, last_autolineup_before
        )
        total_success += success
        total_fail += fail

        if not has_more:
            break

        offset += batch_size

    logging.info(
        f"Team alignment completed: {total_success} successful, {total_fail} failed"
    )

    return (total_success, total_fail)
