import unittest

from mini_npu.loader import ParsedPatternKey, parse_pattern_key


class ParsePatternKeyTests(unittest.TestCase):
    def test_extracts_size_and_numeric_case_id(self):
        parsed = parse_pattern_key("size_13_2")

        self.assertEqual(parsed, ParsedPatternKey(size=13, case_id="2"))
        self.assertEqual(parsed.filter_key, "size_13")

    def test_preserves_non_numeric_case_id(self):
        parsed = parse_pattern_key("size_25_example")

        self.assertEqual(parsed.size, 25)
        self.assertEqual(parsed.case_id, "example")
        self.assertEqual(parsed.filter_key, "size_25")

    def test_rejects_missing_prefix(self):
        with self.assertRaisesRegex(ValueError, "expected"):
            parse_pattern_key("13_2")

    def test_rejects_missing_case_id(self):
        with self.assertRaisesRegex(ValueError, "expected"):
            parse_pattern_key("size_13_")

    def test_rejects_zero_size(self):
        with self.assertRaisesRegex(ValueError, "expected"):
            parse_pattern_key("size_0_1")

    def test_rejects_negative_size(self):
        with self.assertRaisesRegex(ValueError, "expected"):
            parse_pattern_key("size_-5_1")

    def test_rejects_whitespace_in_key(self):
        with self.assertRaisesRegex(ValueError, "expected"):
            parse_pattern_key("size_5_case one")

    def test_rejects_non_string_key(self):
        with self.assertRaisesRegex(ValueError, "must be a string"):
            parse_pattern_key(13)


if __name__ == "__main__":
    unittest.main()
