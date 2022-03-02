import logging
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
    Scrape data from South Dakota.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Open the cache
    cache = Cache(cache_dir)

    # Get the HTML
    url = "https://dlr.sd.gov/workforce_services/businesses/warn_notices.aspx"
    r = utils.get_url(url)
    html = r.text
    cache.write("sd/source.html", html)

    # Scrape out the data
    table_list = utils.parse_tables(html)

    row_list = table_list[0]

    # Write out
    data_path = data_dir / "sd.csv"
    utils.write_rows_to_csv(data_path, row_list)

    # Return the path to the CSV
    return data_path


if __name__ == "__main__":
    scrape()
