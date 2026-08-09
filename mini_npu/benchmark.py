"""콘솔·파일 I/O를 제외하고 MAC 함수 호출 시간만 측정한다."""

import time
from typing import Callable

from mini_npu.constants import BENCHMARK_REPEATS
from mini_npu.core import mac_2d
from mini_npu.validation import Matrix


def measure_pair_average_ms(
    pattern: Matrix,
    filter_a: Matrix,
    filter_b: Matrix,
    repeats: int = BENCHMARK_REPEATS,
    clock_ns: Callable[[], int] = time.perf_counter_ns,
) -> float:
    """필터 A와 B의 MAC 계산 한 쌍에 걸린 평균 시간을 측정한다.

    Args:
        pattern: 두 필터와 비교할 N×N 패턴.
        filter_a: 첫 번째 N×N 필터.
        filter_b: 두 번째 N×N 필터.
        repeats: 반복 측정 횟수. 과제 기준에 따라 최소 10회다.
        clock_ns: 나노초 단위 시계 함수. 테스트에서 대체할 수 있다.

    Returns:
        A/B MAC 계산 한 쌍의 평균 실행 시간(ms).

    Raises:
        ValueError: 반복 횟수가 과제의 최소 기준보다 작을 때.
    """
    if repeats < BENCHMARK_REPEATS:
        raise ValueError(
            "repeats must be at least {}.".format(BENCHMARK_REPEATS)
        )

    start_ns = clock_ns()
    for _ in range(repeats):
        mac_2d(pattern, filter_a)
        mac_2d(pattern, filter_b)
    elapsed_ns = clock_ns() - start_ns

    return elapsed_ns / repeats / 1_000_000
