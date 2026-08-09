"""File loading and key parsing helpers for the data.json schema."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple, Union

from mini_npu.constants import CROSS, X_LABEL
from mini_npu.labels import normalize_label
from mini_npu.validation import Matrix, validate_square_matrix


PATTERN_KEY = re.compile(r"^size_([1-9]\d*)_([^\s]+)$")
FILTER_GROUP_KEY = re.compile(r"^size_([1-9]\d*)$")


class DataLoadError(Exception):
    """Raised when a JSON data file cannot be loaded as an object."""


class SchemaValidationError(ValueError):
    """Raised when required top-level JSON sections are invalid."""


@dataclass(frozen=True)
class ParsedPatternKey:
    """Structured values extracted from a pattern key."""

    size: int
    case_id: str

    @property
    def filter_key(self) -> str:
        """Return the matching key used in the filters object."""
        return "size_{}".format(self.size)


@dataclass(frozen=True)
class TopLevelSchema:
    """Validated top-level sections and non-fatal metadata warnings."""

    filters: Dict[str, Any]
    patterns: Dict[str, Any]
    warnings: Tuple[str, ...]


@dataclass(frozen=True)
class ValidatedFilterGroup:
    """A size-specific pair of normalized and validated filters."""

    size: int
    filters: Dict[str, Matrix]


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


def validate_top_level_schema(data: Dict[str, Any]) -> TopLevelSchema:
    """Validate required sections and collect non-fatal metadata warnings."""
    if not isinstance(data, dict):
        raise SchemaValidationError("top-level data must be an object.")

    for section_name in ("filters", "patterns"):
        if section_name not in data:
            raise SchemaValidationError(
                "required section {!r} is missing.".format(section_name)
            )
        if not isinstance(data[section_name], dict):
            raise SchemaValidationError(
                "required section {!r} must be an object.".format(section_name)
            )

    warnings = []
    meta = data.get("meta")
    if not isinstance(meta, dict):
        warnings.append("meta is missing or is not an object.")
    else:
        if meta.get("version") != "1.0":
            warnings.append("meta.version is not '1.0'.")
        if meta.get("type") != "json":
            warnings.append("meta.type is not 'json'.")

    return TopLevelSchema(
        filters=data["filters"],
        patterns=data["patterns"],
        warnings=tuple(warnings),
    )


def validate_filter_group(
    group_key: str,
    raw_group: Any,
) -> ValidatedFilterGroup:
    """Validate one ``size_N`` group containing Cross and X matrices."""
    if not isinstance(group_key, str):
        raise SchemaValidationError("filter group key must be a string.")

    match = FILTER_GROUP_KEY.fullmatch(group_key)
    if match is None:
        raise SchemaValidationError(
            "invalid filter group key {!r}: expected size_{{N}}.".format(
                group_key
            )
        )

    if not isinstance(raw_group, dict):
        raise SchemaValidationError(
            "filter group {!r} must be an object.".format(group_key)
        )

    size = int(match.group(1))
    normalized_filters = {}
    for raw_label, matrix in raw_group.items():
        try:
            label = normalize_label(raw_label)
        except ValueError as error:
            raise SchemaValidationError(
                "filter group {!r} has invalid label {!r}.".format(
                    group_key, raw_label
                )
            ) from error

        if label in normalized_filters:
            raise SchemaValidationError(
                "filter group {!r} has duplicate label {!r}.".format(
                    group_key, label
                )
            )

        try:
            validate_square_matrix(
                matrix,
                expected_size=size,
                name="{}.{} filter".format(group_key, label),
            )
        except ValueError as error:
            raise SchemaValidationError(str(error)) from error

        normalized_filters[label] = matrix

    missing_labels = [
        label for label in (CROSS, X_LABEL) if label not in normalized_filters
    ]
    if missing_labels:
        raise SchemaValidationError(
            "filter group {!r} is missing: {}.".format(
                group_key, ", ".join(missing_labels)
            )
        )

    return ValidatedFilterGroup(size=size, filters=normalized_filters)
