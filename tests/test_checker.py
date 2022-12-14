# flake8: noqa
from typing import Set, List

import pytest
from pytest_mock import MockFixture

from flake8_ado import Plugin
from flake8_ado.domain import ErrorCode


def lint_(input_: str) -> Set[str]:
    plugin = Plugin(None, input_.split("\n"))
    plugin.organization_url = ""  # calling Plugin.run() won't trigger option parsing
    plugin.access_token = ""
    return {f"{line_num}: {col_num} {msg}" for line_num, col_num, msg, _ in plugin.run()}


_MISSING = "123345"
_EXISTING = "998877"
_ADO_TAG_OFFSET = len(" # ADO: ")
_TODO_TAG_OFFSET = len(" # TODO: ")
_CODE_OVER_COMMENTS = [
    "foo = 1",
    (
        # fmt: off
            "class FooClass:\n" 
            "    def foo() -> None:\n"
            "        pass"
        # fmt: on
    ),
]


class ADOClientStub:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def get_not_existing_item_ids(self, ids: List[str]) -> List[str]:
        return [_MISSING] if _MISSING in ids else []


@pytest.fixture(autouse=True)
def mock_ado_client(mocker: MockFixture) -> None:
    mocker.patch("flake8_ado.plugin.AzureDevOpsClient", new=ADOClientStub)


@pytest.mark.parametrize("code", _CODE_OVER_COMMENTS)
@pytest.mark.parametrize(
    "errors, comment, column_of_error_offset",
    [
        ([ErrorCode.ADO001_MISSING_ITEM], f"# ADO: AB#{_MISSING} See the ticket", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO002_MALFORMED_ITEM_REF], "# ADO: AB: 1234567 See the ticket", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO002_MALFORMED_ITEM_REF], "# ADO: #1234567 See the ticket", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO002_MALFORMED_ITEM_REF], "# ADO: ab 1234567 See the ticket", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO002_MALFORMED_ITEM_REF], "# ADO: 1234567 See the ticket", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO002_MALFORMED_ITEM_REF], "# ADO: I forgot the number", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO002_MALFORMED_ITEM_REF], "# ADO: Fix this", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO002_MALFORMED_ITEM_REF], "# ADO: AB123444", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO002_MALFORMED_ITEM_REF], "# ADO: ab123444", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO002_MALFORMED_ITEM_REF], "# ADO: ABblahblah", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO002_MALFORMED_ITEM_REF], "# ADO: abblahblah", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO002_MALFORMED_ITEM_REF], "# ADO: AB#998877dasdasd", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO003_CAPITALIZATION], f"# ado: AB#{_EXISTING}", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO003_CAPITALIZATION], f"# ADO: ab#{_EXISTING}", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO003_CAPITALIZATION], f"# ado: ab#{_EXISTING}", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO003_CAPITALIZATION, ErrorCode.ADO001_MISSING_ITEM], f"# ado: ab#{_MISSING}", _ADO_TAG_OFFSET),
        ([ErrorCode.ADO005_NO_TODO_REF], "# TODO: someone fix this please", _TODO_TAG_OFFSET),
    ],
)
def test_plugin_with_errors(errors: List[ErrorCode], comment: str, code: str, column_of_error_offset: int):
    code_line_by_line = code.split("\n")
    for line_number in range(len(code_line_by_line)):
        lines = code_line_by_line.copy()
        original_line = lines[line_number]
        lines[line_number] += f" {comment}"
        code_to_analyse = "\n".join(lines)
        linting_result = lint_(code_to_analyse)
        column = len(original_line) + column_of_error_offset
        expected = {f"{line_number + 1}: {column} {e.value}" for e in errors}
        assert linting_result == expected


@pytest.mark.parametrize("code", _CODE_OVER_COMMENTS)
@pytest.mark.parametrize(
    "comment",
    [
        f"# ADO: AB#{_EXISTING} See the ticket",
        f"# TODO AB#{_EXISTING} Something",
        f"# TODO AB#{_EXISTING}",
        f"# This needs to be fixed, todo AB#{_EXISTING}",
        "# todo someone fix this please",
        "# fix it please todo",
        "# tOdO",
    ],
)
def test_plugin_with_proper_code(code: str, comment: str) -> None:
    assert lint_(comment) == set()
