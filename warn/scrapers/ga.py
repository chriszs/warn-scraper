from datetime import datetime
from pathlib import Path

from .. import utils
from ..cache import Cache

__authors__ = ["chriszs"]
__tags__ = ["html"]


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Georgia.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    state_code = "ga"
    cache = Cache(cache_dir)

    # The basic configuration for the scrape
    base_url = "https://www.dol.state.ga.us/public/es/warn/searchwarns/list"

    area = 9  # statewide

    current_year = datetime.now().year
    first_year = 2002  # first available year

    years = list(range(first_year, current_year + 1))
    years.reverse()

    # Loop through the years and scrape them one by one
    output_rows = []
    for i, year in enumerate(years):
        # Concoct the URL
        url = f"{base_url}?geoArea={area}&year={year}&step=search"
        cache_key = f"{state_code}/{year}.html"

        # Read from cache if available and not this year or the year before
        if cache.exists(cache_key) and year < current_year - 1:
            html = cache.read(cache_key)
        else:
            # Otherwise, go request it
            page = utils.get_url(url)
            html = page.text
            cache.write(cache_key, html)

        # Scrape out any tables
        table_list = utils.parse_tables(
            html,
            include_headers=i == 0,  # After the first loop, we can skip the headers
            id="emplrList",
        )

        # Get rows from the first table ob the page
        new_rows = table_list[0]

        # Concatenate the rows
        output_rows.extend(new_rows)

    # Write out the results
    data_path = data_dir / f"{state_code}.csv"
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the CSV
    return data_path


if __name__ == "__main__":
    scrape()
