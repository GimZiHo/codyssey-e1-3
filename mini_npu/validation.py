"""MAC 연산에 들어가는 행렬의 형태와 값 검증을 담당한다."""

import math
from typing import List, Optional


Matrix = List[List[float]]


def validate_square_matrix(
    matrix: Matrix,
    expected_size: Optional[int] = None,
    name: str = "matrix",
) -> int:
    """값이 유한한 숫자로 구성된 정사각 행렬인지 검증한다.

    Args:
        matrix: 검증할 2차원 리스트.
        expected_size: 이미 정해진 행렬 한 변의 길이. 없으면 생략한다.
        name: 오류 메시지에서 행렬을 구분할 이름.

    Returns:
        검증을 통과한 정사각 행렬의 한 변 길이.

    Raises:
        ValueError: 행렬이 비었거나 정사각형이 아니거나, 예상 크기와
            다르거나, 숫자가 아닌 값 또는 유한하지 않은 값이 있을 때.
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
