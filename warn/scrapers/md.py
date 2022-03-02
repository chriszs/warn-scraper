import logging
from pathlib import Path

from bs4 import BeautifulSoup

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
    Scrape data from Maryland.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Set the cache
    cache = Cache(cache_dir)

    # Get the page
    url = "http://www.dllr.state.md.us/employment/warn.shtml"
    r = utils.get_url(url)
    r.encoding = "utf-8"
    html = r.text

    # Save it to the cache
    cache.write("md/source.html", html)

    # Parse the list of links
    soup = BeautifulSoup(html, "html.parser")
    a_list = soup.find_all("a", {"class": "sub"})
    href_list = [a["href"] for a in a_list]

    # Download them all
    html_list = []
    for href in href_list:

        # Request the HTML
        url = f"http://www.dllr.state.md.us/employment/{href}"
        r = utils.get_url(url)
        r.encoding = "utf-8"
        html = r.text

        # Save it to the cache
        cache.write(f"md/{href}.html", html)

        # Add it to the list
        html_list.append(html)

    # Parse them all
    output_rows = []
    for i, html in enumerate(html_list):
        # Parse the HTML
        table_list = utils.parse_tables(html, include_headers=i == 0)

        # Add the rows
        output_rows += table_list[0]

    # Set the export path
    data_path = data_dir / "md.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the file
    return data_path


if __name__ == "__main__":
    scrape()
