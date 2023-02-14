from abc import ABC, abstractmethod
from collections import deque
from csv import DictReader
from io import StringIO, BytesIO
from pathlib import Path
from typing import Dict, List, Iterable, Collection, Optional, Any, Union, BinaryIO
from zipfile import ZipFile

from merits.csvs_zip import config


class Rows(ABC):
    """
    This interface provides CSV data rows for a single CSV table/file.
    """

    @abstractmethod
    def headers(self) -> List[str]:
        pass

    @abstractmethod
    def has_more(self) -> bool:
        """
        Indicates if at least one more row is available.
        :return:
        """
        pass

    @abstractmethod
    def peek(self) -> Dict[str, str]:
        """
        Reads the next row but keeps it in the data.
        :return:
        :raise StopIteration: if no more rows are available
        """
        pass

    @abstractmethod
    def pop(self) -> Dict[str, str]:
        """
        Reads the next row and removes it from the data.
        :return:
        :raise StopIteration: if no more rows are available
        """
        pass


class RowsInMemory(Rows):
    """
    This implementation has all the data as dicts in memory.
    """

    def __init__(
            self,
            data: Iterable[Dict[str, str]],
            headers: Collection[str],
    ):
        super().__init__()
        self.data: deque[Dict[str, str]] = deque(data)
        self._headers = headers

    def headers(self) -> List[str]:
        return list(self._headers)

    def has_more(self) -> bool:
        return bool(self.data)

    def peek(self) -> Dict[str, str]:
        return self.data[0]

    def pop(self) -> Dict[str, str]:
        return self.data.popleft()


class RowsDictReader(Rows):
    """
    This implementation reads from a csv.DictReader and can buffer one row to support the peek operation.
    """

    def __init__(
            self,
            dict_reader: DictReader,
    ):
        super().__init__()
        self._dict_reader = dict_reader
        self._headers = self._dict_reader.fieldnames
        self._peeked: Optional[Dict[str, str]] = None

    def headers(self) -> List[str]:
        return list(self._headers)

    def has_more(self) -> bool:
        return self._try_peek() is None

    def peek(self) -> Dict[str, str]:
        if not self._peeked:
            self._peeked = next(self._dict_reader)
        return self._peeked

    def pop(self) -> Dict[str, str]:
        if self._peeked:
            result = self._peeked
            self._peeked = None
        else:
            result = next(self._dict_reader)
        return result

    def _try_peek(self) -> Dict[str, str]:
        """
        Almost as the peek operation but returns None (instead of raising StopIteration) if no row is available.
        :return:
        """
        if not self._peeked:
            try:
                self._peeked = next(self._dict_reader)
            except StopIteration:
                self._peeked = None
        return self._peeked


class RowsFactory(object):
    """
    This class contains convenience methods for creating Rows objects.
    """

    @staticmethod
    def from_string(
            csv_content: str,
            csv_dict_reader_kwargs: Optional[Dict[str, Any]] = None,
            pre_load: bool = True,
    ) -> Rows:
        """
        Gives the single string content of one CSV file as a Rows object.
        :param csv_content:
        :param csv_dict_reader_kwargs:
        :param pre_load: if True convert to dicts now, else use a csv.DictReader on the fly
        :return:
        """
        f = StringIO(csv_content)
        dr = DictReader(f, **config.get_csv_dict_reader_kwargs(csv_dict_reader_kwargs))

        if pre_load:
            row_list = [
                row
                for row in dr
            ]
            rows = RowsInMemory(
                data=row_list,
                headers=dr.fieldnames,
            )
        else:
            rows = RowsDictReader(
                dict_reader=dr,
            )

        return rows

    @staticmethod
    def from_files(
            csv_paths: List[Union[str, Path]],
            csv_dict_reader_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Rows]:
        """
        Gives the contents of the CSV files as Rows objects
        :param csv_paths: source files paths
        :param csv_dict_reader_kwargs:
        :return: Dict[csv_file_name_without_path: str, Rows]
        """
        csv_file_name_2_rows = {}
        for path in csv_paths:
            if isinstance(path, str):
                path = Path(path)
            csv_file_name = path.name
            with open(path, "r") as f:
                text = f.read()
            rows = RowsFactory.from_string(
                csv_content=text,
                csv_dict_reader_kwargs=csv_dict_reader_kwargs,
            )
            csv_file_name_2_rows[csv_file_name] = rows
        return csv_file_name_2_rows

    @staticmethod
    def from_directory(
            directory: Union[str, Path],
            name_pass_filter: Optional[Collection[str]] = None,
    ) -> Dict[str, Rows]:
        """
        Reads all *.csv (case-insensitive extension) files in the directory
        :param directory:
        :param name_pass_filter:
        :return: Dict[csv_file_name_without_path: str, Rows]
        """
        if not isinstance(directory, Path):
            directory = Path(directory)
        csv_paths = [
            csv_path
            for csv_path in directory.glob("*.[Cc][Ss][Vv]")
            if name_pass_filter is None or csv_path.name in name_pass_filter
        ]
        return RowsFactory.from_files(csv_paths)

    @staticmethod
    def from_zip(
        zipped: Union[str, Path, bytes, BinaryIO],
    ) -> Dict[str, Rows]:
        """
        Makes rows from a zipped archive.
        :param zipped: Path or str: path to the zipped file; bytes: zipped bytes; BinaryIO zipped file-like object
        :return: { csv_file_name: rows }
        """
        csv_file_name_2_rows = {}
        if isinstance(zipped, bytes):
            f = BytesIO(zipped)
        else:
            f = zipped

        with ZipFile(file=f) as zf:
            for csv_file_name in zf.namelist():
                csv_content = zf.read(csv_file_name).decode()
                rows = RowsFactory.from_string(csv_content)
                csv_file_name_2_rows[csv_file_name] = rows

        return csv_file_name_2_rows
