import logging

from hmtracker.database import models
from hmtracker.database.repository import RepositorySession


def import_matches(
    repository_session: RepositorySession,
    matches: list[models.Match],
):
    """
    Import or update matches into the repository.
    Matches with existing IDs will be updated, new matches will be inserted.

    :param repository_session: Database session
    :param matches: List of Match objects to import
    :return:
    """
    repository_session.session.begin_nested()

    # Get all match IDs from the input
    match_ids = [match.id for match in matches]

    # Fetch existing matches from database
    existing_matches = (
        repository_session.session.query(models.Match)
        .filter(models.Match.id.in_(match_ids))
        .all()
    )

    # Create a dict for quick lookup
    existing_matches_dict = {match.id: match for match in existing_matches}

    new_matches = []
    updated_count = 0

    for match in matches:
        if match.id in existing_matches_dict:
            # Update existing match
            existing_match = existing_matches_dict[match.id]
            existing_match.home_club = match.home_club
            existing_match.away_club = match.away_club
            existing_match.match_datetime = match.match_datetime
            updated_count += 1
        else:
            # Add new match
            new_matches.append(match)

    repository_session.session.add_all(new_matches)
    repository_session.session.commit()

    logging.info(
        f"Imported {len(new_matches)} new matches, updated {updated_count} existing matches"
    )

    return len(new_matches), updated_count
