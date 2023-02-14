import dataclasses
import logging
import sys
from datetime import datetime

from merits import common
from merits.cmd.arg_definition import (
    get_argument_parser,
    Arguments,
    CONVERSION_SKDUPD_EDIFACT_CSV,
    CONVERSION_SKDUPD_CSV_EDIFACT,
    CONVERSION_TSDUPD_EDIFACT_CSV,
    CONVERSION_TSDUPD_CSV_EDIFACT,
    CONVERSION_SKDUPD_EDIFACT_CSV_MULTI,
    CONVERSION_SKDUPD_CSV_EDIFACT_MULTI,
    CONVERSION_TSDUPD_EDIFACT_CSV_MULTI,
    CONVERSION_TSDUPD_CSV_EDIFACT_MULTI,
)
from merits.cmd.worker import Worker
from merits.exceptions import MeritsException

LOG_FILE_NAME = 'merits-convert.log'
logging.basicConfig(
    filename=LOG_FILE_NAME,
    format="%(asctime)s %(levelname)s %(name)s  %(message)s",
    encoding='utf-8',
    level=logging.DEBUG,
)

logger = common.get_logger(__file__)


def main() -> None:
    """
    Wraps the _main function to gracefully handle some exceptions that are related to user input validation.
    :return:
    """
    try:
        _main()
    except (MeritsException, FileNotFoundError) as e:
        logger.exception(e)
        _print(
            f"Aborting operation due to error: {e}"
            f"\nSee the log file {LOG_FILE_NAME} for technical details."
        )


def _main():
    """
    Does all the work described as the `merits-convert` executable.
    :return:
    """
    parser = get_argument_parser()
    args = parser.parse_args()
    arguments = Arguments(**vars(args))
    _print(
        "Arguments:\n"
        + "\n".join(
            f"    {k} = {v}"
            for k, v in dataclasses.asdict(arguments).items()
        )
    )
    worker = Worker(
        arguments=arguments,
        print_function=_print,
    )
    worker.run()


def skdupd_2_csv():
    sys.argv.insert(1, CONVERSION_SKDUPD_EDIFACT_CSV)
    main()


def csv_2_skdupd():
    sys.argv.insert(1, CONVERSION_SKDUPD_CSV_EDIFACT)
    main()


def tsdupd_2_csv():
    sys.argv.insert(1, CONVERSION_TSDUPD_EDIFACT_CSV)
    main()


def csv_2_tsdupd():
    sys.argv.insert(1, CONVERSION_TSDUPD_CSV_EDIFACT)
    main()


def skdupd_2_csv_multi():
    sys.argv.insert(1, CONVERSION_SKDUPD_EDIFACT_CSV_MULTI)
    main()


def csv_2_skdupd_multi():
    sys.argv.insert(1, CONVERSION_SKDUPD_CSV_EDIFACT_MULTI)
    main()


def tsdupd_2_csv_multi():
    sys.argv.insert(1, CONVERSION_TSDUPD_EDIFACT_CSV_MULTI)
    main()


def csv_2_tsdupd_multi():
    sys.argv.insert(1, CONVERSION_TSDUPD_CSV_EDIFACT_MULTI)
    main()


def _print(s: str):
    """
    Prints to the command line with some wrapping format.
    :param s:
    :return:
    """
    print(
        f"{datetime.now():%Y-%m-%dT%H:%M:%S.%f} {s}"
    )


if __name__ == '__main__':
    main()
