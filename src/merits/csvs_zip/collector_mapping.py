from typing import Dict, Optional

from merits.csvs_zip.collector import Collector
from merits.exceptions import MeritsException


class CollectorMapping(Collector):
    """
    This collector maps header/column/key names before passing it on to a delegate collector.
    """

    def __init__(
            self,
            delegate: Collector,
            csv_file_name_2_name_in_dict_2_name_in_file: Optional[Dict[str, Dict[str, str]]] = None,
    ):
        """

        :param delegate: the delegate that will collect the mapped data
        :param csv_file_name_2_name_in_dict_2_name_in_file: the mapping for each csv file or None if you wish to use the
        add_mapping method instead.
        """
        super().__init__()

        if csv_file_name_2_name_in_dict_2_name_in_file:
            self._csv_file_name_2_name_in_dict_2_name_in_file = csv_file_name_2_name_in_dict_2_name_in_file
        else:
            self._csv_file_name_2_name_in_dict_2_name_in_file = {}
        self.delegate = delegate

    def add_mapping(self, csv_file_name: str, name_in_dict_2_name_in_file: Dict[str, str]) -> None:
        """
        Adds a mapping for one CSV file.
        :param csv_file_name:
        :param name_in_dict_2_name_in_file:
        :return: nothing
        """
        self._csv_file_name_2_name_in_dict_2_name_in_file[csv_file_name] = name_in_dict_2_name_in_file

    def collect(
            self,
            csv_file_name: str,
            row: Dict[str, str],
    ) -> None:
        name_in_dict_2_name_in_file: Dict[str, str] = self._csv_file_name_2_name_in_dict_2_name_in_file.get(
            csv_file_name
        )
        if not name_in_dict_2_name_in_file:
            raise MeritsException(
                f'Please, add a mapping for csv_file_name "{csv_file_name}" before collecting data.'
            )
        missing_mappings = row.keys() - name_in_dict_2_name_in_file.keys()
        if missing_mappings:
            raise MeritsException(
                f'Please, add a mapping for csv_file_name "{csv_file_name}"'
                f' for keys {list(missing_mappings)}.'
            )
        mapped_row = {
            name_in_dict_2_name_in_file[k]: v
            for k, v in row.items()
        }
        self.delegate.collect(csv_file_name, mapped_row)
