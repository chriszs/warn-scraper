import logging
from pathlib import Path

import requests
from bs4 import BeautifulSoup

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
    Scrape data from Washington.

    Arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Set the cache
    cache = Cache(cache_dir)

    output_rows = []

    with requests.Session() as session:
        # Request the initial page
        url = "https://fortress.wa.gov/esd/file/warn/Public/SearchWARN.aspx"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:68.0) Gecko/20100101 Firefox/68.0"
        r = utils.get_url(url, user_agent=user_agent, session=session)

        # Save it to the cache
        html = r.text
        cache.write("wa/source.html", html)

        # Parse out the headers
        table_list = utils.parse_tables(html)

        # Start jumping through the pages
        soup_content = BeautifulSoup(r.content, "html5lib")

        page = 2
        while True:
            try:
                # Post for the next page
                formdata = {
                    "__EVENTTARGET": "ucPSW$gvMain",
                    "__EVENTARGUMENT": f"Page${page}",
                    "__VIEWSTATE": soup_content.find(
                        "input", attrs={"name": "__VIEWSTATE"}
                    )["value"],
                    "__EVENTVALIDATION": soup_content.find(
                        "input", attrs={"name": "__EVENTVALIDATION"}
                    )["value"],
                }
                next = session.post(url, data=formdata)
                logger.debug(f"Page status is {next.status_code} for {url}")

                # Update the input variables
                soup_content = BeautifulSoup(next.content, "html5lib")

                # Cache the html
                html = next.text
                cache.write(f"wa/{page}.html", html)

                # Parse out the data
                table_list = utils.parse_tables(html)
                row_list[2 : len(row_list) - 2]

                # Up the page number
                page += 1

            # Once it fails, we're done
            except Exception:
                break

    # Set the export path
    data_path = data_dir / "wa.csv"

    # Write out the file
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the path to the file
    return data_path


if __name__ == "__main__":
    scrape()
