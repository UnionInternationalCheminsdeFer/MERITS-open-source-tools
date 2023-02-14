import csv
from typing import Any, Dict


def get_csv_dict_writer_kwargs(override_kwargs=None) -> Dict[str, Any]:
    """
    Gives the kwargs for constructing a csv.DictWriter with the standard options for this project.
    :param override_kwargs: optional overrides
    :return:
    """
    result = {
        "delimiter": ";",
        "quoting": csv.QUOTE_ALL,
        "lineterminator": "\n",
    }
    if override_kwargs:
        result.update(override_kwargs)
    return result


def get_csv_dict_reader_kwargs(override_kwargs=None) -> Dict[str, Any]:
    """
    Gives the kwargs for constructing a csv.DictReader with the standard options for this project.
    :param override_kwargs: optional overrides
    :return:
    """
    result = {
        "delimiter": ";",
        "quoting": csv.QUOTE_ALL,
        "lineterminator": "\n",
        "restval": "",
    }
    if override_kwargs:
        result.update(override_kwargs)
    return result
