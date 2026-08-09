import unittest

from mini_npu.constants import CROSS, X_LABEL
from mini_npu.labels import normalize_label


class NormalizeLabelTests(unittest.TestCase):
    def test_normalizes_plus_to_cross(self):
        self.assertEqual(normalize_label("+"), CROSS)

    def test_normalizes_cross_filter_key(self):
        self.assertEqual(normalize_label("cross"), CROSS)

    def test_normalizes_lowercase_x(self):
        self.assertEqual(normalize_label("x"), X_LABEL)

    def test_ignores_surrounding_whitespace_and_case(self):
        self.assertEqual(normalize_label("  CrOsS  "), CROSS)
        self.assertEqual(normalize_label("  X  "), X_LABEL)

    def test_rejects_unknown_label(self):
        with self.assertRaisesRegex(ValueError, "unsupported label"):
            normalize_label("circle")

    def test_rejects_empty_label(self):
        with self.assertRaisesRegex(ValueError, "unsupported label"):
            normalize_label("   ")

    def test_rejects_non_string_label(self):
        with self.assertRaisesRegex(ValueError, "must be a string"):
            normalize_label(1)


if __name__ == "__main__":
    unittest.main()
