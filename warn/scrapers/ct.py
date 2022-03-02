import logging
from datetime import datetime
from pathlib import Path

from .. import utils
from ..cache import Cache

__authors__ = [
    "zstumgoren",
    "Dilcia19",
    "stucka",
]
__tags__ = ["html"]

logger = logging.getLogger(__name__)


def scrape(
    data_dir: Path = utils.WARN_DATA_DIR,
    cache_dir: Path = utils.WARN_CACHE_DIR,
) -> Path:
    """
    Scrape data from Connecticut.

    Keyword arguments:
    data_dir -- the Path were the result will be saved (default WARN_DATA_DIR)
    cache_dir -- the Path where results can be cached (default WARN_CACHE_DIR)

    Returns: the Path where the file is written
    """
    # Open the cache
    cache = Cache(cache_dir)

    # We start in 2015
    current_year = datetime.now().year

    # Get the full range of years
    year_range = range(2015, current_year + 1)

    output_rows = []
    for year in year_range:
        url = f"https://www.ctdol.state.ct.us/progsupt/bussrvce/warnreports/warn{year}.htm"
        cache_key = f"ct/{year}.html"

        if cache.exists(cache_key) and year < current_year:
            html = cache.read(cache_key)
        else:
            r = utils.get_url(url)
            html = r.text
            cache.write(cache_key, html)

        # Set the class to target for the table
        table_class = "style15" if year == 2016 else "MsoTableNormal"

        # Parse out the table
        table_list = utils.parse_tables(html, include_headers=False, class_=table_class)

        output_rows = []

        for table_rows in table_list:
            for table_cells in table_rows:
                if len(table_cells) > 9:
                    output_row = _merge_problem_cells(table_cells)
                    row_list.append(output_row)
                    continue
                # if a row has less than 9 it is skipped because it is incomplete
                elif len(table_cells) < 9:
                    continue
                else:
                    output_rows.append(table_cells)

        # Add data to the big list
        output_rows.extend(row_list)

    # Tack headers on the top
    header_row = [
        "warn_date",
        "affected_company",
        "layoff_location",
        "number_workers",
        "layoff_date",
        "closing",
        "closing_date",
        "union",
        "union_address",
    ]
    row_list = [header_row] + output_rows

    # Set the export path
    data_path = data_dir / "ct.csv"

    # Write out to csv
    utils.write_rows_to_csv(data_path, row_list)

    # Return the path
    return data_path


def _merge_problem_cells(table_cells):
    """Deal with problem rows in the 2016 table."""
    output_row = []
    for i, current_cell in enumerate(table_cells):
        current_cell = " ".join(current_cell.split())
        if i == 0:
            output_row.append(current_cell)
        else:
            previous_index = i - 1
            previous_cell = table_cells[previous_index]
            previous_cell = " ".join(previous_cell.split())
            if current_cell == previous_cell:
                continue
            else:
                output_row.append(current_cell)
    return output_row


if __name__ == "__main__":
    scrape()
