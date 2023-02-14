from pathlib import Path
from typing import List

from merits.edifact.data_handler import DataHandler
from merits.edifact.object_model import DataLeaf, DataBranch

SKDUPD_ALL_FIELDS_FILE = Path("tests/EDIFACT_examples/SKDUPD_all_fields.r")
SKDUPD_ALL_FIELDS_META_FILE = Path("tests/EDIFACT_examples/SKDUPD_all_fields_META.csv")
SKDUPD_ALL_FIELDS_ODI_FILE = Path("tests/EDIFACT_examples/SKDUPD_all_fields_ODI.csv")
SKDUPD_ALL_FIELDS_POR_FILE = Path("tests/EDIFACT_examples/SKDUPD_all_fields_POR.csv")
SKDUPD_ALL_FIELDS_RELATION_FILE = Path("tests/EDIFACT_examples/SKDUPD_all_fields_RELATION.csv")
SKDUPD_ALL_FIELDS_TRAIN_FILE = Path("tests/EDIFACT_examples/SKDUPD_all_fields_TRAIN.csv")
SKDUPD_ALL_FIELDS_ACTUAL_FILE = Path("tests/EDIFACT_examples/SKDUPD_all_fields-actual.r")
SKDUPD_ALL_FIELDS_META_ACTUAL_FILE = Path("tests/EDIFACT_examples/SKDUPD_all_fields_META-actual.csv")
SKDUPD_ALL_FIELDS_ODI_ACTUAL_FILE = Path("tests/EDIFACT_examples/SKDUPD_all_fields_ODI-actual.csv")
SKDUPD_ALL_FIELDS_POR_ACTUAL_FILE = Path("tests/EDIFACT_examples/SKDUPD_all_fields_POR-actual.csv")
SKDUPD_ALL_FIELDS_RELATION_ACTUAL_FILE = Path("tests/EDIFACT_examples/SKDUPD_all_fields_RELATION-actual.csv")
SKDUPD_ALL_FIELDS_TRAIN_ACTUAL_FILE = Path("tests/EDIFACT_examples/SKDUPD_all_fields_TRAIN-actual.csv")

SKDUPD_EXAMPLE_FILE = Path("tests/EDIFACT_examples/SKDUPD_example.r")

TSDUPD_ALL_FIELDS_FILE = Path("tests/EDIFACT_examples/TSDUPD_all_fields.r")
TSDUPD_ALL_FIELDS_META_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_all_fields_META-actual.csv")
TSDUPD_ALL_FIELDS_STOP_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_all_fields_STOP-actual.csv")
TSDUPD_ALL_FIELDS_SYNONYM_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_all_fields_SYNONYM-actual.csv")
TSDUPD_ALL_FIELDS_MCT_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_all_fields_MCT-actual.csv")
TSDUPD_ALL_FIELDS_FOOTPATH_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_all_fields_FOOTPATH-actual.csv")
TSDUPD_ALL_FIELDS_META_FILE = Path("tests/EDIFACT_examples/TSDUPD_all_fields_META.csv")
TSDUPD_ALL_FIELDS_STOP_FILE = Path("tests/EDIFACT_examples/TSDUPD_all_fields_STOP.csv")
TSDUPD_ALL_FIELDS_SYNONYM_FILE = Path("tests/EDIFACT_examples/TSDUPD_all_fields_SYNONYM.csv")
TSDUPD_ALL_FIELDS_MCT_FILE = Path("tests/EDIFACT_examples/TSDUPD_all_fields_MCT.csv")
TSDUPD_ALL_FIELDS_FOOTPATH_FILE = Path("tests/EDIFACT_examples/TSDUPD_all_fields_FOOTPATH.csv")

TSDUPD_ESCAPES_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_escapes-actual.r")
TSDUPD_ESCAPES_FILE = Path("tests/EDIFACT_examples/TSDUPD_escapes.r")
TSDUPD_ESCAPES_META_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_escapes_META-actual.csv")
TSDUPD_ESCAPES_STOP_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_escapes_STOP-actual.csv")
TSDUPD_ESCAPES_SYNONYM_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_escapes_SYNONYM-actual.csv")
TSDUPD_ESCAPES_MCT_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_escapes_MCT-actual.csv")
TSDUPD_ESCAPES_FOOTPATH_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_escapes_FOOTPATH-actual.csv")
TSDUPD_ESCAPES_META_FILE = Path("tests/EDIFACT_examples/TSDUPD_escapes_META.csv")
TSDUPD_ESCAPES_STOP_FILE = Path("tests/EDIFACT_examples/TSDUPD_escapes_STOP.csv")
TSDUPD_ESCAPES_SYNONYM_FILE = Path("tests/EDIFACT_examples/TSDUPD_escapes_SYNONYM.csv")
TSDUPD_ESCAPES_MCT_FILE = Path("tests/EDIFACT_examples/TSDUPD_escapes_MCT.csv")
TSDUPD_ESCAPES_FOOTPATH_FILE = Path("tests/EDIFACT_examples/TSDUPD_escapes_FOOTPATH.csv")

TSDUPD_V3_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_V3-actual.r")
TSDUPD_V3_FILE = Path("tests/EDIFACT_examples/TSDUPD_V3.r")
TSDUPD_V3_META_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_V3_META-actual.csv")
TSDUPD_V3_STOP_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_V3_STOP-actual.csv")
TSDUPD_V3_SYNONYM_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_V3_SYNONYM-actual.csv")
TSDUPD_V3_MCT_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_V3_MCT-actual.csv")
TSDUPD_V3_FOOTPATH_ACTUAL_FILE = Path("tests/EDIFACT_examples/TSDUPD_V3_FOOTPATH-actual.csv")
TSDUPD_V3_META_FILE = Path("tests/EDIFACT_examples/TSDUPD_V3_META.csv")
TSDUPD_V3_STOP_FILE = Path("tests/EDIFACT_examples/TSDUPD_V3_STOP.csv")
TSDUPD_V3_SYNONYM_FILE = Path("tests/EDIFACT_examples/TSDUPD_V3_SYNONYM.csv")
TSDUPD_V3_MCT_FILE = Path("tests/EDIFACT_examples/TSDUPD_V3_MCT.csv")
TSDUPD_V3_FOOTPATH_FILE = Path("tests/EDIFACT_examples/TSDUPD_V3_FOOTPATH.csv")


def load_txt(file: Path) -> str:
    with open(file, "r") as fp:
        result = fp.read()
    return result


def dump_txt(content: str, file: Path) -> None:
    with open(file, "w") as fp:
        fp.write(content)


class DataHandlerToStr(DataHandler):

    def __init__(
            self,
            do_print: bool = True,
    ):
        self._lines: List[str] = []
        self.do_print = do_print

    def on_enter_branch(self, branch: DataBranch) -> None:
        self._add_line(f'Entered branch "{branch.path}".')

    def on_exit_branch(self, path: str) -> None:
        self._add_line(f'Exited branch "{path}".')

    def on_enter_leaf(self, leaf: DataLeaf):
        self._add_line(f'Entered leaf "{leaf.path}".')
        # noinspection PyProtectedMember
        name_len = max(len(n) for n in leaf._name_2_value) if leaf._name_2_value else 1
        fmt = f'    "{{name:{name_len}}}" = "{{value}}"'
        # noinspection PyProtectedMember
        for name, value in leaf._name_2_value.items():
            self._add_line(fmt.format(name=name, value=value))

    def on_exit_leaf(self, path: str):
        self._add_line(f'Exited leaf "{path}".')

    def get_result(self) -> str:
        return "\n".join(self._lines)

    def _add_line(self, line: str):
        self._lines.append(line)
        if self.do_print:
            print(line)
