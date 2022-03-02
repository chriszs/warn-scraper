import logging
import re
from datetime import datetime
from pathlib import Path

from .. import utils
from ..cache import Cache

__authors__ = ["zstumgoren", "Dilcia19", "shallotly"]
__tags__ = ["html"]

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Missouri.

    NOTES for data cleaning:
    - 2019 and 2020 page has duplicate data
    - 2017 date format is different

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Set the cache
    cache = Cache(cache_dir)

    # Get the range of years we're after
    today = datetime.today()
    current_year = today.year
    year_range = list(range(2015, current_year + 1))
    year_range.reverse()

    # Download them all
    html_list = []
    for year in year_range:

        # Set the URL, with a hack for 2020 and 2022
        if year == 2020:
            url = "https://jobs.mo.gov/content/2020-missouri-warn-notices"
        elif year == 2022:
            url = "https://jobs.mo.gov/content/2022-warn-notices"
        else:
            url = f"https://jobs.mo.gov/warn{year}"

        # Read from cache if available and not this year or the year before
        cache_key = f"mo/{year}.html"
        if cache.exists(cache_key) and year < current_year - 1:
            html = cache.read(cache_key)
        else:
            # Otherwise, go request it
            r = utils.get_url(url)
            html = r.text
            # Save it to the cache
            cache.write(cache_key, html)

        # Add it to the list
        html_list.append(html)

    # Parse them all
    output_rows = []
    for i, html in enumerate(html_list):
        # Parse the HTML
        utils.parse_tables(html, include_headers=i == 0)

        if len(cell_list) < 9:  # to account for the extra column in 2021
            cell_list.insert(2, "")

    # Set the export path
    data_path = data_dir / "mo.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the file
    return data_path


if __name__ == "__main__":
    scrape()
