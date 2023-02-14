from abc import ABC, abstractmethod
from typing import Dict


class CsvHandler(ABC):
    """
    Interface for handling parsed rows from a CSV hierarchy.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def handle_begin(self, meta_data: Dict[str, str]):
        """
        This method is called as first, just after the single meta.csv row is read.
        :param meta_data: the row from the meta CSV file.
        :return:
        """
        pass

    @abstractmethod
    def handle_row(
            self,
            csv_file_name: str,
            row: Dict[str, str],
    ):
        """
        This is called for every row in every CSV file in the order of parent then children as given by a CsvHierarchy
        and the actual data.
        :param csv_file_name: the name of the file where this row came from
        :param row: the data in the row from field name to value
        :return:
        """
        pass

    @abstractmethod
    def handle_end(self, meta_data: Dict[str, str]):
        """
        This is called after all rows from all CSV files have been handled.
        :param meta_data: the same as in the handle_begin method, because it may contain useful info like a reference
        :return:
        """
        pass
