from abc import ABC, abstractmethod
from typing import Dict, List


class EdifactToCsvsBase(ABC):
    """
    This class defines an interface for converting from an EDIFACT to CSV format.
    """

    @abstractmethod
    def get_csv_file_name_2_next_id(self) -> Dict[str, int]:
        """
        Gets the next CSV row IDs after conversion to be used if you want to continue counting in more conversions.
        :return:
        """
        pass

    @abstractmethod
    def set_csv_file_name_2_next_id(
            self,
            csv_file_name_2_next_id: Dict[str, int],
    ) -> None:
        """
        This sets the first CSV row IDs if you want to continue counting from a previous conversion.
        :param csv_file_name_2_next_id:
        :return:
        """
        pass

    @abstractmethod
    def load(
            self,
            edifact_segments: List[str],
    ) -> None:
        """
        Reads and converts the edifact segments to CSV format.
        :param edifact_segments:
        :return:
        """
        pass

    @abstractmethod
    def get_csvs(self) -> Dict[str, str]:
        """
        Gives the loaded CSV files as a dict from file name to file content.
        :return:
        """
        pass

    @abstractmethod
    def get_zip(self) -> bytes:
        """
        Gives the loaded CSV files as zipped bytes
        :return:
        """
        pass
