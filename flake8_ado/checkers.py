import abc
from typing import List

from flake8_ado.ado_client import AzureDevOpsClient
from flake8_ado.domain import FailedCheck, TagAnnotatedLine
from flake8_ado.scanner import RegexMatcher
from flake8_ado.validators import CapitalizationValidator, ReferenceValidator, DevOpsItemValidator


class Checker(abc.ABC):
    @abc.abstractmethod
    def check_line(self) -> List[FailedCheck]:
        raise NotImplementedError


class SyntaxChecker(Checker):
    def __init__(self, annotated_line: TagAnnotatedLine, regex_matcher: RegexMatcher) -> None:
        self._annotated_line = annotated_line
        self._regex_matcher = regex_matcher

    def check_line(self) -> List[FailedCheck]:
        checks = []
        validators = [
            ReferenceValidator(self._annotated_line, self._regex_matcher),
            CapitalizationValidator(self._annotated_line, self._regex_matcher),
        ]
        for validator in validators:
            for check in validator.validate():
                checks.append(check)
                if check.critical:
                    break
            else:
                continue
            break
        return checks


class AdoChecker(Checker):
    def __init__(
        self, annotated_lines: List[TagAnnotatedLine], regex_matcher: RegexMatcher, ado_client: AzureDevOpsClient
    ) -> None:
        self._lines = {}
        self._regex_matcher = regex_matcher
        for line_with_tag in annotated_lines:
            id_ = self._regex_matcher.get_reference_number(line_with_tag.line)
            self._lines[id_] = line_with_tag
        self._ado_client = ado_client

    def check_line(self) -> List[FailedCheck]:
        validator = DevOpsItemValidator(self._lines, self._regex_matcher, self._ado_client)
        return [check for check in validator.validate()]
