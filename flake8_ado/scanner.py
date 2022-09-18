import re
from functools import lru_cache
from typing import List

_ANNOTATION_PATTERN = re.compile(r"# ((ado: )|(todo: )).*$", flags=re.IGNORECASE)


class RegexMatcher:
    @lru_cache(maxsize=None)
    def get_reference_match(self, line: str, tag: str) -> re.Match:
        reference_pattern = re.compile(rf"# {tag}AB#(\d+)(\s|.$)", flags=re.IGNORECASE)
        return re.search(reference_pattern, line)

    @lru_cache(maxsize=None)
    def get_reference_number(self, line: str) -> str:
        return re.compile(r"AB#(\d+)", flags=re.IGNORECASE).findall(line)[0]

    @lru_cache(maxsize=None)
    def get_tag_match(self, line: str, tag: str) -> re.Match:
        tag_pattern = re.compile(rf"# {tag}", flags=re.IGNORECASE)
        return re.search(tag_pattern, line)

    @staticmethod
    def get_lines_with_annotated_comments(lines: List[str]):
        for line_num, line in enumerate(lines):
            tags = {part.lower() for match in _ANNOTATION_PATTERN.findall(line) for part in match if part}
            if tags:
                yield line, line_num + 1, tags.pop()
