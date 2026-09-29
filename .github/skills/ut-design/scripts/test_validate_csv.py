"""Tests for the ut-design CSV validator/auto-fixer (fix_csv.py).

Run with: pytest .github/skills/ut-design/scripts/test_validate_csv.py
"""
import csv
import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).parent / "fix_csv.py"
spec = importlib.util.spec_from_file_location("fix_csv", SCRIPT_PATH)
fix_csv = importlib.util.module_from_spec(spec)
sys.modules["fix_csv"] = fix_csv
spec.loader.exec_module(fix_csv)


VALID_ROW = [
    "UT-001", "boot_status_success", "desc", '{"boot_status":"SUCCESS"}', "positive", "PASS", "", "yes", "note",
]


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


class TestNormalizeAutomated:
    @pytest.mark.parametrize("value,expected", [("yes", "yes"), ("no", "no")])
    def test_already_normalized_is_unchanged(self, value, expected):
        result, changed = fix_csv.normalize_automated(value)
        assert result == expected
        assert changed is False

    @pytest.mark.parametrize(
        "value,expected",
        [("Y", "yes"), ("true", "yes"), ("1", "yes"), ("YES", "yes"), (" yes ", "yes")],
    )
    def test_truthy_variants_normalize_to_yes(self, value, expected):
        result, changed = fix_csv.normalize_automated(value)
        assert result == expected

    @pytest.mark.parametrize("value,expected", [("N", "no"), ("false", "no"), ("0", "no"), ("FALSE", "no")])
    def test_falsy_variants_normalize_to_no(self, value, expected):
        result, changed = fix_csv.normalize_automated(value)
        assert result == expected

    def test_unrecognized_value_is_returned_unchanged(self):
        result, changed = fix_csv.normalize_automated("maybe")
        assert result == "maybe"
        assert changed is False


class TestFixRows:
    def test_valid_row_produces_no_warnings(self):
        warnings: list[str] = []
        fixed = fix_csv.fix_rows([VALID_ROW], warnings)
        assert fixed == [VALID_ROW]
        assert warnings == []

    def test_short_row_is_padded(self):
        warnings: list[str] = []
        short_row = ["UT-002", "name", "desc", "{}", "edge", "FAIL"]
        fixed = fix_csv.fix_rows([short_row], warnings)
        assert fixed[0] == ["UT-002", "name", "desc", "{}", "edge", "FAIL", "", "", ""]
        assert any("padded" in w for w in warnings)

    def test_long_row_merges_extras_into_comments(self):
        warnings: list[str] = []
        long_row = VALID_ROW + ["part1", "part2"]
        fixed = fix_csv.fix_rows([long_row], warnings)
        assert fixed[0][-1] == "note,part1,part2"
        assert any("merged" in w for w in warnings)

    def test_automated_value_is_normalized_in_output(self):
        warnings: list[str] = []
        row = VALID_ROW.copy()
        row[7] = "Y"
        fixed = fix_csv.fix_rows([row], warnings)
        assert fixed[0][7] == "yes"
        assert any("normalized 'automated'" in w for w in warnings)

    def test_invalid_test_case_type_is_flagged_for_manual_review(self):
        warnings: list[str] = []
        row = VALID_ROW.copy()
        row[4] = "smoke"
        fix_csv.fix_rows([row], warnings)
        assert any("needs manual review" in w and "test case type" in w for w in warnings)

    def test_id_not_matching_pattern_is_flagged(self):
        warnings: list[str] = []
        row = VALID_ROW.copy()
        row[0] = "TC-1"
        fix_csv.fix_rows([row], warnings)
        assert any("does not match UT-### pattern" in w for w in warnings)

    def test_duplicate_id_is_flagged(self):
        warnings: list[str] = []
        fix_csv.fix_rows([VALID_ROW, VALID_ROW.copy()], warnings)
        assert any("duplicate testcase id" in w for w in warnings)

    def test_malformed_json_in_clear_input_is_flagged(self):
        warnings: list[str] = []
        row = VALID_ROW.copy()
        row[3] = '{"boot_status":"SUCCESS"'
        fix_csv.fix_rows([row], warnings)
        assert any("failed to parse" in w for w in warnings)

    def test_non_blank_actual_output_is_flagged(self):
        warnings: list[str] = []
        row = VALID_ROW.copy()
        row[6] = "PASS"
        fix_csv.fix_rows([row], warnings)
        assert any("'actual output' should be blank" in w for w in warnings)


class TestMain:
    def test_valid_csv_exits_zero_and_prints_no_issues(self, tmp_path, capsys):
        path = tmp_path / "design.csv"
        write_csv(path, fix_csv.REQUIRED_HEADER, [VALID_ROW])
        sys.argv = ["fix_csv.py", str(path)]
        exit_code = fix_csv.main()
        assert exit_code == 0
        assert "No issues found" in capsys.readouterr().out

    def test_malformed_csv_is_rewritten_when_auto_fixable(self, tmp_path):
        path = tmp_path / "design.csv"
        row = VALID_ROW.copy()
        row[7] = "Y"
        write_csv(path, fix_csv.REQUIRED_HEADER, [row])
        sys.argv = ["fix_csv.py", str(path)]
        exit_code = fix_csv.main()
        assert exit_code == 0

        with path.open(encoding="utf-8") as f:
            rewritten_rows = list(csv.reader(f))
        assert rewritten_rows[1][7] == "yes"

    def test_check_only_does_not_modify_file(self, tmp_path):
        path = tmp_path / "design.csv"
        row = VALID_ROW.copy()
        row[7] = "Y"
        write_csv(path, fix_csv.REQUIRED_HEADER, [row])
        original_contents = path.read_text(encoding="utf-8")

        sys.argv = ["fix_csv.py", str(path), "--check-only"]
        fix_csv.main()

        assert path.read_text(encoding="utf-8") == original_contents

    def test_unresolved_issue_exits_nonzero(self, tmp_path):
        path = tmp_path / "design.csv"
        row = VALID_ROW.copy()
        row[0] = "TC-1"
        write_csv(path, fix_csv.REQUIRED_HEADER, [row])
        sys.argv = ["fix_csv.py", str(path)]
        exit_code = fix_csv.main()
        assert exit_code == 1

    def test_missing_file_exits_with_usage_error(self, tmp_path):
        missing = tmp_path / "nope.csv"
        sys.argv = ["fix_csv.py", str(missing)]
        exit_code = fix_csv.main()
        assert exit_code == 2

    def test_no_arguments_exits_with_usage_error(self):
        sys.argv = ["fix_csv.py"]
        exit_code = fix_csv.main()
        assert exit_code == 2
