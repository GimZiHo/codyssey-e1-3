"""data.json 파일 로드와 단계별 스키마 검증 기능을 제공한다."""

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
    """JSON 파일을 읽거나 최상위 객체로 변환할 수 없을 때 사용한다."""


class SchemaValidationError(ValueError):
    """로드된 데이터가 과제의 스키마 규칙을 위반할 때 사용한다."""


@dataclass(frozen=True)
class ParsedPatternKey:
    """패턴 키에서 추출한 크기와 케이스 식별자를 보관한다."""

    size: int
    case_id: str

    @property
    def filter_key(self) -> str:
        """패턴 크기에 대응하는 filters의 `size_N` 키를 계산한다."""
        return "size_{}".format(self.size)


@dataclass(frozen=True)
class TopLevelSchema:
    """검증된 필수 섹션과 분석을 막지 않는 meta 경고를 보관한다."""

    filters: Dict[str, Any]
    patterns: Dict[str, Any]
    warnings: Tuple[str, ...]


@dataclass(frozen=True)
class ValidatedFilterGroup:
    """크기와 라벨 검증을 통과한 Cross/X 필터 쌍을 보관한다."""

    size: int
    filters: Dict[str, Matrix]


def parse_pattern_key(key: str) -> ParsedPatternKey:
    """`size_{N}_{case_id}` 형식의 패턴 키를 구조화한다.

    Args:
        key: patterns 객체에서 읽은 패턴 키.

    Returns:
        크기 N과 케이스 식별자를 담은 `ParsedPatternKey`.

    Raises:
        ValueError: 문자열이 아니거나 정해진 키 형식과 다를 때.
    """
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
    """UTF-8 JSON 파일을 읽고 최상위 객체를 반환한다.

    Args:
        path: 읽을 JSON 파일의 문자열 또는 Path 경로.

    Returns:
        JSON 최상위 객체를 변환한 dict.

    Raises:
        DataLoadError: 파일을 읽을 수 없거나 JSON 문법이 잘못됐거나,
            최상위 값이 객체가 아닐 때.
    """
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
    """최상위 필수 섹션을 검증하고 meta 경고를 수집한다.

    Args:
        data: `load_json_file()`이 반환한 최상위 JSON 객체.

    Returns:
        검증된 filters, patterns와 meta 경고를 담은 결과.

    Raises:
        SchemaValidationError: 최상위 값이나 필수 섹션이 객체가 아닐 때,
            또는 filters/patterns가 누락됐을 때.
    """
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
    """`size_N` 필터 그룹 하나의 라벨과 두 행렬을 검증한다.

    Args:
        group_key: `size_5`처럼 필터 크기를 포함한 그룹 키.
        raw_group: Cross와 X 필터가 들어 있는 원시 JSON 값.

    Returns:
        크기와 정규화된 Cross/X 행렬을 담은 검증 결과.

    Raises:
        SchemaValidationError: 그룹 키/자료형/라벨이 잘못됐거나 필터가
            누락됐거나 행렬이 N×N 유한 숫자 구조가 아닐 때.
    """
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
