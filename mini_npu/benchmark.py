"""Timing helpers that measure MAC calls without console or file I/O."""

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
    """Return average milliseconds for one A/B MAC calculation pair."""
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
