import math
import unittest

from mini_npu.constants import EPSILON
from mini_npu.core import compare_scores, mac_2d


CROSS_3X3 = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0],
]

X_3X3 = [
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 1],
]


class Mac2DTests(unittest.TestCase):
    def test_cross_pattern_with_cross_filter_scores_five(self):
        self.assertEqual(mac_2d(CROSS_3X3, CROSS_3X3), 5.0)

    def test_cross_pattern_with_x_filter_scores_one(self):
        self.assertEqual(mac_2d(CROSS_3X3, X_3X3), 1.0)

    def test_supports_float_values(self):
        pattern = [[0.1, 0.2], [0.3, 0.4]]
        filter_matrix = [[1.0, 0.0], [0.5, 2.0]]

        self.assertTrue(math.isclose(mac_2d(pattern, filter_matrix), 1.05))

    def test_rejects_different_matrix_sizes(self):
        with self.assertRaisesRegex(ValueError, "sizes must match"):
            mac_2d([[1]], [[1, 0], [0, 1]])


class CompareScoresTests(unittest.TestCase):
    def test_returns_zero_inside_epsilon(self):
        self.assertEqual(compare_scores(1.0, 1.0 + EPSILON / 2), 0)

    def test_exact_epsilon_is_not_a_tie(self):
        self.assertEqual(compare_scores(0.0, EPSILON), -1)

    def test_returns_one_when_a_is_larger(self):
        self.assertEqual(compare_scores(5.0, 1.0), 1)

    def test_returns_minus_one_when_b_is_larger(self):
        self.assertEqual(compare_scores(1.0, 5.0), -1)

    def test_rejects_invalid_epsilon(self):
        with self.assertRaisesRegex(ValueError, "positive finite"):
            compare_scores(1.0, 1.0, epsilon=0)


if __name__ == "__main__":
    unittest.main()
