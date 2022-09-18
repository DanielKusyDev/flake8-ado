import abc
from typing import Dict, Iterator

from flake8_ado.ado_client import AzureDevOpsClient
from flake8_ado.domain import FailedCheck, ErrorCode, TagAnnotatedLine
from flake8_ado.scanner import RegexMatcher


class Validator(abc.ABC):
    @abc.abstractmethod
    def validate(self) -> Iterator[FailedCheck]:
        raise NotImplementedError


class RegexValidator(Validator, abc.ABC):
    def __init__(self, annotated_line: TagAnnotatedLine, matcher: RegexMatcher) -> None:
        self._annotated_line = annotated_line
        self._matcher = matcher


class ReferenceValidator(RegexValidator):
    def validate(self) -> Iterator[FailedCheck]:
        reference_match = self._matcher.get_reference_match(self._annotated_line.line, self._annotated_line.tag)
        tag_match = self._matcher.get_tag_match(self._annotated_line.line, self._annotated_line.tag)
        if not reference_match:
            code = (
                ErrorCode.ADO005_NO_TODO_REF
                if "todo" in self._annotated_line.tag.lower()
                else ErrorCode.ADO002_MALFORMED_ITEM_REF
            )
            yield FailedCheck(
                line=self._annotated_line.line,
                match_col=tag_match.regs[0][-1],
                line_num=self._annotated_line.line_num,
                code=code,
                critical=True,
            )


class CapitalizationValidator(RegexValidator):
    def validate(self) -> Iterator[FailedCheck]:
        reference_match = self._matcher.get_reference_match(self._annotated_line.line, self._annotated_line.tag)
        tag_match = self._matcher.get_tag_match(self._annotated_line.line, self._annotated_line.tag)
        if not reference_match[0].isupper():
            yield FailedCheck(
                line=self._annotated_line.line,
                match_col=tag_match.regs[0][-1],
                line_num=self._annotated_line.line_num,
                code=ErrorCode.ADO003_CAPITALIZATION,
                critical=False,
            )


class DevOpsItemValidator(Validator):
    def __init__(self, lines: Dict[str, TagAnnotatedLine], matcher: RegexMatcher) -> None:
        self._ado_client = AzureDevOpsClient()
        self._lines = lines
        self._regex_matcher = matcher

    def validate(self) -> Iterator[FailedCheck]:
        for not_existing_id in self._ado_client.get_not_existing_item_ids(list(self._lines)):
            item = self._lines[not_existing_id]
            column = self._regex_matcher.get_tag_match(item.line, item.tag).regs[0][-1]
            yield FailedCheck(
                line=item.line,
                match_col=column,
                line_num=item.line_num,
                code=ErrorCode.ADO001_MISSING_ITEM,
                critical=True,
            )
