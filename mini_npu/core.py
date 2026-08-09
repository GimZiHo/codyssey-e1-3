"""Core MAC calculation and score comparison logic."""

import math

from mini_npu.constants import EPSILON
from mini_npu.validation import Matrix, validate_square_matrix


def mac_2d(pattern: Matrix, filter_matrix: Matrix) -> float:
    """Multiply matching matrix positions and accumulate their sum."""
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
    """Compare two scores using epsilon.

    Returns:
        0 when the scores are tied within epsilon, 1 when A is larger,
        and -1 when B is larger.
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
