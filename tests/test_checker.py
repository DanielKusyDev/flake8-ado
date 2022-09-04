from typing import Set

import pytest

from flake8_aod import Plugin
from flake8_aod.plugin import ErrorCode


def lint_(input_: str) -> Set[str]:
    plugin = Plugin(None, input_.split("\n"))
    return {f"{line_num}: {col_num} {msg}" for line_num, col_num, msg, _ in plugin.run()}


_CODE_OVER_COMMENTS = [
    ("foo = 1", 1),
    ("def foo():", 1),
    (
        """def foo() -> None:
            pass""",
        1,
    ),
    (
        """class FooClass::
                def foo() -> None:
                pass""",
        3,
    ),
]


@pytest.mark.parametrize("code, line_with_comment", _CODE_OVER_COMMENTS)
@pytest.mark.parametrize(
    "error, comment",
    [
        (ErrorCode.ADO001_MISSING_ITEM, "# ADO: AB#123345 See the ticket"),
        (ErrorCode.ADO002_MALFORMED_ITEM_REF, "# ADO: AB: 1234567 See the ticket"),
        (ErrorCode.ADO002_MALFORMED_ITEM_REF, "# ADO: #1234567 See the ticket"),
        (ErrorCode.ADO002_MALFORMED_ITEM_REF, "# ADO: ab 1234567 See the ticket"),
        (ErrorCode.ADO002_MALFORMED_ITEM_REF, "# ADO: 1234567 See the ticket"),
        (ErrorCode.ADO002_MALFORMED_ITEM_REF, "# ADO: I forgot the number"),
        (ErrorCode.ADO002_MALFORMED_ITEM_REF, "# ADO: Fix this"),
        (ErrorCode.ADO002_MALFORMED_ITEM_REF, "# ADO: AB123444"),
        (ErrorCode.ADO002_MALFORMED_ITEM_REF, "# ADO: ab123444"),
        (ErrorCode.ADO002_MALFORMED_ITEM_REF, "# ADO: ABblahblah"),
        (ErrorCode.ADO002_MALFORMED_ITEM_REF, "# ADO: abblahblah"),
        (ErrorCode.ADO003_CAPITALIZATION, "# ado: AB#112233"),
        (ErrorCode.ADO003_CAPITALIZATION, "# ADO: ab#112233"),
        (ErrorCode.ADO003_CAPITALIZATION, "# ado: ab#112233"),
        (ErrorCode.ADO005_NO_TODO_REF, "# TODO: someone fix this please"),
        (ErrorCode.ADO005_NO_TODO_REF, "# todo someone fix this please"),
        (ErrorCode.ADO005_NO_TODO_REF, "# fix it please todo"),
        (ErrorCode.ADO005_NO_TODO_REF, "# tOdO"),
    ],
)
def test_plugin_with_errors(error: str, comment: str, code: str, line_with_comment: int):
    result = lint_(f"{code} {comment}")
    column = len(code.split("\n")[line_with_comment - 1])
    assert result == {f"{line_with_comment}: {column + 1} {error}"}


@pytest.mark.parametrize("code", _CODE_OVER_COMMENTS)
@pytest.mark.parametrize(
    "comment",
    [
        "# ADO: AB#112233 See the ticket",
        "# TODO AB#112233 Something",
        "# TODO AB#112233",
        "# This needs to be fixed, todo AB#112233",
    ],
)
def test_plugin_with_proper_code(code: str, comment: str) -> None:
    assert lint_(comment) == set()
