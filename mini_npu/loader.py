"""Parsing helpers for the data.json schema."""

import re
from dataclasses import dataclass


PATTERN_KEY = re.compile(r"^size_([1-9]\d*)_([^\s]+)$")


@dataclass(frozen=True)
class ParsedPatternKey:
    """Structured values extracted from a pattern key."""

    size: int
    case_id: str

    @property
    def filter_key(self) -> str:
        """Return the matching key used in the filters object."""
        return "size_{}".format(self.size)


def parse_pattern_key(key: str) -> ParsedPatternKey:
    """Parse ``size_{N}_{case_id}`` and reject malformed keys."""
    if not isinstance(key, str):
        raise ValueError("pattern key must be a string.")

    match = PATTERN_KEY.fullmatch(key)
    if match is None:
        raise ValueError(
            "invalid pattern key {!r}: expected size_{{N}}_{{case_id}}.".format(
                key
            )
        )

    return ParsedPatternKey(
        size=int(match.group(1)),
        case_id=match.group(2),
    )
