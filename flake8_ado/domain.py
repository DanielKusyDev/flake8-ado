from dataclasses import dataclass
from enum import Enum
from typing import Tuple


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

    def as_flake8(self) -> Tuple[int, int, str]:
        return self.line_num, self.match_col, self.code.value


@dataclass(frozen=True)
class TagAnnotatedLine:
    line: str
    line_num: int
    tag: str
