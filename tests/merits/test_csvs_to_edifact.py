from unittest import TestCase

from merits.skdupd.definition import META_FILE_NAME, ODI_FILE_NAME, RELATION_FILE_NAME, POR_FILE_NAME, TRAIN_FILE_NAME
from merits.skdupd.csvs_to_edifact import CsvsToEdifact
from merits.tsdupd.definition import (
    META_FILE_NAME as TSDUPD_META_FILE_NAME, STOP_FILE_NAME, SYNONYM_FILE_NAME, MCT_FILE_NAME, FOOTPATH_FILE_NAME,
)
from merits.tsdupd.csvs_to_edifact import CsvsToEdifact as TsdupdCsvsToEdifact
from . import test_data_helper


class TestCsvsToEdifact(TestCase):

    def test_read(self):
        csv_file_name_2_content = {
            META_FILE_NAME: test_data_helper.load_txt(test_data_helper.SKDUPD_ALL_FIELDS_META_FILE),
            TRAIN_FILE_NAME: test_data_helper.load_txt(test_data_helper.SKDUPD_ALL_FIELDS_TRAIN_FILE),
            POR_FILE_NAME: test_data_helper.load_txt(test_data_helper.SKDUPD_ALL_FIELDS_POR_FILE),
            RELATION_FILE_NAME: test_data_helper.load_txt(test_data_helper.SKDUPD_ALL_FIELDS_RELATION_FILE),
            ODI_FILE_NAME: test_data_helper.load_txt(test_data_helper.SKDUPD_ALL_FIELDS_ODI_FILE),
        }
        obj = CsvsToEdifact()
        obj.load_csvs(csv_file_name_2_content=csv_file_name_2_content)
        actual = obj.get()
        test_data_helper.dump_txt(actual, test_data_helper.SKDUPD_ALL_FIELDS_ACTUAL_FILE)
        expected = test_data_helper.load_txt(test_data_helper.SKDUPD_ALL_FIELDS_FILE)
        self.assertEqual(expected, actual)

    def test_read_tsdupd_escapes(self):
        csv_file_name_2_content = {
            TSDUPD_META_FILE_NAME: test_data_helper.load_txt(test_data_helper.TSDUPD_ESCAPES_META_FILE),
            STOP_FILE_NAME: test_data_helper.load_txt(test_data_helper.TSDUPD_ESCAPES_STOP_FILE),
            SYNONYM_FILE_NAME: test_data_helper.load_txt(test_data_helper.TSDUPD_ESCAPES_SYNONYM_FILE),
            MCT_FILE_NAME: test_data_helper.load_txt(test_data_helper.TSDUPD_ESCAPES_MCT_FILE),
            FOOTPATH_FILE_NAME: test_data_helper.load_txt(test_data_helper.TSDUPD_ESCAPES_FOOTPATH_FILE),
        }
        obj = TsdupdCsvsToEdifact()
        obj.load_csvs(csv_file_name_2_content=csv_file_name_2_content)
        actual = obj.get()
        test_data_helper.dump_txt(actual, test_data_helper.TSDUPD_ESCAPES_ACTUAL_FILE)
        expected = test_data_helper.load_txt(test_data_helper.TSDUPD_ESCAPES_FILE)
        self.assertEqual(expected, actual)

    def test_read_tsdupd_v3(self):
        csv_file_name_2_content = {
            TSDUPD_META_FILE_NAME: test_data_helper.load_txt(test_data_helper.TSDUPD_V3_META_FILE),
            STOP_FILE_NAME: test_data_helper.load_txt(test_data_helper.TSDUPD_V3_STOP_FILE),
            SYNONYM_FILE_NAME: test_data_helper.load_txt(test_data_helper.TSDUPD_V3_SYNONYM_FILE),
            MCT_FILE_NAME: test_data_helper.load_txt(test_data_helper.TSDUPD_V3_MCT_FILE),
            FOOTPATH_FILE_NAME: test_data_helper.load_txt(test_data_helper.TSDUPD_V3_FOOTPATH_FILE),
        }
        obj = TsdupdCsvsToEdifact()
        obj.load_csvs(csv_file_name_2_content=csv_file_name_2_content)
        actual = obj.get()
        test_data_helper.dump_txt(actual, test_data_helper.TSDUPD_V3_ACTUAL_FILE)
        expected = test_data_helper.load_txt(test_data_helper.TSDUPD_V3_FILE)
        self.assertEqual(expected, actual)
