"""콘솔 문자열을 정사각 숫자 행렬로 입력받는 기능을 제공한다."""

import math
from typing import Callable, List, Optional

from mini_npu.validation import Matrix


def parse_matrix_row(text: str, size: int) -> List[float]:
    """공백으로 구분된 한 줄을 지정한 개수의 실수로 변환한다.

    Args:
        text: 사용자가 입력한 행 문자열.
        size: 한 행에 필요한 숫자의 개수.

    Returns:
        문자열의 각 값을 float로 변환한 한 행.

    Raises:
        ValueError: 열 개수가 다르거나 숫자로 변환할 수 없거나,
            유한하지 않은 값이 있을 때.
    """
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
    """정사각 행렬을 한 행씩 입력받고 잘못된 행만 다시 요청한다.

    Args:
        name: 화면에 표시할 행렬 이름.
        size: 입력받을 행과 열의 개수.
        input_fn: 입력 함수. 생략하면 내장 `input`을 사용한다.
        output_fn: 출력 함수. 생략하면 내장 `print`를 사용한다.

    Returns:
        입력 검증을 통과한 size×size 실수 행렬.

    Raises:
        ValueError: size가 0 이하일 때.
    """
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
