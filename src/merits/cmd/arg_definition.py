from argparse import ArgumentParser, BooleanOptionalAction, Action
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict

from merits.skdupd import definition as skdupd_definition
from merits.tsdupd import definition as tsdupd_definition

# CONVERSION_* are possible values for the `conversion` argument.
CONVERSION_SKDUPD_CSV_EDIFACT = "skdupd-csv-edifact"
CONVERSION_SKDUPD_EDIFACT_CSV = "skdupd-edifact-csv"
CONVERSION_TSDUPD_CSV_EDIFACT = "tsdupd-csv-edifact"
CONVERSION_TSDUPD_EDIFACT_CSV = "tsdupd-edifact-csv"
CONVERSION_SKDUPD_CSV_EDIFACT_MULTI = "skdupd-csv-edifact-multi"
CONVERSION_SKDUPD_EDIFACT_CSV_MULTI = "skdupd-edifact-csv-multi"
CONVERSION_TSDUPD_CSV_EDIFACT_MULTI = "tsdupd-csv-edifact-multi"
CONVERSION_TSDUPD_EDIFACT_CSV_MULTI = "tsdupd-edifact-csv-multi"

CONVERSIONS = [
    CONVERSION_SKDUPD_CSV_EDIFACT,
    CONVERSION_SKDUPD_EDIFACT_CSV,
    CONVERSION_TSDUPD_CSV_EDIFACT,
    CONVERSION_TSDUPD_EDIFACT_CSV,
    CONVERSION_SKDUPD_CSV_EDIFACT_MULTI,
    CONVERSION_SKDUPD_EDIFACT_CSV_MULTI,
    CONVERSION_TSDUPD_CSV_EDIFACT_MULTI,
    CONVERSION_TSDUPD_EDIFACT_CSV_MULTI,
]


@dataclass
class Arguments:
    """
    An object representation of the command line arguments. This allows auto-completion and prevent typos in code that
    uses the arguments. For field definitions read the README.md file in the cmd package.
    """
    conversion: str
    csv_zip: bool
    input: Optional[Path] = None
    output: Optional[Path] = None
    csv_file_name_2_next_id: Optional[Dict[str, int]] = None


class DictAction(Action):

    """
    This class parses an argument of form `--my-dict-option key1=value1 key2=value2 key-n=value-n` into a dict.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        parsed = {}
        for value in values:
            key, value = value.split('=')
            parsed[key] = self.value_action(value)
        setattr(namespace, self.dest, parsed)

    # noinspection PyMethodMayBeStatic
    def value_action(self, value):
        return value


class DictIntAction(DictAction):
    # noinspection PyMethodMayBeStatic
    def value_action(self, value):
        return int(value)


def get_argument_parser() -> ArgumentParser:
    """
    Gives a parser for the sys.argv.
    :return:
    """
    parser = ArgumentParser(
        prog="merits-convert",
        description=f"""This program converts MERITS files between CSV and EDIFACT.
       
The first argument must be one of the conversions {CONVERSIONS}.
 
Without further arguments this works on the current directory with the default file names. For SKDUPD these are
{skdupd_definition.EDIFACT_FILE_NAME}, {skdupd_definition.META_FILE_NAME}, {skdupd_definition.TRAIN_FILE_NAME},
{skdupd_definition.POR_FILE_NAME}, {skdupd_definition.RELATION_FILE_NAME}, and {skdupd_definition.ODI_FILE_NAME}.
The defaults for TSDUPD are {tsdupd_definition.EDIFACT_FILE_NAME}, {tsdupd_definition.META_FILE_NAME}, 
{tsdupd_definition.STOP_FILE_NAME}, {tsdupd_definition.SYNONYM_FILE_NAME}, {tsdupd_definition.MCT_FILE_NAME}, and 
{tsdupd_definition.FOOTPATH_FILE_NAME}.
""",
    )
    parser.add_argument(
        "conversion",
        choices=CONVERSIONS,
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=None,
        help="The source ZIP file, EDIFACT file, or directory. Defaults to current directory and default file names.",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="The destination ZIP file, EDIFACT file, or directory. Defaults to current directory and default file"
             " names.",
    )
    parser.add_argument(
        "--csv-zip", "-z",
        type=bool,
        action=BooleanOptionalAction,
        help="If set, the CSV files will be written/read as a ZIP file per EDIFACT file."
    )
    parser.add_argument(
        "--csv-id",
        dest="csv_file_name_2_next_id",
        nargs="*",
        action=DictIntAction,
        help="Sets the first ID's in created CSV files. Example --csv-id SKDUPD_TRAIN.csv=12 SKDUPD_POR.csv=3456"
    )

    return parser
