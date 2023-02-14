import logging
from pathlib import Path
import merits

_MERITS_ROOT = Path(merits.__file__).parent.parent


def get_logger(file: str) -> logging.Logger:
    """
    Gets a logger with a name made up of the first characters of the packages, and the full module name.
    For example file "./src/merits/cmd/main.py" would result in name "m.c.main"
    :param file: the __file__ value from module that wants a logger.
    :return:
    """
    relative_path = Path(file)
    try:
        relative_path = relative_path.relative_to(_MERITS_ROOT)
    except ValueError as e:
        print(f"m.common WARNING: Using absolute path: {e}.")
    prefix = ".".join(
        p.name[0]
        for p in reversed(relative_path.parents)
        if p.name
    )
    name = f"{prefix}.{relative_path.stem}"
    logger = logging.getLogger(name)
    return logger
