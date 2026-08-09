import unittest

from mini_npu.benchmark import measure_pair_average_ms
from mini_npu.constants import BENCHMARK_REPEATS


class MeasurePairAverageTests(unittest.TestCase):
    def test_converts_elapsed_nanoseconds_to_average_milliseconds(self):
        times = iter([1_000_000, 3_000_000])
        matrix = [[1.0]]

        average_ms = measure_pair_average_ms(
            matrix,
            matrix,
            matrix,
            repeats=10,
            clock_ns=lambda: next(times),
        )

        self.assertEqual(average_ms, 0.2)

    def test_rejects_fewer_than_ten_repeats(self):
        with self.assertRaisesRegex(ValueError, "at least"):
            measure_pair_average_ms([[1.0]], [[1.0]], [[1.0]], repeats=9)

    def test_default_repeat_count_is_at_least_requirement(self):
        self.assertGreaterEqual(BENCHMARK_REPEATS, 10)


if __name__ == "__main__":
    unittest.main()
