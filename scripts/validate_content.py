"""
validate_content.py - Validate all 100 problems/*.json files have correct new fields.

Checks:
1. Every file has description_en (length > 50)
2. Every file has description_zh (length > 50 or equals description_en)
3. Every file has constraints (non-empty string)
4. Every file has leetcode_examples (non-empty list)
5. Existing examples preserved (if present in backup, identical)
6. No extra fields beyond expected set

Usage: python scripts/validate_content.py
Exit 0 if all pass, 1 otherwise.
"""

import json
import sys
from pathlib import Path

PROBLEMS_DIR = Path("problems")
BACKUP_DIR = Path("problems_backup")

# Fields that existed before the fetch (the "original" schema)
ORIGINAL_FIELDS = {"id", "slug", "title_en", "title_zh", "difficulty",
                   "categories", "function", "url"}

# Fields added by the fetch
NEW_FIELDS = {"description_en", "description_zh", "constraints", "leetcode_examples"}

# Fields that some files originally had (001-020)
OPTIONAL_ORIGINAL_FIELDS = {"examples"}

ALL_KNOWN_FIELDS = ORIGINAL_FIELDS | NEW_FIELDS | OPTIONAL_ORIGINAL_FIELDS


def get_problem_number(filepath: Path) -> int:
    """Extract problem number from filename like '001_two-sum.json'."""
    return int(filepath.stem.split("_")[0])


def load_json(filepath: Path, encoding: str = "utf-8-sig") -> dict | None:
    """Load a JSON file, returning None on failure."""
    try:
        with open(filepath, encoding=encoding) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None


def check_new_fields(data: dict, filename: str, errors: list) -> None:
    """Check that all new fields exist and are valid."""
    # 1. description_en: exists, length > 50
    desc_en = data.get("description_en")
    if desc_en is None:
        errors.append(f"{filename}: missing 'description_en'")
    elif not isinstance(desc_en, str):
        errors.append(f"{filename}: 'description_en' is not a string")
    elif len(desc_en) <= 50:
        errors.append(f"{filename}: 'description_en' too short ({len(desc_en)} chars, need > 50)")

    # 2. description_zh: exists, length > 50 or equals description_en
    desc_zh = data.get("description_zh")
    if desc_zh is None:
        errors.append(f"{filename}: missing 'description_zh'")
    elif not isinstance(desc_zh, str):
        errors.append(f"{filename}: 'description_zh' is not a string")
    elif len(desc_zh) <= 50 and desc_zh != desc_en:
        errors.append(f"{filename}: 'description_zh' too short ({len(desc_zh)} chars) and not equal to description_en")

    # 3. constraints: non-empty string
    constraints = data.get("constraints")
    if constraints is None:
        errors.append(f"{filename}: missing 'constraints'")
    elif not isinstance(constraints, str):
        errors.append(f"{filename}: 'constraints' is not a string")
    elif len(constraints.strip()) == 0:
        errors.append(f"{filename}: 'constraints' is empty")

    # 4. leetcode_examples: non-empty list
    leetcode_examples = data.get("leetcode_examples")
    if leetcode_examples is None:
        errors.append(f"{filename}: missing 'leetcode_examples'")
    elif not isinstance(leetcode_examples, list):
        errors.append(f"{filename}: 'leetcode_examples' is not a list")
    elif len(leetcode_examples) == 0:
        errors.append(f"{filename}: 'leetcode_examples' is empty")


def check_examples_preserved(data: dict, backup_data: dict, filename: str, errors: list) -> None:
    """Check that the 'examples' field matches the backup (if present in backup)."""
    backup_examples = backup_data.get("examples")
    if backup_examples is None:
        # Backup doesn't have examples - this is expected for 021+
        return

    current_examples = data.get("examples")
    if current_examples is None:
        errors.append(f"{filename}: backup has 'examples' but current file is missing it")
    elif current_examples != backup_examples:
        errors.append(f"{filename}: 'examples' field differs from backup")


def check_no_extra_fields(data: dict, filename: str, errors: list) -> None:
    """Check that no unexpected fields were added."""
    extra = set(data.keys()) - ALL_KNOWN_FIELDS
    if extra:
        errors.append(f"{filename}: unexpected fields: {sorted(extra)}")


def main() -> int:
    problem_files = sorted(PROBLEMS_DIR.glob("*.json"))
    if not problem_files:
        print(f"ERROR: No JSON files found in {PROBLEMS_DIR}/")
        return 1

    total = len(problem_files)
    errors: list[str] = []
    warnings: list[str] = []
    passed = 0

    print(f"Validating {total} problem files...\n")

    for pf in problem_files:
        filename = pf.name
        prob_num = get_problem_number(pf)

        data = load_json(pf)
        if data is None:
            errors.append(f"{filename}: failed to load JSON")
            continue

        # Check new fields
        check_new_fields(data, filename, errors)

        # Check examples preserved against backup
        backup_path = BACKUP_DIR / pf.name
        backup_data = load_json(backup_path)
        if backup_data is None:
            warnings.append(f"{filename}: backup file not found or invalid, skipping examples check")
        else:
            check_examples_preserved(data, backup_data, filename, errors)

        # Check no extra fields
        check_no_extra_fields(data, filename, errors)

        # If no errors for this file, count as pass
        file_errors = [e for e in errors if e.startswith(f"{filename}:")]
        if not file_errors:
            passed += 1

    # Print summary
    failed = total - passed

    if warnings:
        print("--- Warnings ---")
        for w in warnings:
            print(f"  WARN: {w}")
        print()

    if errors:
        print("--- Errors ---")
        for e in errors:
            print(f"  FAIL: {e}")
        print()

    print(f"Results: {passed}/{total} passed, {failed}/{total} failed")

    if errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
