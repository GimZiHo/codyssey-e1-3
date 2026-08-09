"""Console input parsing for square matrices."""

import math
from typing import Callable, List, Optional

from mini_npu.validation import Matrix


def parse_matrix_row(text: str, size: int) -> List[float]:
    """Parse one whitespace-separated row containing exactly ``size`` numbers."""
    parts = text.split()
    if len(parts) != size:
        raise ValueError(
            "각 줄에 {}개의 숫자를 공백으로 구분해 입력하세요.".format(size)
        )

    try:
        row = [float(part) for part in parts]
    except ValueError as error:
        raise ValueError("모든 값은 숫자여야 합니다.") from error

    if not all(math.isfinite(value) for value in row):
        raise ValueError("모든 값은 유한한 숫자여야 합니다.")

    return row


def read_square_matrix(
    name: str,
    size: int = 3,
    input_fn: Optional[Callable[[str], str]] = None,
    output_fn: Optional[Callable[[str], None]] = None,
) -> Matrix:
    """Read a square matrix, retrying only the row that contains an error."""
    if size <= 0:
        raise ValueError("size must be positive.")

    actual_input = input if input_fn is None else input_fn
    actual_output = print if output_fn is None else output_fn
    matrix = []

    actual_output("{} ({}줄 입력, 공백 구분)".format(name, size))
    while len(matrix) < size:
        row_number = len(matrix) + 1
        text = actual_input("{}행: ".format(row_number))
        try:
            matrix.append(parse_matrix_row(text, size))
        except ValueError as error:
            actual_output("입력 형식 오류: {}".format(error))

    return matrix
