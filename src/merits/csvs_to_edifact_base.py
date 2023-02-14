from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, BinaryIO, Union

from merits.csvs_zip.rows import RowsFactory, Rows


class CsvsToEdifactBase(ABC):
    """
    This class defines a high level entry point for a conversion from CSVs to EDIFACT.
    """

    def load_zip(
            self,
            zipped: Union[str, Path, bytes, BinaryIO],
    ) -> None:
        """
        Convenience method for loading from a zipped archive. The file names inside the ZIP must be the same as in the
        CsvHierarchy in the definition.

        :param zipped: source: [str or Path] the path to a file; [bytes] the zipped bytes; [BinaryIO] file-like
        :return: None
        """
        csv_file_name_2_rows = RowsFactory.from_zip(zipped)
        self.load(csv_file_name_2_rows)

    def load_csvs(
            self,
            csv_file_name_2_content: Dict[str, str],
    ) -> None:
        """
        Convenience method to load
        :param csv_file_name_2_content:
        :return:
        """
        csv_file_name_2_rows = {
            csv_file_name: RowsFactory.from_string(content)
            for csv_file_name, content in csv_file_name_2_content.items()
        }
        self.load(csv_file_name_2_rows)

    @abstractmethod
    def load(
            self,
            csv_file_name_2_rows: Dict[str, Rows],
    ) -> None:
        """
        Reads and converts the CSV data from csv_file_name_2_rows and makes the resulting EDIFACT available through the
        get method.

        You may use RowsFactory to obtain Rows objects from different sources (zipped, strings, files, etc).

        :param csv_file_name_2_rows: csv_file_name must be the same as in the CsvHierarchy in the definition
        :return:
        """
        pass

    @abstractmethod
    def get(self) -> str:
        """
        After loading is completed, this method returns the EDIFACT file content as one string.
        :return:
        """
        pass
