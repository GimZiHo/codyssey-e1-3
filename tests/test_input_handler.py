import unittest

from mini_npu.input_handler import parse_matrix_row, read_square_matrix


class ParseMatrixRowTests(unittest.TestCase):
    def test_parses_three_numbers_as_floats(self):
        self.assertEqual(parse_matrix_row("0 1 0.5", 3), [0.0, 1.0, 0.5])

    def test_rejects_wrong_column_count(self):
        with self.assertRaisesRegex(ValueError, "3개의 숫자"):
            parse_matrix_row("0 1", 3)

    def test_rejects_non_numeric_value(self):
        with self.assertRaisesRegex(ValueError, "숫자여야"):
            parse_matrix_row("0 hello 1", 3)

    def test_rejects_non_finite_value(self):
        with self.assertRaisesRegex(ValueError, "유한한 숫자"):
            parse_matrix_row("0 nan 1", 3)


class ReadSquareMatrixTests(unittest.TestCase):
    def test_retries_invalid_row_and_keeps_valid_rows(self):
        answers = iter(["0 1", "0 1 0", "1 1 1", "0 1 0"])
        messages = []

        matrix = read_square_matrix(
            "패턴",
            input_fn=lambda _prompt: next(answers),
            output_fn=messages.append,
        )

        self.assertEqual(
            matrix,
            [[0.0, 1.0, 0.0], [1.0, 1.0, 1.0], [0.0, 1.0, 0.0]],
        )
        self.assertTrue(any("입력 형식 오류" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
