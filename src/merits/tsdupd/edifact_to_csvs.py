import dataclasses
from typing import Dict, List, Optional

from merits.csvs_zip.collector_in_memory import CollectorInMemory
from merits.edifact.edifact_reader import EdifactReader
from merits.edifact_to_csvs_base import EdifactToCsvsBase
from merits.tsdupd import definition
from merits.tsdupd.definition import (
    META_FILE_NAME, STOP_FILE_NAME, SYNONYM_FILE_NAME, MCT_FILE_NAME, FOOTPATH_FILE_NAME
)
from merits.tsdupd.csv_model import Meta, Stop, Synonym, Mct, Footpath
from merits.tsdupd.data_handler_to_csv_collector import DataHandlerToCsvCollector


class EdifactToCsvs(EdifactToCsvsBase):
    """
    This class is the high level entrypoint for converting TSDUPD EDIFACT to CSV files.
    """

    def __init__(
            self,
    ):
        self._definition = definition.edifact_definition
        self._csv_collector = CollectorInMemory(
            csv_file_name_2_field_names={
                STOP_FILE_NAME: [
                    field.name
                    for field in dataclasses.fields(Stop)
                ],
                SYNONYM_FILE_NAME: [
                    field.name
                    for field in dataclasses.fields(Synonym)
                ],
                MCT_FILE_NAME: [
                    field.name
                    for field in dataclasses.fields(Mct)
                ],
                FOOTPATH_FILE_NAME: [
                    field.name
                    for field in dataclasses.fields(Footpath)
                ],
                META_FILE_NAME: [
                    field.name
                    for field in dataclasses.fields(Meta)
                ],
            },
        )
        self._data_handler = DataHandlerToCsvCollector(
            csv_collector=self._csv_collector,
            definition=self._definition,
        )
        self._edifact_reader = EdifactReader(
            definition=self._definition,
        )

    def get_csv_file_name_2_next_id(self) -> Dict[str, int]:
        return self._data_handler.get_csv_file_name_2_next_id()

    def set_csv_file_name_2_next_id(self, csv_file_name_2_next_id: Dict[str, int]) -> None:
        self._data_handler.set_csv_file_name_2_next_id(csv_file_name_2_next_id)

    def load(
            self,
            edifact_segments: List[str],
    ):
        """
        Reads and converts the edifact segments to CSV format.
        :param edifact_segments:
        :return:
        """
        self._edifact_reader.read(
            segments=edifact_segments,
            data_handler=self._data_handler,
        )

    def get_csvs(self) -> Dict[str, str]:
        """
        Gives the loaded CSV files as a dict from file name to file content.
        :return:
        """
        return self._csv_collector.to_csvs()

    def get_zip(self) -> bytes:
        """
        Gives the loaded CSV files as zipped bytes
        :return:
        """
        return self._csv_collector.to_zip()
