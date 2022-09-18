import sys
from typing import Generator, Tuple, Type, Any
from typing import List

from flake8_ado.ado_client import AzureDevOpsClient
from flake8_ado.checkers import SyntaxChecker, AdoChecker
from flake8_ado.domain import FailedCheck, TagAnnotatedLine
from flake8_ado.scanner import RegexMatcher

if sys.version_info < (3, 8):
    import importlib_metadata as metadata
else:
    from importlib import metadata

__version__ = metadata.version("flake8_ado")

PluginError = Tuple[int, int, str, Type[Any]]


class Plugin:
    name = __name__
    version = __version__

    def __init__(self, tree, lines: List[str]) -> None:
        self._lines = lines

    def _get_errors(self, failed_checks: List[FailedCheck]):
        for check in failed_checks:
            result = tuple([*check.as_flake8(), type(self)])
            yield result

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
            ado_client = AzureDevOpsClient(self.access_token, self.organization_url)
            ado_checker = AdoChecker(proper_reference_tags, regex_matcher, ado_client)
            ado_errors = ado_checker.check_line()
            yield from self._get_errors(ado_errors)

    @classmethod
    def add_options(cls, parser) -> None:  # type: ignore
        parser.add_option(
            "--ado-access-token",
            action="store",
            parse_from_config=True,
            comma_separated_list=False,
            help="Valid AzureDevOps token.",
        )
        parser.add_option(
            "--ado_organization_url",
            action="store",
            parse_from_config=True,
            comma_separated_list=False,
            help="AzureDevOps organization url e.g. https://dev.azure.com/foo.",
        )

    @classmethod
    def parse_options(cls, options) -> None:  # type: ignore
        cls.access_token = options.ado_access_token
        cls.organization_url = options.ado_organization_url
