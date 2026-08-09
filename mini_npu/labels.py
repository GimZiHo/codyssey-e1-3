"""외부 라벨 표현을 프로그램 내부 표준 라벨로 변환한다."""

from mini_npu.constants import CROSS, X_LABEL


LABEL_ALIASES = {
    "+": CROSS,
    "cross": CROSS,
    "x": X_LABEL,
}


def normalize_label(value: str) -> str:
    """지원하는 외부 라벨을 표준 라벨인 Cross 또는 X로 변환한다.

    Args:
        value: `+`, `cross`, `x` 등 외부에서 읽은 라벨 문자열.

    Returns:
        공백과 대소문자를 정리한 표준 라벨 `Cross` 또는 `X`.

    Raises:
        ValueError: 문자열이 아니거나 지원하지 않는 라벨일 때.
    """
    if not isinstance(value, str):
        raise ValueError("label must be a string.")

    normalized_key = value.strip().lower()
    if normalized_key not in LABEL_ALIASES:
        raise ValueError("unsupported label: {!r}.".format(value))

    return LABEL_ALIASES[normalized_key]
