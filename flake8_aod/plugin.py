import abc
import sys
from dataclasses import dataclass
from enum import Enum
from typing import List, Generator, Tuple, Type, Any, Optional

if sys.version_info < (3, 8):
    import importlib_metadata as metadata
else:
    from importlib import metadata

__version__ = metadata.version("flake8_aod")

PluginError = Tuple[int, int, str, Type[Any]]


class ErrorCode(str, Enum):
    ADO001_MISSING_ITEM = "ADO001 Missing ADO item"
    ADO002_MALFORMED_ITEM_REF = "ADO002 Malformed item reference"
    ADO003_CAPITALIZATION = "ADO003 Wrong capitalization (ADO and AB must be capital)"
    ADO005_NO_TODO_REF = "ADO004 TODO needs the AOD item reference"


@dataclass(frozen=True)
class FailedCheck:
    line: int
    match_col: int
    line_num: str
    code: ErrorCode
    critical: bool = False


class Checker(abc.ABC):
    @abc.abstractmethod
    def check_line(self, line: str, line_num: int) -> FailedCheck:
        raise NotImplementedError


class SyntaxChecker(Checker):
    def check_line(self, line: str, line_num: int) -> FailedCheck:
        pass


class ADOChecker(Checker):
    def check_line(self, line: str, line_num: int) -> FailedCheck:
        pass


class Plugin:
    name = __name__
    version = __version__

    def __init__(self, tree, lines: List[str]) -> None:
        self._lines = lines
        self._syntax_checker = SyntaxChecker()
        self._ado_checker = ADOChecker()

    def _get_error(self, failed_check: FailedCheck) -> PluginError:
        return failed_check.line, failed_check.match_col, failed_check.code.value, type(self)

    def run(self) -> Generator[PluginError, None, None]:
        for i, line in enumerate(self._lines):
            syntax_error = self._syntax_checker.check_line(line, i)
            if syntax_error:
                yield from self._get_error(syntax_error)
            if not syntax_error or not syntax_error.critical:
                ado_error = self._ado_checker.check_line(line, i)
                if ado_error:
                    yield from self._get_error(ado_error)
