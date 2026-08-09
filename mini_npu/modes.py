"""Application workflows for each simulator mode."""

from typing import Callable, Optional

from mini_npu.benchmark import measure_pair_average_ms
from mini_npu.constants import BENCHMARK_REPEATS
from mini_npu.core import compare_scores, mac_2d
from mini_npu.input_handler import read_square_matrix


def mode1_decision(score_a: float, score_b: float) -> str:
    """Convert the shared score comparison into mode 1 wording."""
    comparison = compare_scores(score_a, score_b)
    if comparison == 0:
        return "판정 불가"
    return "A" if comparison == 1 else "B"


def run_mode1(
    input_fn: Optional[Callable[[str], str]] = None,
    output_fn: Optional[Callable[[str], None]] = None,
) -> None:
    """Run the interactive 3x3 input workflow."""
    actual_output = print if output_fn is None else output_fn

    actual_output("\n[1] 필터 입력")
    filter_a = read_square_matrix(
        "필터 A", input_fn=input_fn, output_fn=actual_output
    )
    filter_b = read_square_matrix(
        "필터 B", input_fn=input_fn, output_fn=actual_output
    )
    actual_output("필터 A와 B 저장 완료")

    actual_output("\n[2] 패턴 입력")
    pattern = read_square_matrix(
        "패턴", input_fn=input_fn, output_fn=actual_output
    )

    score_a = mac_2d(pattern, filter_a)
    score_b = mac_2d(pattern, filter_b)
    average_ms = measure_pair_average_ms(pattern, filter_a, filter_b)
    decision = mode1_decision(score_a, score_b)

    actual_output("\n[3] MAC 결과")
    actual_output("A 점수: {}".format(score_a))
    actual_output("B 점수: {}".format(score_b))
    actual_output(
        "연산 시간(평균/{}회): {:.6f} ms".format(
            BENCHMARK_REPEATS, average_ms
        )
    )
    if decision == "판정 불가":
        actual_output("판정: 판정 불가 (|A-B| < 1e-9)")
    else:
        actual_output("판정: {}".format(decision))
