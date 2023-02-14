from pathlib import Path
from unittest import TestCase

from . import test_data_helper
from merits.edifact.edifact_reader import EdifactReader

from merits.skdupd.definition import edifact_definition as skdupd_definition
from merits.tsdupd.definition import edifact_definition as tsdupd_definition
from .test_data_helper import DataHandlerToStr


class TestEdifactReader(TestCase):

    FILE_001_PRINT = Path("tests/merits/test_edifact_reader-001-print.txt")
    FILE_001_PRINT_ACTUAL = Path("tests/merits/test_edifact_reader-001-print-actual.txt")
    FILE_002_PRINT = Path("tests/merits/test_edifact_reader-002-print.txt")
    FILE_002_PRINT_ACTUAL = Path("tests/merits/test_edifact_reader-002-print-actual.txt")
    FILE_003_PRINT = Path("tests/merits/test_edifact_reader-003-print.txt")
    FILE_003_PRINT_ACTUAL = Path("tests/merits/test_edifact_reader-003-print-actual.txt")

    def test_read(self):
        # Load input data.
        edifact = test_data_helper.load_txt(test_data_helper.SKDUPD_ALL_FIELDS_FILE)
        edifact_lines = edifact.splitlines(keepends=False)
        # Create objects.
        edifact_reader = EdifactReader(
            definition=skdupd_definition,
        )
        data_handler = DataHandlerToStr(do_print=False)
        # Execute.
        edifact_reader.read(
            segments=edifact_lines,
            data_handler=data_handler,
        )
        actual = data_handler.get_result()
        test_data_helper.dump_txt(actual, self.FILE_001_PRINT_ACTUAL)
        expected = test_data_helper.load_txt(self.FILE_001_PRINT)
        self.assertEqual(expected, actual, "Wrong printed result.")

    def test_read_tsdupd(self):
        # Load input data.
        edifact = test_data_helper.load_txt(test_data_helper.TSDUPD_ALL_FIELDS_FILE)
        edifact_lines = edifact.splitlines(keepends=False)
        # Create objects.
        edifact_reader = EdifactReader(
            definition=tsdupd_definition,
        )
        data_handler = DataHandlerToStr(do_print=False)
        # Execute.
        edifact_reader.read(
            segments=edifact_lines,
            data_handler=data_handler,
        )
        actual = data_handler.get_result()
        test_data_helper.dump_txt(actual, self.FILE_002_PRINT_ACTUAL)
        expected = test_data_helper.load_txt(self.FILE_002_PRINT)
        self.assertEqual(expected, actual, "Wrong printed result.")
