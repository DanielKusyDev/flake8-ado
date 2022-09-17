import abc
import re
import sys
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache

from typing import List, Generator, Tuple, Type, Any, Optional, Set

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


class RegexMatcher:
    def __init__(self, tag: str) -> None:
        self._reference_pattern = re.compile(rf"# {tag}AB#(\d+)(\s|.$)", flags=re.IGNORECASE)
        self._tag_pattern = re.compile(rf"# {tag}", flags=re.IGNORECASE)

    @lru_cache
    def get_reference_match(self, line: str) -> re.Match:
        return re.search(self._reference_pattern, line)

    @lru_cache
    def get_tag_match(self, line: str) -> re.Match:
        return re.search(self._tag_pattern, line)


class Validator(abc.ABC):
    @abc.abstractmethod
    def validate(self, line: str, line_num: int) -> Optional[FailedCheck]:
        raise NotImplementedError


class RegexValidator(Validator, abc.ABC):
    def __init__(self, tag: str, matcher: RegexMatcher) -> None:
        self._tag = tag
        self._matcher = matcher


class ReferenceValidator(RegexValidator):
    def validate(self, line: str, line_num: int) -> Optional[FailedCheck]:
        reference_match = self._matcher.get_reference_match(line)
        tag_match = self._matcher.get_tag_match(line)
        if not reference_match:
            code = ErrorCode.ADO005_NO_TODO_REF if "todo" in self._tag.lower() else ErrorCode.ADO002_MALFORMED_ITEM_REF
            return FailedCheck(line=line, match_col=tag_match.regs[0][-1], line_num=line_num, code=code, critical=True)


class CapitalizationValidator(RegexValidator):
    def validate(self, line: str, line_num: int) -> Optional[FailedCheck]:
        reference_match = self._matcher.get_reference_match(line)
        tag_match = self._matcher.get_tag_match(line)
        if not reference_match[0].isupper():
            return FailedCheck(
                line=line,
                match_col=tag_match.regs[0][-1],
                line_num=line_num,
                code=ErrorCode.ADO003_CAPITALIZATION,
                critical=False,
            )


class Checker(abc.ABC):
    @abc.abstractmethod
    def check_line(self, line: str, line_num: int) -> List[FailedCheck]:
        raise NotImplementedError


class SyntaxChecker(Checker):
    def __init__(self) -> None:
        self._main_pattern = re.compile(r"# (ado: )|(todo: )", flags=re.IGNORECASE)

    def _get_tags(self, line: str) -> Set[str]:
        main_tags_match = self._main_pattern.findall(line)
        return {part.lower() for match in main_tags_match for part in match if part}

    def check_line(self, line: str, line_num: int) -> List[FailedCheck]:
        checks = []
        line_num += 1
        for tag in self._get_tags(line):
            matcher = RegexMatcher(tag)
            validators = [ReferenceValidator(tag, matcher), CapitalizationValidator(tag, matcher)]
            for validator in validators:
                check = validator.validate(line, line_num)
                if check:
                    checks.append(check)
                    if check.critical:
                        break
        return checks


class ADOChecker(Checker):
    def check_line(self, line: str, line_num: int) -> List[FailedCheck]:
        pass


class Plugin:
    name = __name__
    version = __version__

    def __init__(self, tree, lines: List[str]) -> None:
        self._lines = lines
        self._syntax_checker = SyntaxChecker()
        self._ado_checker = ADOChecker()

    def _get_errors(self, failed_checks: List[FailedCheck]):
        for check in failed_checks:
            yield check.line_num, check.match_col, check.code.value, type(self)

    def run(self) -> Generator[PluginError, None, None]:
        for i, line in enumerate(self._lines):
            syntax_errors = self._syntax_checker.check_line(line, i)
            if syntax_errors:
                yield from self._get_errors(syntax_errors)
