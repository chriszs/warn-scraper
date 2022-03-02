import logging
import re
from datetime import datetime
from pathlib import Path

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "ydoc5212"]
__tags__ = ["html"]

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Wisconsin.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Set the cache
    cache = Cache(cache_dir)

    # Get the current year
    today = datetime.today()
    current_year = today.year

    # Set the date range we're going to scrape
    year_range = list(range(2016, current_year + 1))
    year_range.reverse()

    # Loop through the years and download the pages
    html_list = []
    for year in year_range:
        # Since the 2022 page doesn't exist yet, we're going to hack in a skip
        if year == 2022:
            continue

        # Request fresh pages, use cache for old ones
        cache_key = f"wi/{year}.html"
        if cache.exists(cache_key) and year < current_year - 1:
            html = cache.read(cache_key)
        else:
            url = f"https://dwd.wisconsin.gov/dislocatedworker/warn/{year}/default.htm"
            r = utils.get_url(url)
            html = r.text
            cache.write(cache_key, html)

        # Add to the list
        html_list.append(html)

    output_rows = []
    for i, html in enumerate(html_list):
        # Parse the HTML
        table_list = utils.parse_tables(html, include_headers=i == 0)

        # Remove the "Updates to Previously Filed Notices" tables
        # We can single them out because they only have two columns
        notice_tables = [t for t in table_list if len(t.find("tr").find_all("th")) > 2]

    # Set the export path
    data_path = data_dir / "wi.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the file
    return data_path


def _clean_text(text):
    """Clean up the provided cell."""
    # remove trailing characters after LayoffBeginDate
    if re.match(r"^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", text):
        text = re.sub(r"(?<=[0-9]{4}).*", "", text)
    return text.strip()


if __name__ == "__main__":
    scrape()
