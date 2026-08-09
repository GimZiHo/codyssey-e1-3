import json
import unittest
from unittest.mock import mock_open, patch

from mini_npu.loader import (
    DataLoadError,
    ParsedPatternKey,
    SchemaValidationError,
    TopLevelSchema,
    load_json_file,
    parse_pattern_key,
    validate_top_level_schema,
)


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


class LoadJsonFileTests(unittest.TestCase):
    def test_loads_utf8_json_object(self):
        expected = {"message": "십자가", "filters": {}}

        with patch(
            "pathlib.Path.open",
            mock_open(read_data=json.dumps(expected, ensure_ascii=False)),
        ):
            self.assertEqual(load_json_file("data.json"), expected)

    def test_rejects_missing_file(self):
        error = FileNotFoundError(2, "No such file or directory")
        with patch("pathlib.Path.open", side_effect=error):
            with self.assertRaisesRegex(DataLoadError, "could not read"):
                load_json_file("missing.json")

    def test_reports_invalid_json_location(self):
        with patch(
            "pathlib.Path.open", mock_open(read_data='{"filters": }')
        ):
            with self.assertRaisesRegex(DataLoadError, "line 1, column"):
                load_json_file("invalid.json")

    def test_rejects_top_level_array(self):
        with patch("pathlib.Path.open", mock_open(read_data="[]")):
            with self.assertRaisesRegex(DataLoadError, "must be an object"):
                load_json_file("array.json")


class ValidateTopLevelSchemaTests(unittest.TestCase):
    def test_returns_required_sections_without_warnings(self):
        filters = {"size_5": {}}
        patterns = {"size_5_1": {}}
        data = {
            "meta": {"version": "1.0", "type": "json"},
            "filters": filters,
            "patterns": patterns,
        }

        result = validate_top_level_schema(data)

        self.assertEqual(
            result,
            TopLevelSchema(filters=filters, patterns=patterns, warnings=()),
        )

    def test_rejects_missing_filters(self):
        with self.assertRaisesRegex(SchemaValidationError, "'filters' is missing"):
            validate_top_level_schema({"patterns": {}})

    def test_rejects_missing_patterns(self):
        with self.assertRaisesRegex(SchemaValidationError, "'patterns' is missing"):
            validate_top_level_schema({"filters": {}})

    def test_rejects_non_object_required_section(self):
        with self.assertRaisesRegex(SchemaValidationError, "must be an object"):
            validate_top_level_schema({"filters": [], "patterns": {}})

    def test_warns_when_meta_is_missing(self):
        result = validate_top_level_schema({"filters": {}, "patterns": {}})

        self.assertEqual(
            result.warnings,
            ("meta is missing or is not an object.",),
        )

    def test_warns_for_unexpected_meta_values(self):
        data = {
            "meta": {"version": "2.0", "type": "text"},
            "filters": {},
            "patterns": {},
        }

        result = validate_top_level_schema(data)

        self.assertEqual(
            result.warnings,
            ("meta.version is not '1.0'.", "meta.type is not 'json'."),
        )

    def test_rejects_non_object_top_level_data(self):
        with self.assertRaisesRegex(SchemaValidationError, "top-level"):
            validate_top_level_schema([])


if __name__ == "__main__":
    unittest.main()
