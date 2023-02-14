import dataclasses
from pathlib import Path
from typing import Callable, Optional, List, Union

from merits import common
from merits.cmd.arg_definition import (
    Arguments,
    CONVERSION_SKDUPD_CSV_EDIFACT,
    CONVERSION_SKDUPD_EDIFACT_CSV,
    CONVERSION_TSDUPD_CSV_EDIFACT,
    CONVERSION_TSDUPD_EDIFACT_CSV,
    CONVERSION_SKDUPD_CSV_EDIFACT_MULTI,
    CONVERSION_SKDUPD_EDIFACT_CSV_MULTI,
    CONVERSION_TSDUPD_CSV_EDIFACT_MULTI,
    CONVERSION_TSDUPD_EDIFACT_CSV_MULTI,
)
from merits.csvs_zip.rows import RowsFactory
from merits.exceptions import MeritsException
from merits.skdupd import definition as skdupd_definition
from merits.skdupd.csvs_to_edifact import CsvsToEdifact as SkdupdCsvsToEdifact
from merits.skdupd.edifact_to_csvs import EdifactToCsvs as SkdupdEdifactToCsv
from merits.tsdupd import definition as tsdupd_definition
from merits.tsdupd.csvs_to_edifact import CsvsToEdifact as TsdupdCsvsToEdifact
from merits.tsdupd.edifact_to_csvs import EdifactToCsvs as TsdupdEdifactToCsv

logger = common.get_logger(__file__)


class Worker(object):

    def __init__(
            self,
            arguments: Arguments,
            print_function: Optional[Callable] = None,
    ):
        """

        :param arguments: the command line arguments
        :param print_function: optional function to print messages on the command line. If None messages only go to the
        logger.
        """
        self.arguments = arguments
        self._print_function = print_function

    def run(self) -> None:
        conversion = self.arguments.conversion
        conversion_2_method = {
            CONVERSION_SKDUPD_CSV_EDIFACT: self._skdupd_csv_edifact,
            CONVERSION_SKDUPD_EDIFACT_CSV: self._skdupd_edifact_csv,
            CONVERSION_TSDUPD_CSV_EDIFACT: self._tsdupd_csv_edifact,
            CONVERSION_TSDUPD_EDIFACT_CSV: self._tsdupd_edifact_csv,
            CONVERSION_SKDUPD_CSV_EDIFACT_MULTI: self._skdupd_csv_edifact_multi,
            CONVERSION_SKDUPD_EDIFACT_CSV_MULTI: self._skdupd_edifact_csv_multi,
            CONVERSION_TSDUPD_CSV_EDIFACT_MULTI: self._tsdupd_csv_edifact_multi,
            CONVERSION_TSDUPD_EDIFACT_CSV_MULTI: self._tsdupd_edifact_csv_multi,
        }
        method = conversion_2_method.get(conversion)
        if method:
            method()
        else:
            self._print(
                f'Sorry conversion {conversion} is not available in this version.'
            )

    def _skdupd_csv_edifact_multi(self):
        self._csv_edifact_multi(self._skdupd_csv_edifact)

    def _tsdupd_csv_edifact_multi(self):
        self._csv_edifact_multi(self._tsdupd_csv_edifact)

    def _csv_edifact_multi(
            self,
            target_method: Callable,
    ):
        if self.arguments.input:
            input_dir = self.arguments.input
        else:
            input_dir = Path()
        if self.arguments.output:
            output_dir = self.arguments.output
        else:
            output_dir = Path()
        if not input_dir.is_dir():
            raise MeritsException(
                f'Input should be a directory: "{input_dir.resolve()}".'
            )
        if output_dir.is_file():
            raise MeritsException(
                f'Output should be a directory: "{output_dir.resolve()}".'
            )
        args_dict = {
            k: v
            for k, v in dataclasses.asdict(self.arguments).items()
            if k not in ("input", "output")
        }
        if self.arguments.csv_zip:
            for input_file in input_dir.glob("*.zip"):
                output_file = output_dir / input_file.with_suffix(".r").name
                arguments = Arguments(
                    input=input_file,
                    output=output_file,
                    **args_dict,
                )
                target_method(arguments)
        else:
            for input_sub_dir in input_dir.iterdir():
                if not input_sub_dir.is_dir():
                    continue
                output_file = output_dir / (input_sub_dir.name + ".r")
                arguments = Arguments(
                    input=input_sub_dir,
                    output=output_file,
                    **args_dict,
                )
                target_method(arguments)

    def _skdupd_edifact_csv_multi(self):
        self._edifact_csv_multi(self._skdupd_edifact_csv)

    def _tsdupd_edifact_csv_multi(self):
        self._edifact_csv_multi(self._tsdupd_edifact_csv)

    def _edifact_csv_multi(
            self,
            target_method: Callable,
    ):
        if self.arguments.input:
            input_dir = self.arguments.input
        else:
            input_dir = Path()
        if self.arguments.output:
            output_dir = self.arguments.output
        else:
            output_dir = Path()
        if not input_dir.is_dir():
            raise MeritsException(
                f'Input should be a directory: "{input_dir.resolve()}".'
            )
        if output_dir.is_file():
            raise MeritsException(
                f'Output should be a directory: "{output_dir.resolve()}".'
            )
        args_dict = {
            k: v
            for k, v in dataclasses.asdict(self.arguments).items()
            if k not in ("input", "output", "csv_file_name_2_next_id")
        }
        csv_file_name_2_next_id = self.arguments.csv_file_name_2_next_id
        for input_file in input_dir.glob("*.r"):
            if self.arguments.csv_zip:
                output_file = output_dir / input_file.with_suffix(".zip").name
                arguments = Arguments(
                    input=input_file,
                    output=output_file,
                    csv_file_name_2_next_id=csv_file_name_2_next_id,
                    **args_dict,
                )
            else:
                output_sub_dir = output_dir / input_file.stem
                arguments = Arguments(
                    input=input_file,
                    output=output_sub_dir,
                    csv_file_name_2_next_id=csv_file_name_2_next_id,
                    **args_dict,
                )
            target_method(arguments)
            csv_file_name_2_next_id = arguments.csv_file_name_2_next_id

    def _skdupd_csv_edifact(
            self,
            arguments: Optional[Arguments] = None,
    ):
        if arguments is None:
            arguments = self.arguments
        if arguments.csv_zip:
            default_input = Path(skdupd_definition.CSV_ZIP_FILE_NAME)
        else:
            default_input = Path()
        self._csv_edifact(
            source=self._with_default(arguments.input, default_input),
            destination=self._with_default(arguments.output, Path(skdupd_definition.EDIFACT_FILE_NAME)),
            conversion_name=CONVERSION_SKDUPD_CSV_EDIFACT,
            name_pass_filter=[
                skdupd_definition.META_FILE_NAME,
                skdupd_definition.ODI_FILE_NAME,
                skdupd_definition.RELATION_FILE_NAME,
                skdupd_definition.POR_FILE_NAME,
                skdupd_definition.TRAIN_FILE_NAME,
            ],
            convertor=SkdupdCsvsToEdifact(),
        )

    def _tsdupd_csv_edifact(
            self,
            arguments: Optional[Arguments] = None,
    ):
        if arguments is None:
            arguments = self.arguments
        if arguments.csv_zip:
            default_input = Path(tsdupd_definition.CSV_ZIP_FILE_NAME)
        else:
            default_input = Path()
        self._csv_edifact(
            source=self._with_default(arguments.input, default_input),
            destination=self._with_default(arguments.output, Path(tsdupd_definition.EDIFACT_FILE_NAME)),
            conversion_name=CONVERSION_TSDUPD_CSV_EDIFACT,
            name_pass_filter=[
                tsdupd_definition.META_FILE_NAME,
                tsdupd_definition.STOP_FILE_NAME,
                tsdupd_definition.SYNONYM_FILE_NAME,
                tsdupd_definition.MCT_FILE_NAME,
                tsdupd_definition.FOOTPATH_FILE_NAME,
            ],
            convertor=TsdupdCsvsToEdifact(),
        )

    def _skdupd_edifact_csv(
            self,
            arguments: Optional[Arguments] = None,
    ):
        if arguments is None:
            arguments = self.arguments
        if arguments.csv_zip:
            default_output = Path(skdupd_definition.CSV_ZIP_FILE_NAME)
        else:
            default_output = Path()
        convertor = SkdupdEdifactToCsv()
        if arguments.csv_file_name_2_next_id:
            convertor.set_csv_file_name_2_next_id(arguments.csv_file_name_2_next_id)
        self._edifact_csv(
            source=self._with_default(arguments.input, Path(skdupd_definition.EDIFACT_FILE_NAME)),
            destination=self._with_default(arguments.output, default_output),
            conversion_name=CONVERSION_SKDUPD_EDIFACT_CSV,
            convertor=convertor,
        )
        arguments.csv_file_name_2_next_id = convertor.get_csv_file_name_2_next_id()

    def _tsdupd_edifact_csv(
            self,
            arguments: Optional[Arguments] = None,
    ):
        if arguments is None:
            arguments = self.arguments
        if arguments.csv_zip:
            default_output = Path(tsdupd_definition.CSV_ZIP_FILE_NAME)
        else:
            default_output = Path()
        convertor = TsdupdEdifactToCsv()
        if arguments.csv_file_name_2_next_id:
            convertor.set_csv_file_name_2_next_id(arguments.csv_file_name_2_next_id)
        self._edifact_csv(
            source=self._with_default(arguments.input, Path(tsdupd_definition.EDIFACT_FILE_NAME)),
            destination=self._with_default(arguments.output, default_output),
            conversion_name=CONVERSION_TSDUPD_EDIFACT_CSV,
            convertor=convertor,
        )
        arguments.csv_file_name_2_next_id = convertor.get_csv_file_name_2_next_id()

    def _edifact_csv(
            self,
            source: Path,
            destination: Path,
            conversion_name: str,
            convertor: Union[SkdupdEdifactToCsv, TsdupdEdifactToCsv],
    ):
        self._print(f'Running {conversion_name}.')
        self._print(
            f'Reading source file from "{source.resolve()}".'
        )
        with open(source, "r") as f:
            edifact_segments = f.read().splitlines(keepends=False)
        is_csv_zip = self.arguments.csv_zip
        if destination.is_file() and not is_csv_zip:
            raise MeritsException(
                f'The output, "{destination.resolve()}" is an existing file but a directory was expected.'
            )
        if is_csv_zip:
            destination_directory = destination.parent
        else:
            destination_directory = destination
        if not destination_directory.is_dir():
            self._print(
                f'Creating destination directory "{destination_directory.resolve()}".'
            )
            destination_directory.mkdir(parents=True)

        self._print(
            f'Starting conversion.'
        )
        convertor.load(edifact_segments=edifact_segments)

        if is_csv_zip:
            self._print(
                f'Writing to ZIP destination "{destination.resolve()}".'
            )
            with open(destination, "wb") as f:
                f.write(convertor.get_zip())
        else:
            csv_file_name_2_content = convertor.get_csvs()
            for csv_file_name, content in csv_file_name_2_content.items():
                file = destination / csv_file_name
                self._print(
                    f'Writing destination file "{file.resolve()}".'
                )
                with open(file, "w") as f:
                    f.write(content)
        self._print(f"Finished {conversion_name}.")

    def _csv_edifact(
            self,
            source: Path,
            destination: Path,
            conversion_name: str,
            name_pass_filter: List[str],
            convertor: Union[SkdupdCsvsToEdifact, TsdupdCsvsToEdifact],
    ):
        self._print(f'Running {conversion_name}.')
        is_csv_zip = self.arguments.csv_zip
        if is_csv_zip:
            self._print(
                f'Reading source files from ZIP "{source.resolve()}".'
            )
            csv_file_name_2_rows = RowsFactory.from_zip(
                zipped=source,
            )
        else:
            self._print(
                f'Reading source files from directory "{source.resolve()}".'
            )
            csv_file_name_2_rows = RowsFactory.from_directory(
                directory=source,
                name_pass_filter=name_pass_filter,
            )
        if not destination.parent.is_dir():
            self._print(
                f'Creating destination directory "{destination.parent.resolve()}".'
            )
            destination.parent.mkdir(parents=True)

        self._print(
            f'Starting conversion.'
        )
        convertor.load(csv_file_name_2_rows=csv_file_name_2_rows)
        edifact: str = convertor.get()

        self._print(
            f'Writing to destination "{destination.resolve()}".'
        )
        with open(destination, "w") as f:
            f.write(edifact)
        self._print(f"Finished {conversion_name}.")

    def _print(self, s):
        logger.info(s)
        if self._print_function:
            self._print_function(s)

    @staticmethod
    def _with_default(value, default):
        if value:
            return value
        return default
