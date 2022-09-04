import abc
import sys
from enum import Enum
from typing import List, Generator, Tuple, Type, Any

if sys.version_info < (3, 8):
    import importlib_metadata as metadata
else:
    from importlib import metadata

__version__ = metadata.version("flake8_aod")


class ErrorCode(str, Enum):
    ADO001_MISSING_ITEM = "ADO001 Missing ADO item"
    ADO002_MALFORMED_ITEM_REF = "ADO002 Malformed item reference."
    ADO003_CAPITALIZATION = "ADO003 Wrong capitalization (ADO and AB must be capital)"
    ADO005_NO_TODO_REF = "ADO004 TODO needs the AOD item reference"


class Plugin:
    name = __name__
    version = __version__

    def __init__(self, tree, lines: List[str]) -> None:
        self._lines = lines

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        yield 1, 0, "AOD TEST", type(self)
