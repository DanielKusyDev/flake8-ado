import sys
from typing import Generator, Tuple, Type, Any
from typing import List

from flake8_aod.checkers import SyntaxChecker, AdoChecker
from flake8_aod.domain import FailedCheck, TagAnnotatedLine
from flake8_aod.scanner import RegexMatcher

if sys.version_info < (3, 8):
    import importlib_metadata as metadata
else:
    from importlib import metadata

__version__ = metadata.version("flake8_aod")

PluginError = Tuple[int, int, str, Type[Any]]


class Plugin:
    name = __name__
    version = __version__

    def __init__(self, tree, lines: List[str]) -> None:
        self._lines = lines

    def _get_errors(self, failed_checks: List[FailedCheck]):
        for check in failed_checks:
            yield *check.as_flake8(), type(self)

    def run(self) -> Generator[PluginError, None, None]:
        proper_reference_tags = []
        regex_matcher = RegexMatcher()
        for line, line_num, tag in regex_matcher.get_lines_with_annotated_comments(self._lines):
            annotated_line = TagAnnotatedLine(line=line, line_num=line_num, tag=tag)
            syntax_errors = SyntaxChecker(annotated_line, regex_matcher).check_line()
            yield from self._get_errors(syntax_errors)
            if not any([error.critical for error in syntax_errors]):
                proper_reference_tags.append(annotated_line)
        if proper_reference_tags:
            ado_checker = AdoChecker(proper_reference_tags, regex_matcher)
            ado_errors = ado_checker.check_line()
            yield from self._get_errors(ado_errors)
