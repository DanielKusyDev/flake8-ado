import abc
import re
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
    line: str
    match_col: int
    line_num: int
    code: ErrorCode
    critical: bool = False


class Checker(abc.ABC):
    @abc.abstractmethod
    def check_line(self, line: str, line_num: int) -> Optional[FailedCheck]:
        raise NotImplementedError


class SyntaxChecker(Checker):
    def __init__(self) -> None:
        self._main_pattern = re.compile(r"# (ado: )|(\stodo:)", flags=re.IGNORECASE)

    def check_line(self, line: str, line_num: int) -> Optional[FailedCheck]:
        regex_result = self._main_pattern.findall(line)
        line_num += 1
        if regex_result:
            tags = {part.lower() for match in regex_result for part in match if part}
            for tag in tags:
                reference_pattern = re.compile(rf"{tag}AB#(\d+)(\s|.$)", flags=re.IGNORECASE)
                ado_pattern = re.compile(r"# ADO: ", flags=re.IGNORECASE)
                number_match = re.search(reference_pattern, line)
                ado_match = re.search(ado_pattern, line)
                if not number_match:

                    return FailedCheck(
                        line=line,
                        match_col=ado_match.regs[0][-1],
                        line_num=line_num,
                        code=ErrorCode.ADO002_MALFORMED_ITEM_REF,
                        critical=True,
                    )
                if not number_match[0].isupper():
                    return FailedCheck(
                        line=line,
                        match_col=ado_match.regs[0][-1],
                        line_num=line_num,
                        code=ErrorCode.ADO003_CAPITALIZATION,
                        critical=False,
                    )


class ADOChecker(Checker):
    def check_line(self, line: str, line_num: int) -> Optional[FailedCheck]:
        pass


class Plugin:
    name = __name__
    version = __version__

    def __init__(self, tree, lines: List[str]) -> None:
        self._lines = lines
        self._syntax_checker = SyntaxChecker()
        self._ado_checker = ADOChecker()

    def _get_error(self, failed_check: FailedCheck) -> PluginError:
        yield failed_check.line_num, failed_check.match_col, failed_check.code.value, type(self)

    def run(self) -> Generator[PluginError, None, None]:
        for i, line in enumerate(self._lines):
            syntax_error = self._syntax_checker.check_line(line, i)
            if syntax_error:
                yield from self._get_error(syntax_error)
