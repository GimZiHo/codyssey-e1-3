import unittest
from unittest.mock import patch

from mini_npu.modes import mode1_decision, run_mode1


CROSS_ROWS = ["0 1 0", "1 1 1", "0 1 0"]
X_ROWS = ["1 0 1", "0 1 0", "1 0 1"]


class Mode1DecisionTests(unittest.TestCase):
    def test_selects_a(self):
        self.assertEqual(mode1_decision(5.0, 1.0), "A")

    def test_selects_b(self):
        self.assertEqual(mode1_decision(1.0, 5.0), "B")

    def test_reports_undecided_inside_epsilon(self):
        self.assertEqual(mode1_decision(0.9, 0.9 + 1e-10), "판정 불가")


class RunMode1Tests(unittest.TestCase):
    @patch("mini_npu.modes.measure_pair_average_ms", return_value=0.012345)
    def test_prints_scores_time_and_b_decision(self, _mock_measure):
        answers = iter(CROSS_ROWS + X_ROWS + X_ROWS)
        messages = []

        run_mode1(
            input_fn=lambda _prompt: next(answers),
            output_fn=messages.append,
        )

        output = "\n".join(messages)
        self.assertIn("A 점수: 1.0", output)
        self.assertIn("B 점수: 5.0", output)
        self.assertIn("연산 시간(평균/10회): 0.012345 ms", output)
        self.assertIn("판정: B", output)

    @patch("mini_npu.modes.measure_pair_average_ms", return_value=0.01)
    def test_prints_undecided_for_equal_filters(self, _mock_measure):
        answers = iter(CROSS_ROWS + CROSS_ROWS + X_ROWS)
        messages = []

        run_mode1(
            input_fn=lambda _prompt: next(answers),
            output_fn=messages.append,
        )

        self.assertIn(
            "판정: 판정 불가 (|A-B| < 1e-9)",
            "\n".join(messages),
        )


if __name__ == "__main__":
    unittest.main()
