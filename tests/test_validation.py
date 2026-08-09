import math
import unittest

from mini_npu.validation import validate_square_matrix


class ValidateSquareMatrixTests(unittest.TestCase):
    def test_returns_size_for_valid_numeric_matrix(self):
        matrix = [[0, 1.0], [2, 3.5]]

        self.assertEqual(validate_square_matrix(matrix), 2)

    def test_rejects_empty_matrix(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            validate_square_matrix([])

    def test_rejects_non_square_matrix(self):
        with self.assertRaisesRegex(ValueError, "must be square"):
            validate_square_matrix([[1, 2], [3]])

    def test_rejects_wrong_expected_size(self):
        with self.assertRaisesRegex(ValueError, "must have 3 rows"):
            validate_square_matrix([[1, 2], [3, 4]], expected_size=3)

    def test_rejects_non_numeric_value(self):
        with self.assertRaisesRegex(ValueError, "must be a number"):
            validate_square_matrix([[1, "2"], [3, 4]])

    def test_rejects_boolean_value(self):
        with self.assertRaisesRegex(ValueError, "must be a number"):
            validate_square_matrix([[1, True], [3, 4]])

    def test_rejects_non_finite_value(self):
        with self.assertRaisesRegex(ValueError, "must be finite"):
            validate_square_matrix([[1, math.nan], [3, 4]])


if __name__ == "__main__":
    unittest.main()
