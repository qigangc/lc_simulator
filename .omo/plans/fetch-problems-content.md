# Fetch Full LeetCode Problem Content

## TL;DR

> **Quick Summary**: Fetch full problem descriptions, constraints, and examples (English + Chinese) from LeetCode's public GraphQL API and save them into all 100 `problems/*.json` files. Preserve all existing fields and executable test cases.
>
> **Deliverables**:
> - `scripts/fetch_content.py` — fetch script with dry-run, backup, caching
> - All 100 `problems/*.json` updated with `description_en`, `description_zh`, `constraints`, `leetcode_examples`
> - `tests/test_fetch.py` — fetch script unit tests
> - Validation that existing CLI (`lc list`, `lc show`, `lc test`) still works
>
> **Estimated Effort**: Medium
> **Parallel Execution**: NO — sequential API calls + dependent validation
> **Critical Path**: Script prototype → batch fetch → validation → CLI regression

---

## Context

### Original Request
User wants to save full problem content (description, constraints, examples) for all 100 LeetCode Hot 100 problems in both English and Chinese, matching the LeetCode website.

### Interview Summary
**Key Decisions**:
- **Field naming**: New LeetCode text examples go to `leetcode_examples`; existing `examples` (executable test cases) preserved
- **HTML format**: Store as Markdown (preserves code blocks with backticks)
- **Missing Chinese**: Fallback to English description if `translatedContent` is null
- **Test strategy**: Tests-after for fetch script; existing CLI tests must continue to pass

**Research Findings**:
- LeetCode GraphQL API is public at `https://leetcode.com/graphql`
- Query: `questionData($titleSlug: String!)` returns `content` (EN HTML), `translatedContent` (ZH HTML), `constraints`, `exampleTestcases`
- API requires no auth for free problems
- Rate limiting: recommend 2s delay between requests

### Metis Review
**Identified Gaps** (addressed):
- Field naming collision resolved (`leetcode_examples` vs existing `examples`)
- HTML format decided (Markdown)
- Backup/idempotency/dry-run requirements incorporated
- Rate limiting with exponential backoff specified

### Momus Review (High-Accuracy Mode)
**Verdict**: OKAY
**Date**: 2026-06-22
**Findings**: All referenced files exist and match plan assumptions. 100 problem files and 20 files with existing `examples` confirmed. Tasks have clear starting points, concrete deliverables, and executable QA scenarios. No contradictions or missing references.
**Approved with note**: HTML-to-Markdown dependency (`markdownify`) explicitly approved for this task.

---

## Work Objectives

### Core Objective
Write a robust Python script that calls LeetCode's GraphQL API for all 100 problem slugs, converts HTML descriptions to Markdown, and updates each `problems/*.json` with `description_en`, `description_zh`, `constraints`, and `leetcode_examples` — without breaking existing executable test cases or CLI behavior.

### Concrete Deliverables
- `scripts/fetch_content.py` — idempotent fetch script
- `cache/` directory — raw API response cache
- `problems_backup/` directory — pre-run JSON backups
- All 100 `problems/*.json` files updated with new fields
- `tests/test_fetch.py` — unit tests for fetch logic

### Definition of Done
- [ ] `python scripts/fetch_content.py --dry-run` previews changes without writing
- [ ] `python scripts/fetch_content.py` fetches all 100 problems successfully
- [ ] Every `problems/*.json` contains `description_en`, `description_zh`, `constraints`, `leetcode_examples`
- [ ] Existing `examples` field (executable test cases) preserved in all 20 files that have it
- [ ] `python -m lc list` works
- [ ] `python -m lc show 1` displays URL without crashing
- [ ] `python -m lc test 1` runs test cases without crashing
- [ ] `python -m unittest discover -s tests -v` passes all tests

### Must Have
- All 100 problems fetched and saved
- HTML converted to Markdown (not raw HTML or plain text)
- Chinese description falls back to English when unavailable
- Existing executable `examples` preserved exactly
- Backup created before any mutation
- Dry-run mode supported
- Cache of raw API responses
- Rate limiting (2s base delay + exponential backoff)

### Must NOT Have (Guardrails)
- MUST NOT overwrite existing `examples` executable test cases
- MUST NOT modify `function`, `categories`, `difficulty`, `title_*`, `url`, `id`, `slug` fields
- MUST NOT add new Python package dependencies to `pyproject.toml` without approval
- MUST NOT fetch hints, solutions, code snippets, tags, likes, discuss counts
- MUST NOT write a general-purpose LeetCode client library
- MUST NOT leave partial file writes on failure

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (unittest)
- **Automated tests**: Tests-after
- **Framework**: stdlib `unittest`
- **Agent-Executed QA**: MANDATORY for all tasks

### QA Policy
Every task MUST include agent-executed QA scenarios. Evidence saved to `.omo/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Script validation**: Bash — run script, check exit code, verify JSON content
- **CLI regression**: Bash — run `lc list`, `lc show`, `lc test`, capture output
- **Content validation**: Bash — `python -c` to assert field presence and length

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation — script skeleton + utilities):
├── Task 1: Create fetch script skeleton + GraphQL client
├── Task 2: Add HTML-to-Markdown converter
├── Task 3: Add JSON update logic with backup/dry-run
├── Task 4: Add rate limiting + retry + caching
└── Task 5: Write unit tests for fetch utilities

Wave 2 (Core — prototype + batch + validation):
├── Task 6: Prototype fetch on 3 problems and inspect output
├── Task 7: Run full batch fetch for all 100 problems
├── Task 8: Write and run content validation script
└── Task 9: CLI regression test (list, show, test)

Wave FINAL (4 parallel reviews):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 4 → Task 6 → Task 7 → Task 8 → Task 9 → F1-F4 → user okay
```

### Agent Dispatch Summary

- **Wave 1**: 5 tasks — quick for script skeleton, quick for converter, quick for JSON logic, quick for rate limit, quick for tests
- **Wave 2**: 4 tasks — unspecified-high for prototype, unspecified-high for batch, quick for validation, unspecified-high for CLI regression
- **FINAL**: 4 tasks — oracle, unspecified-high, unspecified-high, deep

---

## TODOs

- [x] 1. **Create fetch script skeleton and GraphQL client**

  **What to do**:
  - Create `scripts/fetch_content.py` with argparse for `--dry-run`, `--backup`, `--force`, `--limit`
  - Implement `fetch_problem(slug)` that POSTs GraphQL query to `https://leetcode.com/graphql`
  - Query: `questionData($titleSlug: String!)` requesting `content`, `translatedContent`, `constraints`, `exampleTestcases`
  - Return raw dict or None on failure
  - Create `cache/` directory if missing; cache raw JSON responses by slug
  - Add logging for every request

  **Must NOT do**:
  - Do NOT parse HTML yet
  - Do NOT write to problem JSONs yet

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: Script scaffolding, single file

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 2-5)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 6 (prototype)
  - **Blocked By**: None

  **References**:
  - `lc/paths.py` — use `PROBLEMS_DIR` for globbing
  - LeetCode GraphQL: `https://leetcode.com/graphql`

  **Acceptance Criteria**:
  - [ ] `python scripts/fetch_content.py --help` shows all arguments
  - [ ] `python -c "from scripts.fetch_content import fetch_problem; print(fetch_problem('two-sum'))"` returns a dict with keys `content`, `translatedContent`, `constraints`, `exampleTestcases`
  - [ ] Cache file created at `cache/two-sum.json` after first call
  - [ ] Second call reads from cache, no network request

  **QA Scenarios**:
  ```
  Scenario: Fetch problem data from API
    Tool: Bash (python -c)
    Steps:
      1. python -c "from scripts.fetch_content import fetch_problem; r=fetch_problem('two-sum'); print('content' in r, 'translatedContent' in r)"
    Expected Result: Output contains `True True`
    Evidence: .omo/evidence/task-1-fetch-two-sum.txt

  Scenario: Cache hit on second fetch
    Tool: Bash
    Steps:
      1. ls cache/two-sum.json (should exist after first call)
    Expected Result: File exists
    Evidence: .omo/evidence/task-1-cache-hit.txt
  ```

  **Commit**: YES
  - Message: `feat: add LeetCode content fetch script skeleton`
  - Files: `scripts/fetch_content.py`

- [x] 2. **Add HTML-to-Markdown converter**

  **What to do**:
  - Install `markdownify` (converts HTML to Markdown) or use `html2text`
  - Implement `html_to_markdown(html_str)` function
  - Handle `<pre><code>` blocks → fenced code blocks with backticks
  - Handle `<sup>` → plain text (remove superscript markers)
  - Handle `<strong>`, `<em>` → Markdown bold/italic
  - Strip images (`<img>`) and replace with `[image]` placeholder
  - Test on `two-sum` and `median-of-two-sorted-arrays` HTML

  **Must NOT do**:
  - Do NOT store raw HTML in JSON
  - Do NOT strip all formatting (must preserve code blocks)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: Single utility function

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 1, 3-5)
  - **Parallel Group**: Wave 1

  **Acceptance Criteria**:
  - [ ] `html_to_markdown("<p>Given <code>nums</code></p>")` returns `"Given `nums`"`
  - [ ] `html_to_markdown("<pre><code>class Solution:</code></pre>")` contains fenced code block
  - [ ] Output for `two-sum` has > 100 characters and contains backticks

  **QA Scenarios**:
  ```
  Scenario: Convert LeetCode HTML to Markdown
    Tool: Bash (python -c)
    Steps:
      1. python -c "from scripts.fetch_content import html_to_markdown; print(html_to_markdown('<p>Hello <code>world</code></p>'))"
    Expected Result: Output contains backticks around `world`
    Evidence: .omo/evidence/task-2-html-to-md.txt
  ```

  **Commit**: YES (groups with Task 1)

- [x] 3. **Add JSON update logic with backup and dry-run**

  **What to do**:
  - Implement `update_problem_json(path, data)` that:
    1. Reads existing JSON
    2. Extracts `content` → `description_en` (via html_to_markdown)
    3. Extracts `translatedContent` → `description_zh` (fallback to `description_en` if null)
    4. Extracts `constraints` → `constraints` (html_to_markdown)
    5. Extracts `exampleTestcases` → `leetcode_examples` (parse newline-separated string into array)
    6. Adds new fields without modifying existing ones
    7. Writes back with `indent=4`, `ensure_ascii=False`
  - Backup: copy original to `problems_backup/{filename}` before writing
  - Dry-run: print intended changes but do not write

  **Must NOT do**:
  - Do NOT modify `examples`, `function`, `tests`, or any existing field
  - Do NOT write if `--dry-run` is set

  **Recommended Agent Profile**:
  - **Category**: `quick`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 1-2, 4-5)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 6 (prototype)

  **Acceptance Criteria**:
  - [ ] `--dry-run` prints "Would update problems/001_two-sum.json: add description_en (length=...), description_zh, constraints, leetcode_examples"
  - [ ] Without `--dry-run`, backup file created at `problems_backup/001_two-sum.json`
  - [ ] Updated JSON preserves all original fields
  - [ ] New fields added with correct structure

  **QA Scenarios**:
  ```
  Scenario: Dry-run shows intended changes
    Tool: Bash
    Steps:
      1. python scripts/fetch_content.py --dry-run --limit 1
    Expected Result: Output shows "Would update" but file unchanged
    Evidence: .omo/evidence/task-3-dry-run.txt

  Scenario: Backup created on write
    Tool: Bash
    Steps:
      1. python scripts/fetch_content.py --limit 1
      2. ls problems_backup/001_two-sum.json
    Expected Result: Backup file exists
    Evidence: .omo/evidence/task-3-backup.txt
  ```

  **Commit**: YES (groups with Tasks 1-2)

- [x] 4. **Add rate limiting, retry, and caching**

  **What to do**:
  - Rate limit: 2-second delay between requests
  - Exponential backoff on HTTP 429/5xx: 2s, 4s, 8s, max 30s
  - Jitter: add random 0-1s to backoff
  - Timeout: 10s per request
  - Cache: save raw GraphQL response to `cache/{slug}.json`
  - If cache exists and not `--force`, skip network call
  - Log every request with timestamp, slug, status

  **Must NOT do**:
  - Do NOT hammer the API without delays
  - Do NOT ignore network errors silently

  **Recommended Agent Profile**:
  - **Category**: `quick`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 1-3, 5)
  - **Parallel Group**: Wave 1

  **Acceptance Criteria**:
  - [ ] Two consecutive calls to `fetch_problem` take >= 2 seconds total
  - [ ] HTTP 429 triggers retry with backoff
  - [ ] Cache hit skips network entirely

  **QA Scenarios**:
  ```
  Scenario: Rate limiting enforces delay
    Tool: Bash (time)
    Steps:
      1. time python -c "from scripts.fetch_content import fetch_problem; fetch_problem('two-sum'); fetch_problem('add-two-numbers')"
    Expected Result: Real time >= 2 seconds
    Evidence: .omo/evidence/task-4-rate-limit.txt
  ```

  **Commit**: YES (groups with Tasks 1-3)

- [x] 5. **Write unit tests for fetch utilities**

  **What to do**:
  - Create `tests/test_fetch.py`
  - Test `html_to_markdown` with various HTML snippets
  - Test `update_problem_json` with mock data
  - Test rate limiting behavior (mock time)
  - Test cache hit/miss logic
  - Test dry-run doesn't write files

  **Must NOT do**:
  - Do NOT make real network calls in tests (mock requests)

  **Recommended Agent Profile**:
  - **Category**: `quick`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 1-4)
  - **Parallel Group**: Wave 1

  **Acceptance Criteria**:
  - [ ] `python -m unittest tests.test_fetch -v` passes all tests
  - [ ] Coverage includes html_to_markdown, update_problem_json, cache logic

  **QA Scenarios**:
  ```
  Scenario: Unit tests pass
    Tool: Bash
    Steps:
      1. python -m unittest discover -s tests -v -k test_fetch
    Expected Result: All tests pass
    Evidence: .omo/evidence/task-5-unit-tests.txt
  ```

  **Commit**: YES (groups with Tasks 1-4)

- [x] 6. **Prototype fetch on 3 problems and inspect output**

  **What to do**:
  - Run script on `two-sum` (001), `median-of-two-sorted-arrays` (004), `word-ladder` (100)
  - Inspect generated Markdown for each:
    - Check code blocks are fenced with backticks
    - Check Chinese translation is present or falls back to English
    - Check constraints are captured
    - Check leetcode_examples is an array of strings
  - Verify JSON is valid and preserves existing fields
  - If issues found, fix script before full batch

  **Must NOT do**:
  - Do NOT proceed to full batch if prototype has issues

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Reason**: Requires judgment on data quality

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocked By**: Tasks 1-5
  - **Blocks**: Task 7 (full batch)

  **Acceptance Criteria**:
  - [ ] `problems/001_two-sum.json` contains `description_en` with length > 100
  - [ ] `problems/001_two-sum.json` contains `description_zh` (or fallback English)
  - [ ] `problems/001_two-sum.json` contains `constraints` as non-empty string
  - [ ] `problems/001_two-sum.json` contains `leetcode_examples` as array
  - [ ] Existing `examples` field unchanged (if present)

  **QA Scenarios**:
  ```
  Scenario: Prototype produces valid content
    Tool: Bash (python -c)
    Steps:
      1. python scripts/fetch_content.py --limit 3
      2. python -c "import json; d=json.load(open('problems/001_two-sum.json')); print(len(d['description_en'])>100, 'constraints' in d, isinstance(d['leetcode_examples'], list))"
    Expected Result: `True True True`
    Evidence: .omo/evidence/task-6-prototype.txt
  ```

  **Commit**: NO (prototype data; will batch commit after Task 7)

- [x] 7. **Run full batch fetch for all 100 problems**

  **What to do**:
  - Run `python scripts/fetch_content.py` (no --limit)
  - Monitor for failures (network errors, missing fields, parse errors)
  - Log all failures with problem ID and error message
  - Retry failed problems manually if needed
  - Verify all 100 cache files exist

  **Must NOT do**:
  - Do NOT proceed if > 5 problems fail

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Reason**: Long-running batch, requires monitoring

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocked By**: Task 6
  - **Blocks**: Task 8 (validation)

  **Acceptance Criteria**:
  - [ ] Script exits with code 0
  - [ ] All 100 `problems/*.json` files updated
  - [ ] All 100 `cache/*.json` files exist
  - [ ] Failure count <= 5 (if any, retry separately)

  **QA Scenarios**:
  ```
  Scenario: Full batch completes successfully
    Tool: Bash
    Steps:
      1. python scripts/fetch_content.py
      2. echo $?
    Expected Result: Exit code 0
    Evidence: .omo/evidence/task-7-batch.txt

  Scenario: All files updated
    Tool: Bash
    Steps:
      1. python -c "import json, glob; files=glob.glob('problems/*.json'); print(all('description_en' in json.load(open(f)) for f in files))"
    Expected Result: `True`
    Evidence: .omo/evidence/task-7-all-updated.txt
  ```

  **Commit**: YES
  - Message: `feat: populate all 100 problems with LeetCode content`
  - Files: `problems/*.json`, `cache/`

- [x] 8. **Write and run content validation script**

  **What to do**:
  - Create `scripts/validate_content.py` that checks:
    1. Every file has `description_en` (length > 50)
    2. Every file has `description_zh` (length > 50 or equals `description_en`)
    3. Every file has `constraints` (non-empty)
    4. Every file has `leetcode_examples` (non-empty list)
    5. Existing `examples` preserved (if present before, still present and identical)
    6. No other fields were modified
  - Print statistics: success count, failure count, details of failures
  - Exit non-zero if any check fails

  **Must NOT do**:
  - Do NOT modify files during validation

  **Recommended Agent Profile**:
  - **Category**: `quick`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocked By**: Task 7
  - **Blocks**: Task 9

  **Acceptance Criteria**:
  - [ ] Validation script exits 0
  - [ ] 100/100 files pass all checks
  - [ ] Existing `examples` in 20 files are bit-for-bit identical to backups

  **QA Scenarios**:
  ```
  Scenario: Validation passes
    Tool: Bash
    Steps:
      1. python scripts/validate_content.py
    Expected Result: Exit code 0, output shows "100/100 passed"
    Evidence: .omo/evidence/task-8-validation.txt
  ```

  **Commit**: YES (groups with Task 7)

- [x] 9. **CLI regression test (list, show, test)**

  **What to do**:
  - Run `python -m lc list` — verify no crash, 100 problems shown
  - Run `python -m lc show 1` — verify no crash, URL shown
  - Run `python -m lc test 1` — verify "missing solution file" (not crash)
  - Run `python -m unittest discover -s tests -v` — all 7+ tests pass
  - If any CLI command crashes, investigate and fix

  **Must NOT do**:
  - Do NOT ignore crashes

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocked By**: Task 8

  **Acceptance Criteria**:
  - [ ] `lc list` runs without traceback
  - [ ] `lc show 1` runs without traceback
  - [ ] `lc test 1` reports "missing solution file" without traceback
  - [ ] All unittest tests pass

  **QA Scenarios**:
  ```
  Scenario: CLI list works
    Tool: Bash
    Steps:
      1. python -m lc list | head -5
    Expected Result: Shows problem table, no traceback
    Evidence: .omo/evidence/task-9-cli-list.txt

  Scenario: CLI show works
    Tool: Bash
    Steps:
      1. python -m lc show 1
    Expected Result: Shows problem metadata including URL, no traceback
    Evidence: .omo/evidence/task-9-cli-show.txt

  Scenario: CLI test works
    Tool: Bash
    Steps:
      1. python -m lc test 1
    Expected Result: "missing solution file: ...", no traceback
    Evidence: .omo/evidence/task-9-cli-test.txt

  Scenario: All unit tests pass
    Tool: Bash
    Steps:
      1. python -m unittest discover -s tests -v
    Expected Result: All tests pass
    Evidence: .omo/evidence/task-9-unit-tests.txt
  ```

  **Commit**: YES (groups with Tasks 7-8)

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle`

  **Result**: VERDICT: APPROVE
  - Must Have: 8/8 implemented (description_en, description_zh, constraints, leetcode_examples in all 100 files; HTML→Markdown; Chinese fallback; existing examples preserved; backup; dry-run; cache; rate limiting)
  - Must NOT Have: 6/6 compliant (no examples overwritten, no existing fields modified, no new dependencies without approval, no hints/solutions fetched, no general-purpose library, no partial writes)
  - Tasks: 9/9 completed
  - Evidence files present in .omo/evidence/
  - Validation: 100/100 passed
  - Unit tests: 48/48 passed
  - CLI regression: list/show/test all work without crashing

  **Recommended Agent Profile**:
  - **Category**: `oracle`
  - **Reason**: Read-only verification of plan against implementation

  **Parallelization**:
  - **Can Run In Parallel**: YES (with F2-F4)
  - **Parallel Group**: Wave FINAL

  Read the plan end-to-end. Verify all "Must Have" items are implemented (description_en, description_zh, constraints, leetcode_examples in all 100 files). Verify "Must NOT Have" guardrails (no examples overwritten, no existing fields modified). Check evidence files exist in `.omo/evidence/`.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`

  **Result**: VERDICT: APPROVE
  - Code: PASS
  - scripts/fetch_content.py has robust error handling, rate limiting with exponential backoff, HTML parsing via markdownify, comprehensive logging
  - scripts/validate_content.py checks all 6 required integrity checks
  - tests/test_fetch.py has 41 tests covering all major functionality
  - No hardcoded secrets, no debug logging left in production paths
  - Issues: 0

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Reason**: Review script quality, error handling, logging

  **Parallelization**:
  - **Can Run In Parallel**: YES (with F1, F3-F4)
  - **Parallel Group**: Wave FINAL

  Review `scripts/fetch_content.py` for: error handling, rate limiting, HTML parsing robustness, logging. Review `scripts/validate_content.py` for completeness. Check no hardcoded secrets, no debug logging in production paths.
  Output: `Code [PASS/FAIL] | Issues [N] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`

  **Result**: VERDICT: APPROVE
  - Scenarios: 9/9 pass (dry-run, backup, list, show, test, unit tests, validation, prototype, batch)
  - Content Quality: PASS
  - Random spot-check of problems 001, 004, 010, 100 show readable Markdown with fenced code blocks
  - Chinese descriptions present where available, fallback to English where not
  - All CLI commands run without traceback
  - Evidence files present in .omo/evidence/

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Reason**: Hands-on execution of all QA scenarios

  **Parallelization**:
  - **Can Run In Parallel**: YES (with F1-F2, F4)
  - **Parallel Group**: Wave FINAL

  Start from clean state. Run `python scripts/fetch_content.py --dry-run` first. Then run full fetch. Execute all QA scenarios from Tasks 6-9. Verify 3 random problems have readable Markdown descriptions with code blocks. Verify Chinese descriptions are present or fallback to English.
  Output: `Scenarios [N/N pass] | Content Quality [PASS/FAIL] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`

  **Result**: VERDICT: APPROVE
  - Tasks: 9/9 compliant (all spec items built exactly as specified, nothing beyond spec)
  - Data Integrity: PASS
  - All 100 problems/*.json contain new fields without modifying existing ones
  - Existing `examples` fields preserved in all 20 files that had them
  - No existing fields (function, categories, difficulty, title_*, url, id, slug) were modified
  - Must NOT do guardrails: 6/6 compliant

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Reason**: Deep inspection of diffs vs plan requirements

  **Parallelization**:
  - **Can Run In Parallel**: YES (with F1-F3)
  - **Parallel Group**: Wave FINAL

  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built, nothing beyond spec was built. Check "Must NOT do" compliance. Verify no existing `examples` fields were modified in the 20 files that had them.
  Output: `Tasks [N/N compliant] | Data Integrity [PASS/FAIL] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat: add LeetCode content fetch script with utilities and tests`
  - Files: `scripts/fetch_content.py`, `tests/test_fetch.py`
  - Pre-commit: `python -m py_compile scripts/fetch_content.py && python -m unittest tests.test_fetch -v`

- **Wave 2**: `feat: populate all 100 problems with LeetCode content`
  - Files: `problems/*.json`, `cache/`, `scripts/validate_content.py`
  - Pre-commit: `python scripts/validate_content.py && python -m unittest discover -s tests -v`

---

## Success Criteria

### Verification Commands
```bash
# After Wave 1
python -m py_compile scripts/fetch_content.py
python -m unittest tests.test_fetch -v

# After Wave 2
python scripts/validate_content.py
python -m unittest discover -s tests -v
python -m lc list
python -m lc show 1
python -m lc test 1
```

### Final Checklist
- [ ] All 100 `problems/*.json` contain `description_en`, `description_zh`, `constraints`, `leetcode_examples`
- [ ] Existing `examples` fields preserved (20 files unchanged)
- [ ] `description_zh` falls back to English when Chinese unavailable
- [ ] Descriptions are Markdown (contain backticks for code)
- [ ] `leetcode_examples` is a non-empty array of strings
- [ ] `python -m lc list/show/test` all work without crashing
- [ ] All unit tests pass
- [ ] Backup directory `problems_backup/` exists with original files
- [ ] Cache directory `cache/` exists with raw API responses
