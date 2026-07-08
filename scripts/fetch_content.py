#!/usr/bin/env python3
"""
Fetch LeetCode problem content from GraphQL API and update problems/*.json files.

Usage:
    python scripts/fetch_content.py [--dry-run] [--backup] [--force] [--limit N]
"""

import argparse
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library is required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    from markdownify import markdownify as md
except ImportError:
    print("ERROR: 'markdownify' library is required. Install with: pip install markdownify", file=sys.stderr)
    sys.exit(1)


# --- Constants ---
from lc.config import (
    GRAPHQL_URL, REQUEST_TIMEOUT, RATE_LIMIT_DELAY,
    MAX_RETRY_BACKOFF, MAX_RETRY_ATTEMPTS, USER_AGENT,
    PROBLEMS_DIR_NAME, BACKUP_DIR_NAME, CACHE_DIR_NAME,
    PROBLEM_FILE_PATTERN,
)

PROBLEMS_DIR = Path(PROBLEMS_DIR_NAME)
BACKUP_DIR = Path(BACKUP_DIR_NAME)
CACHE_DIR = Path(CACHE_DIR_NAME)

GRAPHQL_QUERY = """
query questionData($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        content
        translatedContent
        exampleTestcases
    }
}
"""


# --- HTML to Markdown ---
def html_to_markdown(html_str: str) -> str:
    """Convert LeetCode HTML content to Markdown."""
    if not html_str:
        return ""

    # Handle <pre><code> blocks first — wrap in fenced code blocks
    # LeetCode often uses <pre><code> for code examples
    html_str = re.sub(
        r'<pre>\s*<code>([\s\S]*?)</code>\s*</pre>',
        r'```\n\1\n```',
        html_str,
    )

    # Handle standalone <pre> blocks
    html_str = re.sub(
        r'<pre>([\s\S]*?)</pre>',
        r'```\n\1\n```',
        html_str,
    )

    # Replace <sup> tags with plain text (markdownify doesn't handle them well)
    html_str = re.sub(r'<sup>([^<]*)</sup>', r'(\1)', html_str)

    # Replace <sub> tags similarly
    html_str = re.sub(r'<sub>([^<]*)</sub>', r'(\1)', html_str)

    # Replace <img> tags with [image] placeholder
    html_str = re.sub(r'<img[^>]*>', '[image]', html_str)

    # Convert to markdown
    result = md(
        html_str,
        heading_style="ATX",
        bullets="-",
        strip=["a", "style"],  # strip links (keep text), strip styles
    )

    # Clean up excessive whitespace
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = result.strip()

    return result


# --- GraphQL Fetch ---
def _read_cache(slug, cache_path):
    """Read cached API response for a slug. Returns dict or None."""
    if not cache_path.exists():
        return None
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            cached = json.load(f)
        log(slug, "CACHE_HIT")
        return cached
    except (json.JSONDecodeError, OSError) as e:
        log(slug, f"CACHE_READ_ERROR {e}")
        return None


def _save_cache(result, cache_path, slug):
    """Save a successful API response to the cache directory."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        log(slug, "OK")
    except OSError as e:
        log(slug, f"CACHE_WRITE_ERROR {e}")


def fetch_problem(slug: str, force: bool = False) -> dict | None:
    """Fetch problem data from LeetCode GraphQL API.

    Returns dict with keys: content, translatedContent, exampleTestcases
    Returns None on failure.
    """
    cache_path = CACHE_DIR / f"{slug}.json"

    if not force:
        cached = _read_cache(slug, cache_path)
        if cached is not None:
            return cached

    payload = {
        "operationName": "questionData",
        "variables": {"titleSlug": slug},
        "query": GRAPHQL_QUERY,
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }

    last_error = None
    backoff = RATE_LIMIT_DELAY

    for attempt in range(MAX_RETRY_ATTEMPTS):  # max attempts
        try:
            resp = requests.post(
                GRAPHQL_URL,
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            if resp.status_code == 200:
                data = resp.json()
                question = data.get("data", {}).get("question")
                if question is None:
                    log(slug, "EMPTY_RESPONSE")
                    return None

                result = {
                    "content": question.get("content"),
                    "translatedContent": question.get("translatedContent"),
                    "exampleTestcases": question.get("exampleTestcases"),
                }

                _save_cache(result, cache_path, slug)
                return result

            elif resp.status_code in (429,) or 500 <= resp.status_code < 600:
                # Rate limited or server error — backoff
                jitter = random.uniform(0, 1)
                sleep_time = min(backoff + jitter, MAX_RETRY_BACKOFF)
                log(slug, f"RETRY({resp.status_code}) sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
                backoff = min(backoff * 2, MAX_RETRY_BACKOFF)
                last_error = resp.status_code
                continue
            else:
                log(slug, f"HTTP_ERROR {resp.status_code}")
                return None

        except requests.exceptions.Timeout:
            log(slug, f"TIMEOUT (attempt {attempt + 1})")
            last_error = "timeout"
            time.sleep(min(backoff, MAX_RETRY_BACKOFF))
            backoff = min(backoff * 2, MAX_RETRY_BACKOFF)
            continue
        except requests.exceptions.RequestException as e:
            log(slug, f"NETWORK_ERROR {e}")
            return None

    log(slug, f"FAILED after {attempt + 1} attempts, last error: {last_error}")
    return None


def extract_constraints_from_html(html_str: str) -> str:
    """Extract constraints section from LeetCode problem HTML.

    Constraints are in a <ul> following 'Constraints:' text.
    """
    if not html_str:
        return ""
    # Find the constraints section: look for "Constraints:" followed by a <ul>
    match = re.search(
        r'Constraints:\s*</strong>\s*</p>\s*<ul>([\s\S]*?)</ul>',
        html_str,
        re.IGNORECASE,
    )
    if match:
        return "<ul>" + match.group(1) + "</ul>"
    return ""


# --- Update JSON ---
def update_problem_json(path: Path, data: dict) -> bool:
    """Update a problem JSON file with fetched content.

    Adds/updates: description_en, description_zh, constraints, leetcode_examples
    Does NOT touch: id, slug, title_en, title_zh, difficulty, categories, function, examples, url
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            problem = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  ERROR reading {path.name}: {e}", file=sys.stderr)
        return False

    # Extract content
    content_en = data.get("content") or ""
    content_zh = data.get("translatedContent") or content_en  # fallback to en

    description_en = html_to_markdown(content_en)
    description_zh = html_to_markdown(content_zh)

    # Constraints are embedded in the HTML content
    constraints_html = extract_constraints_from_html(content_en)
    constraints = html_to_markdown(constraints_html)

    # Example testcases: newline-separated string -> list of strings
    example_testcases_raw = data.get("exampleTestcases") or ""
    if example_testcases_raw.strip():
        leetcode_examples = [
            line.strip()
            for line in example_testcases_raw.split("\n")
            if line.strip()
        ]
    else:
        leetcode_examples = []

    # Update fields
    problem["description_en"] = description_en
    problem["description_zh"] = description_zh
    problem["constraints"] = constraints
    problem["leetcode_examples"] = leetcode_examples

    # Atomic write: write to temp file, then rename
    temp_path = path.with_suffix(".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(problem, f, indent=4, ensure_ascii=False)
        os.replace(temp_path, path)
    except OSError as e:
        print(f"  ERROR writing {path.name}: {e}", file=sys.stderr)
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()
        return False

    return True


# --- Backup ---
def backup_problem_json(path: Path) -> bool:
    """Copy original problem JSON to problems_backup/."""
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        backup_path = BACKUP_DIR / path.name
        # Read original
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        # Write backup
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except OSError as e:
        print(f"  ERROR backing up {path.name}: {e}", file=sys.stderr)
        return False


# --- Logging ---
def log(slug: str, status: str):
    """Print a timestamped log line."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {slug}: {status}")


# --- Slug extraction ---
def extract_slug(filename: str) -> str | None:
    """Extract slug from filename like '001_two-sum.json' -> 'two-sum'."""
    match = re.match(r"\d{3}_(.+)\.json$", filename)
    if match:
        return match.group(1)
    return None


# --- Main ---
def main():
    parser = argparse.ArgumentParser(
        description="Fetch LeetCode problem content from GraphQL API"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be updated without writing",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Backup original files to problems_backup/ before updating",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip cache and force re-fetch from API",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process the first N problems",
    )
    args = parser.parse_args()

    # Ensure directories exist
    PROBLEMS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Collect and sort problem files
    problem_files = sorted(PROBLEMS_DIR.glob(PROBLEM_FILE_PATTERN))

    if not problem_files:
        print("No problem files found.", file=sys.stderr)
        sys.exit(1)

    if args.limit is not None:
        problem_files = problem_files[: args.limit]

    total = len(problem_files)
    success_count = 0
    fail_count = 0

    print(f"Processing {total} problem(s)...")
    print()

    for i, path in enumerate(problem_files, 1):
        # Read slug from JSON file (more reliable than filename extraction)
        try:
            with open(path, "r", encoding="utf-8") as f:
                problem_data = json.load(f)
            slug = problem_data.get("slug")
        except (json.JSONDecodeError, OSError) as e:
            print(f"  SKIP {path.name}: could not read JSON ({e})", file=sys.stderr)
            fail_count += 1
            continue
        if not slug:
            print(f"  SKIP {path.name}: no slug field in JSON", file=sys.stderr)
            fail_count += 1
            continue

        print(f"[{i}/{total}] {path.name} -> slug='{slug}'")

        # Fetch data
        data = fetch_problem(slug, force=args.force)
        if data is None:
            fail_count += 1
            print(f"  SKIP: fetch failed for '{slug}'")
            print()
            continue

        # Dry-run mode
        if args.dry_run:
            desc_en_len = len(data.get("content") or "")
            has_zh = bool(data.get("translatedContent"))
            constraints_html = extract_constraints_from_html(data.get("content") or "")
            example_count = len((data.get("exampleTestcases") or "").split("\n"))
            print(
                f"  Would update {path.name}: "
                f"add description_en (length={desc_en_len}), "
                f"description_zh={'yes' if has_zh else 'fallback_to_en'}, "
                f"constraints={'yes' if constraints_html else 'no'}, "
                f"leetcode_examples ({example_count} lines)"
            )
            success_count += 1
            print()
            continue

        # Backup
        if args.backup:
            if backup_problem_json(path):
                print(f"  Backup saved to {BACKUP_DIR / path.name}")
            else:
                print(f"  WARNING: backup failed for {path.name}")

        # Update JSON
        if update_problem_json(path, data):
            success_count += 1
            print(f"  Updated: description_en, description_zh, constraints, leetcode_examples")
        else:
            fail_count += 1
            print(f"  FAILED to update {path.name}")

        # Rate limiting delay (skip after last item)
        if i < total:
            print(f"  Waiting {RATE_LIMIT_DELAY}s...")
            time.sleep(RATE_LIMIT_DELAY)

        print()

    print(f"Done: {success_count} succeeded, {fail_count} failed out of {total} total")
    sys.exit(1 if fail_count > 0 else 0)


if __name__ == "__main__":
    main()
