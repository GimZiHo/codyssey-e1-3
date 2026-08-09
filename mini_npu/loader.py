"""File loading and key parsing helpers for the data.json schema."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Union


PATTERN_KEY = re.compile(r"^size_([1-9]\d*)_([^\s]+)$")


class DataLoadError(Exception):
    """Raised when a JSON data file cannot be loaded as an object."""


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


def load_json_file(path: Union[str, Path]) -> Dict[str, Any]:
    """Load a UTF-8 JSON file whose top-level value must be an object."""
    file_path = Path(path)

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise DataLoadError(
            "invalid JSON in {} at line {}, column {}.".format(
                file_path, error.lineno, error.colno
            )
        ) from error
    except OSError as error:
        raise DataLoadError(
            "could not read data file {}: {}.".format(file_path, error.strerror)
        ) from error

    if not isinstance(data, dict):
        raise DataLoadError("top-level JSON value must be an object.")

    return data
