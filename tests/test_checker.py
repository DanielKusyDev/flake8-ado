from typing import Set

import pytest

from flake8_aod import Checker
from flake8_aod.checker import ErrorCode


def lint_(input_: str) -> Set[str]:
    checker = Checker(None, input_.split("\n"))
    return {f"{line_num}: {col_num} {msg}" for line_num, col_num, msg, _ in checker.run()}


@pytest.mark.parametrize(
    "code, line_with_comment",
    [
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
    ],
)
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
        (ErrorCode.ADO003_CAPITALIZATION, "# TODO: someone fix this please"),
        (ErrorCode.ADO003_CAPITALIZATION, "# todo someone fix this please"),
        (ErrorCode.ADO003_CAPITALIZATION, "# fix it please todo"),
        (ErrorCode.ADO003_CAPITALIZATION, "# tOdO"),
    ],
)
def test_checker_with_errors(error: str, comment: str, code: str, line_with_comment: int):
    result = lint_(f"{code} {comment}")
    column = len(code.split("\n")[line_with_comment - 1])
    assert result == {f"{line_with_comment}: {column + 1} {error}"}
