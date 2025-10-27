import csv
from datetime import datetime
from io import StringIO

from hmtracker.database.models import Match

# Mapping of club names to codes
CLUB_MAPPING = {
    "HC Ajoie": "AJO",
    "HC Ambri-Piotta": "AMB",
    "SC Bern": "BER",
    "EHC Biel-Bienne": "BIE",
    "HC Davos": "DAV",
    "Fribourg-Gottéron": "FRI",
    "Genève-Servette HC": "GEN",
    "EHC Kloten": "KLO",
    "SCL Tigers": "LAN",  # Langnau
    "Lausanne HC": "LAU",
    "HC Lugano": "LUG",
    "SC Rapperswil-Jona Lakers": "RAP",
    "ZSC Lions": "ZSC",
    "EV Zug": "ZUG",
}


def parse_match_csv(csv_content: str) -> list[Match]:
    """
    Parse CSV content and return a list of Match objects.

    :param csv_content: String with CSV content
    :return: List of Match objects
    """
    # Parse CSV
    csv_file = StringIO(csv_content)
    reader = csv.reader(csv_file, delimiter=";")

    # Skip header
    next(reader)

    matches = []
    for row in reader:
        try:
            match = _row_to_match(row)
            matches.append(match)
        except (ValueError, KeyError, IndexError) as e:
            # Log error but continue processing other rows
            import logging

            logging.warning(f"Failed to parse row {row}: {e}")
            continue

    return matches


def _row_to_match(row: list[str]) -> Match:
    """
    Convert a CSV row to a Match object.
    Expected format: [..., Date (col 1), Time (col 2), Home (col 3), Away (col 4), ..., ID (col 13)]

    :param row: CSV row as list of strings
    :return: Match object
    """
    match_datetime = datetime.strptime(row[1] + " " + row[2], "%d.%m.%Y %H:%M")
    home_club = CLUB_MAPPING[row[3]]
    away_club = CLUB_MAPPING[row[4]]
    match_id = int(row[13])

    return Match(
        id=match_id,
        match_datetime=match_datetime,
        home_club=home_club,
        away_club=away_club,
    )
