from abc import ABC, abstractmethod
from typing import Dict


class Collector(ABC):
    """
    This interface gathers rows for different CSV files.
    """

    def __init__(self):
        pass

    @abstractmethod
    def collect(self, csv_file_name: str, row: Dict[str, str]) -> None:
        """
        Adds a row to the CSV file indicated by csv_file_name.

        :param csv_file_name:
        :param row:
        :return:
        """
        pass
