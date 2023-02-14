from typing import Dict

from merits.csvs_to_edifact_base import CsvsToEdifactBase
from merits.csvs_zip.csv_reader import CsvReader
from merits.csvs_zip.rows import Rows
from merits.edifact.collector_in_memory import CollectorInMemory
from merits.tsdupd import definition
from merits.tsdupd.csv_handler_to_edifact_collector import CsvHandlerToEdifactCollector


class CsvsToEdifact(CsvsToEdifactBase):
    """
    This class is a high level entry point for a conversion from CSVs to TSDUPD EDIFACT.
    """

    def __init__(self):
        self._csv_definition = definition.get_csv_hierarchy()
        self._edifact_definition = definition.edifact_definition
        self._edifact_collector = CollectorInMemory()
        self._csv_handler = CsvHandlerToEdifactCollector(
            edifact_collector=self._edifact_collector,
            definition=self._edifact_definition,
        )
        self._csv_reader = CsvReader(
            csv_hierarchy=self._csv_definition,
            csv_handler=self._csv_handler,
        )

    def load(
            self,
            csv_file_name_2_rows: Dict[str, Rows],
    ):
        self._csv_reader.read(csv_file_name_2_rows)

    def get(self) -> str:
        return self._edifact_collector.get()
