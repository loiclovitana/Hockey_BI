import csv
from collections.abc import Callable

__DELIMITER = ";"
__ENCODING = "utf-8-sig"


def playerstats_csv_loader(csv_file_path: str) -> Callable[[], list[dict[str, str]]]:
    return lambda: load_csv(csv_file_path)


def load_csv(csv_file_path: str) -> list[dict[str, str]]:
    with open(csv_file_path, encoding=__ENCODING) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=__DELIMITER, quotechar='"')
        return list(reader)
