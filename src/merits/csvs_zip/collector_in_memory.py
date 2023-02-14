import csv
import io
from collections import defaultdict
from typing import Dict, List, Optional, Any
from zipfile import ZipFile

from merits.csvs_zip import config
from merits.csvs_zip.collector import Collector
from merits.exceptions import MeritsException


class CollectorInMemory(Collector):
    """
    Collects the rows in memory and gives the result as CSV string per file or ZIP with all files.
    """

    def __init__(
            self,
            csv_file_name_2_field_names: Dict[str, List[str]],
            csv_dict_writer_kwargs: Optional[Dict[str, Any]] = None,
            zip_file_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """

        :param csv_file_name_2_field_names:
        :param csv_dict_writer_kwargs: arguments passed on to csv.DictWriter constructor. Note that fieldnames is
        obtained from the keys of the first row and can NOT be set here.
        :param zip_file_kwargs: arguments passed on to zipfile.ZipFile.
        """
        super().__init__()

        self._csv_file_name_2_field_names = csv_file_name_2_field_names
        if csv_dict_writer_kwargs and "fieldnames" in csv_dict_writer_kwargs:
            del csv_dict_writer_kwargs["fieldnames"]
        self._csv_dict_writer_kwargs = config.get_csv_dict_writer_kwargs(csv_dict_writer_kwargs)
        if zip_file_kwargs:
            self._zip_file_kwargs = {
                k: v
                for k, v in zip_file_kwargs
                if k != "mode"
            }
        else:
            self._zip_file_kwargs = {}

        self._csv_file_name_2_row_list: Dict[str, List[Dict[str, str]]] = defaultdict(list)

    def collect(self, csv_file_name: str, row: Dict[str, str]) -> None:
        if csv_file_name not in self._csv_file_name_2_field_names:
            raise MeritsException(
                f'Please, specify the field names for csv_file_name "{csv_file_name}"'
                f' in argument csv_file_name_2_field_names in the CollectorInMemory constructor.'
            )
        row_list = self._csv_file_name_2_row_list[csv_file_name]
        row_list.append(row)

    def to_zip(self, file=None) -> Optional[bytes]:
        """
        Writes the collected data to CSV files in a ZIP file.

        :param file: as for zipfile.ZipFile can be a path to a file (a string), a file-like object or a path-like
        object. It can also be None to get bytes instead of writing to file.
        :return: the zipped bytes only if argument file was None
        """
        no_file = file is None
        if no_file:
            file = io.BytesIO()
        with ZipFile(
            file,
            mode="w",
            **self._zip_file_kwargs,
        ) as zf:
            for csv_file_name in self._csv_file_name_2_field_names.keys():
                text = self.to_csv(csv_file_name)
                zf.writestr(
                    zinfo_or_arcname=csv_file_name,
                    data=text,
                )
        if no_file:
            return file.getvalue()

    def to_csvs(self) -> Dict[str, str]:
        """
        Gives the collected data as CSV texts mapped by file name.
        :return: {csv_file_name: content}
        """
        csv_file_name_2_text = {}
        for csv_file_name in self._csv_file_name_2_field_names.keys():
            text = self.to_csv(csv_file_name)
            csv_file_name_2_text[csv_file_name] = text
        return csv_file_name_2_text

    def to_csv(self, csv_file_name: str, add_header: bool = True) -> str:
        """
        Gives the collected data for one CSV file as text
        :param csv_file_name: the name of the file to get the content for
        :param add_header: begin the result with the header
        :return: the content
        """
        field_names = self._csv_file_name_2_field_names.get(csv_file_name)
        if not field_names:
            raise MeritsException(
                f'Please, specify the field names for csv_file_name "{csv_file_name}"'
                f' in argument csv_file_name_2_field_names in the CollectorInMemory constructor.'
            )
        f = io.StringIO()
        dw = csv.DictWriter(f, fieldnames=field_names, **self._csv_dict_writer_kwargs)
        if add_header:
            dw.writeheader()
        row_list = self._csv_file_name_2_row_list[csv_file_name]
        dw.writerows(row_list)
        return f.getvalue()
