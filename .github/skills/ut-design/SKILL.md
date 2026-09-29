---
name: ut-design
description: 'Design or update requirement-traceable unit test cases as a CSV artifact from requirements or code. Use for unit test design, test case matrices, test coverage planning, or generating/fixing docs/ut-design/unit-test-design.csv.'
argument-hint: 'Provide the requirements, feature, or code under test, plus any preferred output path.'
---

# Unit Test Design

Create or update a maintainable, requirement-traceable unit test case design saved as a CSV artifact. This skill produces test **designs** only; it does not implement tests or change application code.

## When to Use
- The user asks to design, plan, or extend unit test cases for a requirement, feature, or piece of code.
- The user asks to create, update, or fix a unit test design CSV (e.g. `docs/ut-design/unit-test-design.csv`).
- The user reports that a test design CSV fails validation (malformed rows, bad quoting, wrong header).

## Procedure

1. **Gather context.** Identify the target behavior and inspect the relevant requirements, source code, nearby tests, and any existing design artifact under `docs/ut-design/`. Prefer repository evidence over assumptions.
2. **Derive test cases.** Map each case to a requirement or observable behavior. Include meaningful success, failure, missing/invalid-data, and boundary scenarios where applicable. Use parameterized cases when variations exercise the same rule.
3. **Do not invent unstated facts.** If the sources don't define an expected result, limit, unit, or exception contract, mark the case as unresolved/TBD in `expected output` or `comments` and state what clarification is needed.
4. **Write the CSV.** Use the user-provided path when given; otherwise reuse the repository's existing design-file location, or default to `docs/ut-design/unit-test-design.csv`. Preserve valid existing coverage, avoid duplicate cases, and keep IDs unique and sequential where practical. Follow the [CSV Contract](#csv-contract) below.
5. **Validate and auto-fix.** Run the [CSV fixer script](./scripts/fix_csv.py) against the saved file:
   ```
   python .github/skills/ut-design/scripts/fix_csv.py <path-to-csv>
   ```
   The script parses the CSV, normalizes formatting, and rewrites the file with fixes applied automatically. Re-run it after any manual edit. If it reports unresolved issues, fix those manually and re-run until it exits clean.

## CSV Contract

Columns, in this exact order:

`testcase id,testcase name,test description,clear input,test case type,expected output,actual output,automated,comments`

- **testcase id**: unique, sequential, e.g. `UT-001`.
- **testcase name**: short, descriptive, snake_case or similar.
- **test description**: what the case verifies and why.
- **clear input**: concrete input/condition; use JSON literals for structured payloads.
- **test case type**: `positive`, `negative`, `edge`, `boundary`, `exception`, or `exhaustive`.
- **expected output**: expected value/status/behavior, or `TBD` with a comment explaining what's blocking it.
- **actual output**: leave blank; this is a design artifact.
- **automated**: lowercase `yes` or `no`.
- **comments**: coverage notes, risk, or rationale.

Escape fields per standard CSV rules: quote any field containing a comma, quote, or newline, and double embedded quotes.

## Boundaries
- Design cases from stated requirements and observed behavior; don't force a case where it isn't relevant.
- Focus on behavioral outcomes and relevant side effects, not implementation details.
- Don't add speculative scenarios for integrations or failure modes unsupported by the target system.
- Preserve the user's existing work and unrelated files.

## Completion
Report the artifact path, approximate case count, and any unresolved requirement decisions. Don't dump the entire CSV into the chat response unless explicitly asked — the saved file is the deliverable.
