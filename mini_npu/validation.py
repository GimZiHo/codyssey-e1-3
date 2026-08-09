"""Validation helpers for matrices used by MAC operations."""

import math
from typing import List, Optional


Matrix = List[List[float]]


def validate_square_matrix(
    matrix: Matrix,
    expected_size: Optional[int] = None,
    name: str = "matrix",
) -> int:
    """Validate a finite numeric square matrix and return its size.

    Args:
        matrix: Two-dimensional list to validate.
        expected_size: Required side length when a size is already known.
        name: Human-readable name included in error messages.

    Raises:
        ValueError: If the value is empty, non-square, has the wrong size,
            or contains a non-numeric/non-finite value.
    """
    if not isinstance(matrix, list) or not matrix:
        raise ValueError("{} must be a non-empty two-dimensional list.".format(name))

    size = len(matrix)
    if expected_size is not None and size != expected_size:
        raise ValueError(
            "{} must have {} rows, but received {}.".format(
                name, expected_size, size
            )
        )

    for row_index, row in enumerate(matrix):
        if not isinstance(row, list):
            raise ValueError("{} row {} must be a list.".format(name, row_index))
        if len(row) != size:
            raise ValueError(
                "{} must be square: row {} has {} values, expected {}.".format(
                    name, row_index, len(row), size
                )
            )

        for column_index, value in enumerate(row):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(
                    "{}[{}][{}] must be a number.".format(
                        name, row_index, column_index
                    )
                )
            if not math.isfinite(value):
                raise ValueError(
                    "{}[{}][{}] must be finite.".format(
                        name, row_index, column_index
                    )
                )

    return size
