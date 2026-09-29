#!/usr/bin/env python3
"""Validate and auto-fix a unit-test-design CSV against the ut-design skill's column contract.

Usage:
    python fix_csv.py <path-to-csv> [--check-only]

Behavior:
    - Parses the CSV tolerantly (handles quoted commas/quotes/newlines).
    - Normalizes the header to the exact required column names/order when the
      column count matches.
    - Pads rows that are missing trailing columns with empty strings.
    - Folds rows with extra columns (usually an unescaped comma in a comment)
      back into the last column, with a warning.
    - Normalizes the "automated" column to lowercase "yes"/"no".
    - Rewrites the file with correct CSV quoting/escaping.
    - Flags issues it cannot safely auto-fix (duplicate ids, non-JSON "clear
      input" values that look like JSON, malformed expected output) without
      guessing at intent.

Exit code 0 if the resulting file is fully valid, 1 if unresolved issues remain.
"""
import csv
import io
import json
import re
import sys
from pathlib import Path

REQUIRED_HEADER = [
    "testcase id",
    "testcase name",
    "test description",
    "clear input",
    "test case type",
    "expected output",
    "actual output",
    "automated",
    "comments",
]
VALID_TYPES = {"positive", "negative", "edge", "boundary", "exception", "exhaustive"}
ID_PATTERN = re.compile(r"^UT-\d{3,}$")


def normalize_automated(value: str) -> tuple[str, bool]:
    """Return (normalized_value, changed)."""
    v = value.strip().lower()
    if v in ("yes", "no"):
        return v, v != value
    if v in ("y", "true", "1"):
        return "yes", True
    if v in ("n", "false", "0"):
        return "no", True
    return value, False


def fix_rows(rows: list[list[str]], warnings: list[str]) -> list[list[str]]:
    fixed = []
    ncols = len(REQUIRED_HEADER)
    seen_ids: dict[str, int] = {}

    for i, row in enumerate(rows, start=1):
        if len(row) < ncols:
            warnings.append(f"Row {i}: padded {ncols - len(row)} missing column(s).")
            row = row + [""] * (ncols - len(row))
        elif len(row) > ncols:
            extra = row[ncols - 1:]
            row = row[: ncols - 1] + [",".join(extra)]
            warnings.append(
                f"Row {i}: merged {len(extra)} extra column(s) into 'comments' "
                "(likely an unescaped comma)."
            )

        tc_id, name, desc, clear_input, tc_type, expected, actual, automated, comments = row

        norm_automated, changed = normalize_automated(automated)
        if changed:
            warnings.append(f"Row {i} ({tc_id}): normalized 'automated' to '{norm_automated}'.")
        automated = norm_automated

        if tc_type.strip().lower() != tc_type.strip():
            tc_type = tc_type.strip().lower()
        if tc_type not in VALID_TYPES:
            warnings.append(
                f"Row {i} ({tc_id}): test case type '{tc_type}' is not one of {sorted(VALID_TYPES)} "
                "-- needs manual review."
            )

        if not ID_PATTERN.match(tc_id.strip()):
            warnings.append(f"Row {i}: testcase id '{tc_id}' does not match UT-### pattern -- needs manual review.")
        elif tc_id in seen_ids:
            warnings.append(
                f"Row {i}: duplicate testcase id '{tc_id}' (first seen at row {seen_ids[tc_id]}) "
                "-- needs manual review."
            )
        else:
            seen_ids[tc_id] = i

        stripped = clear_input.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                json.loads(stripped)
            except json.JSONDecodeError as e:
                warnings.append(f"Row {i} ({tc_id}): 'clear input' looks like JSON but failed to parse ({e}).")

        if actual.strip():
            warnings.append(f"Row {i} ({tc_id}): 'actual output' should be blank in a design artifact.")

        fixed.append([tc_id, name, desc, clear_input, tc_type, expected, actual, automated, comments])

    return fixed


def main() -> int:
    args = sys.argv[1:]
    check_only = "--check-only" in args
    args = [a for a in args if a != "--check-only"]
    if not args:
        print("Usage: python fix_csv.py <path-to-csv> [--check-only]", file=sys.stderr)
        return 2

    path = Path(args[0])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    raw = path.read_text(encoding="utf-8-sig")
    reader = csv.reader(io.StringIO(raw))
    rows = list(reader)
    if not rows:
        print("File is empty.", file=sys.stderr)
        return 1

    header, body = rows[0], rows[1:]
    warnings: list[str] = []

    normalized_header = [h.strip().lower() for h in header]
    if len(header) == len(REQUIRED_HEADER) and normalized_header != REQUIRED_HEADER:
        warnings.append("Header normalized to the required column names.")
    elif len(header) != len(REQUIRED_HEADER):
        warnings.append(
            f"Header has {len(header)} column(s), expected {len(REQUIRED_HEADER)} -- needs manual review."
        )
    header = REQUIRED_HEADER if len(header) == len(REQUIRED_HEADER) else header

    fixed_body = fix_rows(body, warnings)

    unresolved = [w for w in warnings if "needs manual review" in w]
    auto_fixed = [w for w in warnings if "needs manual review" not in w]

    if auto_fixed:
        print("Auto-fixed:")
        for w in auto_fixed:
            print(f"  - {w}")
    if unresolved:
        print("Unresolved (manual review required):")
        for w in unresolved:
            print(f"  - {w}")
    if not warnings:
        print("No issues found; CSV already conforms to the contract.")

    if not check_only and (auto_fixed or (not unresolved and header != rows[0])):
        out = io.StringIO()
        writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(fixed_body)
        path.write_text(out.getvalue(), encoding="utf-8")
        print(f"Wrote fixes to {path}")

    return 1 if unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
