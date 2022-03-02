import logging
import re
from pathlib import Path

from .. import utils

__authors__ = ["zstumgoren", "Dilcia19"]
__tags__ = [
    "html",
]

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Alabama.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    output_csv = data_dir / "al.csv"
    page = utils.get_url("https://www.madeinalabama.com/warn-list/")
    # can't see 2020 listings when I open web page, but they are on the summary in the google search

    # Scrape out any tables
    table_list = utils.parse_tables(page.text)

    # Get rows from the first table
    new_rows = table_list[0]

    # Discard bogus data lines (see last lines of source data)
    # based on check of first field ("Closing or Layoff")
    output_rows = list(
        filter(lambda row: re.match(r"(clos|lay)", row[0], re.I), new_rows)
    )

    if len(output_rows) != len(new_rows):
        logger.warning(
            f"Warning: Discarded {len(new_rows) - len(output_rows)} dirty data row(s)"
        )

    utils.write_rows_to_csv(output_csv, output_rows)
    return output_csv


if __name__ == "__main__":
    scrape()
