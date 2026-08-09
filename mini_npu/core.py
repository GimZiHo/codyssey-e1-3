"""MAC 점수 계산과 epsilon 기반 점수 비교를 담당한다."""

import math

from mini_npu.constants import EPSILON
from mini_npu.validation import Matrix, validate_square_matrix


def mac_2d(pattern: Matrix, filter_matrix: Matrix) -> float:
    """패턴과 필터의 같은 위치 값을 곱해 모두 더한 MAC 점수를 구한다.

    Args:
        pattern: 입력 패턴을 나타내는 N×N 숫자 행렬.
        filter_matrix: 비교 기준인 N×N 숫자 행렬.

    Returns:
        위치별 곱셈 결과를 모두 누적한 실수 점수.

    Raises:
        ValueError: 두 행렬이 올바른 정사각 행렬이 아니거나 크기가 다를 때.
    """
    pattern_size = validate_square_matrix(pattern, name="pattern")
    filter_size = validate_square_matrix(filter_matrix, name="filter")

    if pattern_size != filter_size:
        raise ValueError(
            "pattern and filter sizes must match: {} != {}.".format(
                pattern_size, filter_size
            )
        )

    total = 0.0
    for row_index in range(pattern_size):
        for column_index in range(pattern_size):
            total += (
                pattern[row_index][column_index]
                * filter_matrix[row_index][column_index]
            )
    return total


def compare_scores(
    score_a: float,
    score_b: float,
    epsilon: float = EPSILON,
) -> int:
    """두 점수의 차이를 epsilon 허용오차를 적용하여 비교한다.

    Args:
        score_a: 첫 번째 필터의 MAC 점수.
        score_b: 두 번째 필터의 MAC 점수.
        epsilon: 두 점수를 동점으로 볼 최대 차이의 경계값.

    Returns:
        epsilon 범위 내 동점이면 0, A가 크면 1, B가 크면 -1.

    Raises:
        ValueError: 점수나 epsilon이 올바른 유한 숫자가 아니거나,
            epsilon이 0 이하일 때.
    """
    for name, score in (("score_a", score_a), ("score_b", score_b)):
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise ValueError("{} must be a number.".format(name))
        if not math.isfinite(score):
            raise ValueError("{} must be finite.".format(name))

    if (
        isinstance(epsilon, bool)
        or not isinstance(epsilon, (int, float))
        or not math.isfinite(epsilon)
        or epsilon <= 0
    ):
        raise ValueError("epsilon must be a positive finite number.")

    difference = abs(score_a - score_b)
    if difference < epsilon:
        return 0
    return 1 if score_a > score_b else -1
