import logging
from pathlib import Path

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19"]
__tags__ = ["html"]

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Indiana.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Open the cache
    cache = Cache(cache_dir)

    # Get the HTML
    latest_url = "https://www.in.gov/dwd/2567.htm"
    r = utils.get_url(latest_url)
    latest_html = r.text
    cache.write("in/latest.html", latest_html)

    # Parse tables
    latest_tables = utils.parse_tables(latest_html)

    output_rows = latest_tables[0]

    # Get the archive tables
    archive_url = "https://www.in.gov/dwd/3125.htm"
    r = utils.get_url(archive_url)
    archive_html = r.text
    cache.write("in/archive.html", archive_html)

    table_list = utils.parse_table(archive_html, include_headers=False)

    output_rows += table_list[0]

    # Write out
    data_path = data_dir / "in.csv"
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the CSV
    return data_path


if __name__ == "__main__":
    scrape()
