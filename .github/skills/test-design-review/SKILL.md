---
name: test-design-review
description: 'Review a unit test design CSV (e.g. docs/ut-design/unit-test-design.csv) for requirement traceability, coverage gaps, and quality issues. Use when the user asks to review, audit, critique, or quality-gate a test case matrix or design artifact before implementation.'
argument-hint: 'Provide the test design CSV path and the requirements/code it should trace to.'
---

# Test Design Review

Review an existing unit test design CSV against its source requirements/code and report findings. This is a **read-only review** — do not edit the CSV or fix issues unless the user explicitly asks for that as a follow-up.

## When to Use
- The user asks to review, audit, critique, or sanity-check a test design CSV.
- The user asks whether test coverage is complete against requirements before automation starts.
- The user wants a quality gate on `docs/ut-design/unit-test-design.csv` or a similar artifact.

## Procedure

1. **Locate inputs.** Find the test design CSV (user-specified path, or default to `docs/ut-design/unit-test-design.csv`) and the requirements/code it should trace to.
2. **Check schema conformance first.** Run the ut-design validator in check-only mode so formatting issues are separated from content issues:
   ```
   python .github/skills/ut-design/scripts/fix_csv.py <path> --check-only
   ```
   Report any output verbatim as schema findings before moving to semantic review.
3. **Build a traceability map.** List every requirement/behavior (e.g. each FR, acceptance criterion) and which test case IDs cover it. Call out any requirement with zero coverage.
4. **Assess case quality for each covered requirement:**
   - Missing positive, negative, edge, or exception cases where the requirement warrants them.
   - `expected output` that is vague, contradicts the requirement, or is `TBD` without a stated blocking reason in `comments`.
   - Redundant or duplicate cases that exercise the same behavior without adding coverage.
   - `clear input` that doesn't match the scenario described in `test description`.
   - `test case type` misclassified relative to the scenario.
   - `automated` marked `yes` for cases that realistically can't be automated (non-deterministic, external system dependency) or marked `no` when they clearly could be.
5. **Do not fix silently.** Report findings only. If the user asks you to apply fixes after reviewing, hand schema-level fixes to the ut-design skill/script and make content-level fixes as explicit, separate edits.

## Output Format

Report, in order:
1. **Summary** — case count, requirement coverage percentage, overall verdict (ready / needs work / blocked).
2. **Schema issues** — validator output, if any.
3. **Traceability gaps** — table of requirement → covering case IDs → status (covered / partial / missing).
4. **Quality findings** — grouped by severity (blocker / major / minor / nit), each citing the specific case ID(s) and the reasoning.
5. **Recommendations** — concrete next steps, phrased as suggestions, not applied edits.

## Boundaries
- Read-only: never modify the CSV or source files as part of a review.
- Ground every finding in the actual CSV/requirements content; don't invent requirements that aren't documented.
- If requirements are themselves ambiguous or incomplete (e.g. undefined thresholds), say so rather than guessing at what "complete" coverage would mean.
