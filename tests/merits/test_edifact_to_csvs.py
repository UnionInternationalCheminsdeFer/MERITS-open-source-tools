from unittest import TestCase

from merits.skdupd.definition import META_FILE_NAME, ODI_FILE_NAME, RELATION_FILE_NAME, POR_FILE_NAME, TRAIN_FILE_NAME
from merits.skdupd.edifact_to_csvs import EdifactToCsvs as SkdupdEdifactToCsvs
from merits.tsdupd import definition as tsdupd_definition
from merits.tsdupd.edifact_to_csvs import EdifactToCsvs as TsdupdEdifactToCsvs
from . import test_data_helper


class TestEdifactToCsvs(TestCase):

    def test_get_csvs_skdupd(self):
        # edifact = test_data_helper.load_txt(test_data_helper.SKDUPD_EXAMPLE_FILE)
        edifact = test_data_helper.load_txt(test_data_helper.SKDUPD_ALL_FIELDS_FILE)
        edifact_segments = edifact.splitlines(keepends=False)

        obj = SkdupdEdifactToCsvs()
        obj.load(edifact_segments=edifact_segments)
        actual = obj.get_csvs()
        actual_meta = actual[META_FILE_NAME]
        actual_odi = actual[ODI_FILE_NAME]
        actual_por = actual[POR_FILE_NAME]
        actual_relation = actual[RELATION_FILE_NAME]
        actual_train = actual[TRAIN_FILE_NAME]
        test_data_helper.dump_txt(
            content=actual_meta,
            file=test_data_helper.SKDUPD_ALL_FIELDS_META_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_odi,
            file=test_data_helper.SKDUPD_ALL_FIELDS_ODI_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_por,
            file=test_data_helper.SKDUPD_ALL_FIELDS_POR_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_relation,
            file=test_data_helper.SKDUPD_ALL_FIELDS_RELATION_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_train,
            file=test_data_helper.SKDUPD_ALL_FIELDS_TRAIN_ACTUAL_FILE,
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.SKDUPD_ALL_FIELDS_META_FILE),
            actual_meta,
            "Wrong " + META_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.SKDUPD_ALL_FIELDS_ODI_FILE),
            actual_odi,
            "Wrong " + ODI_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.SKDUPD_ALL_FIELDS_POR_FILE),
            actual_por,
            "Wrong " + POR_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.SKDUPD_ALL_FIELDS_RELATION_FILE),
            actual_relation,
            "Wrong " + RELATION_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.SKDUPD_ALL_FIELDS_TRAIN_FILE),
            actual_train,
            "Wrong " + TRAIN_FILE_NAME
        )

    def test_get_csvs_tsdupd(self):
        edifact = test_data_helper.load_txt(test_data_helper.TSDUPD_ALL_FIELDS_FILE)
        edifact_segments = edifact.splitlines(keepends=False)

        obj = TsdupdEdifactToCsvs()
        obj.load(edifact_segments=edifact_segments)
        actual = obj.get_csvs()
        actual_meta = actual[tsdupd_definition.META_FILE_NAME]
        actual_stop = actual[tsdupd_definition.STOP_FILE_NAME]
        actual_synonym = actual[tsdupd_definition.SYNONYM_FILE_NAME]
        actual_mct = actual[tsdupd_definition.MCT_FILE_NAME]
        actual_footpath = actual[tsdupd_definition.FOOTPATH_FILE_NAME]
        test_data_helper.dump_txt(
            content=actual_meta,
            file=test_data_helper.TSDUPD_ALL_FIELDS_META_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_stop,
            file=test_data_helper.TSDUPD_ALL_FIELDS_STOP_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_synonym,
            file=test_data_helper.TSDUPD_ALL_FIELDS_SYNONYM_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_mct,
            file=test_data_helper.TSDUPD_ALL_FIELDS_MCT_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_footpath,
            file=test_data_helper.TSDUPD_ALL_FIELDS_FOOTPATH_ACTUAL_FILE,
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_ALL_FIELDS_META_FILE),
            actual_meta,
            "Wrong " + tsdupd_definition.META_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_ALL_FIELDS_STOP_FILE),
            actual_stop,
            "Wrong " + tsdupd_definition.STOP_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_ALL_FIELDS_SYNONYM_FILE),
            actual_synonym,
            "Wrong " + tsdupd_definition.SYNONYM_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_ALL_FIELDS_MCT_FILE),
            actual_mct,
            "Wrong " + tsdupd_definition.MCT_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_ALL_FIELDS_FOOTPATH_FILE),
            actual_footpath,
            "Wrong " + tsdupd_definition.FOOTPATH_FILE_NAME
        )

    def test_get_csvs_tsdupd_escapes(self):
        edifact = test_data_helper.load_txt(test_data_helper.TSDUPD_ESCAPES_FILE)
        edifact_segments = edifact.splitlines(keepends=False)

        obj = TsdupdEdifactToCsvs()
        obj.load(edifact_segments=edifact_segments)
        actual = obj.get_csvs()
        actual_meta = actual[tsdupd_definition.META_FILE_NAME]
        actual_stop = actual[tsdupd_definition.STOP_FILE_NAME]
        actual_synonym = actual[tsdupd_definition.SYNONYM_FILE_NAME]
        actual_mct = actual[tsdupd_definition.MCT_FILE_NAME]
        actual_footpath = actual[tsdupd_definition.FOOTPATH_FILE_NAME]
        test_data_helper.dump_txt(
            content=actual_meta,
            file=test_data_helper.TSDUPD_ESCAPES_META_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_stop,
            file=test_data_helper.TSDUPD_ESCAPES_STOP_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_synonym,
            file=test_data_helper.TSDUPD_ESCAPES_SYNONYM_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_mct,
            file=test_data_helper.TSDUPD_ESCAPES_MCT_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_footpath,
            file=test_data_helper.TSDUPD_ESCAPES_FOOTPATH_ACTUAL_FILE,
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_ESCAPES_META_FILE),
            actual_meta,
            "Wrong " + tsdupd_definition.META_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_ESCAPES_STOP_FILE),
            actual_stop,
            "Wrong " + tsdupd_definition.STOP_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_ESCAPES_SYNONYM_FILE),
            actual_synonym,
            "Wrong " + tsdupd_definition.SYNONYM_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_ESCAPES_MCT_FILE),
            actual_mct,
            "Wrong " + tsdupd_definition.MCT_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_ESCAPES_FOOTPATH_FILE),
            actual_footpath,
            "Wrong " + tsdupd_definition.FOOTPATH_FILE_NAME
        )

    def test_get_csvs_tsdupd_v3(self):
        edifact = test_data_helper.load_txt(test_data_helper.TSDUPD_V3_FILE)
        edifact_segments = edifact.splitlines(keepends=False)

        obj = TsdupdEdifactToCsvs()
        obj.load(edifact_segments=edifact_segments)
        actual = obj.get_csvs()
        actual_meta = actual[tsdupd_definition.META_FILE_NAME]
        actual_stop = actual[tsdupd_definition.STOP_FILE_NAME]
        actual_synonym = actual[tsdupd_definition.SYNONYM_FILE_NAME]
        actual_mct = actual[tsdupd_definition.MCT_FILE_NAME]
        actual_footpath = actual[tsdupd_definition.FOOTPATH_FILE_NAME]
        test_data_helper.dump_txt(
            content=actual_meta,
            file=test_data_helper.TSDUPD_V3_META_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_stop,
            file=test_data_helper.TSDUPD_V3_STOP_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_synonym,
            file=test_data_helper.TSDUPD_V3_SYNONYM_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_mct,
            file=test_data_helper.TSDUPD_V3_MCT_ACTUAL_FILE,
        )
        test_data_helper.dump_txt(
            content=actual_footpath,
            file=test_data_helper.TSDUPD_V3_FOOTPATH_ACTUAL_FILE,
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_V3_META_FILE),
            actual_meta,
            "Wrong " + tsdupd_definition.META_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_V3_STOP_FILE),
            actual_stop,
            "Wrong " + tsdupd_definition.STOP_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_V3_SYNONYM_FILE),
            actual_synonym,
            "Wrong " + tsdupd_definition.SYNONYM_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_V3_MCT_FILE),
            actual_mct,
            "Wrong " + tsdupd_definition.MCT_FILE_NAME
        )
        self.assertEqual(
            test_data_helper.load_txt(test_data_helper.TSDUPD_V3_FOOTPATH_FILE),
            actual_footpath,
            "Wrong " + tsdupd_definition.FOOTPATH_FILE_NAME
        )
