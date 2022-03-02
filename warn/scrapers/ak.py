from pathlib import Path

from .. import utils

__authors__ = ["zstumgoren", "Dilcia19"]
__tags__ = [
    "html",
]


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Alaska.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Get URL
    page = utils.get_url("https://jobs.alaska.gov/RR/WARN_notices.htm")

    # Force encoding to fix dashes, apostrophes, etc. on page.text from requests reponse
    page.encoding = "utf-8"

    # Scrape out any tables
    table_list = utils.parse_tables(page.text)

    # Get rows from the first table
    output_rows = table_list[0]

    # Write out the data to a CSV
    data_path = data_dir / "ak.csv"
    utils.write_rows_to_csv(data_path, output_rows)

    # Return the Path to the CSV
    return data_path


if __name__ == "__main__":
    scrape()
