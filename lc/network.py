"""Network utilities with graceful offline handling.

All network operations go through this module so that connection failures
never surface as raw tracebacks to the user. Instead, callers receive a
structured result and can show a friendly "offline mode" message.
"""

import socket


def is_online(host="leetcode.com", port=443, timeout=3):
    """Quick TCP connectivity check. Returns True if reachable."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, socket.timeout):
        return False


def fetch_problem_content(slug, force=False):
    """Fetch problem content from LeetCode GraphQL API.

    Returns a dict with:
        status: "ok" | "offline" | "error" | "missing_dependency"
        data:   dict (only when status == "ok")
        message: str (human-readable detail)
    """
    try:
        import requests
    except ImportError:
        return {
            "status": "missing_dependency",
            "data": None,
            "message": "requests library not installed",
        }

    from .config import (
        GRAPHQL_URL, REQUEST_TIMEOUT, USER_AGENT,
        MAX_RETRY_ATTEMPTS, RATE_LIMIT_DELAY, MAX_RETRY_BACKOFF,
    )

    if not is_online():
        return {
            "status": "offline",
            "data": None,
            "message": "no network connection",
        }

    payload = {
        "operationName": "questionData",
        "variables": {"titleSlug": slug},
        "query": (
            "query questionData($titleSlug: String!) {"
            "  question(titleSlug: $titleSlug) {"
            "    content translatedContent exampleTestcases"
            "  }"
            "}"
        ),
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }

    import time
    import random

    backoff = RATE_LIMIT_DELAY
    for attempt in range(MAX_RETRY_ATTEMPTS):
        try:
            resp = requests.post(
                GRAPHQL_URL,
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            if resp.status_code == 200:
                question = resp.json().get("data", {}).get("question")
                if question is None:
                    return {"status": "error", "data": None, "message": "empty response"}
                return {
                    "status": "ok",
                    "data": {
                        "content": question.get("content"),
                        "translatedContent": question.get("translatedContent"),
                        "exampleTestcases": question.get("exampleTestcases"),
                    },
                    "message": "ok",
                }

            if resp.status_code == 429 or 500 <= resp.status_code < 600:
                sleep_time = min(backoff + random.uniform(0, 1), MAX_RETRY_BACKOFF)
                time.sleep(sleep_time)
                backoff = min(backoff * 2, MAX_RETRY_BACKOFF)
                continue

            return {
                "status": "error",
                "data": None,
                "message": f"HTTP {resp.status_code}",
            }

        except requests.exceptions.Timeout:
            backoff = min(backoff * 2, MAX_RETRY_BACKOFF)
            continue
        except requests.exceptions.RequestException as exc:
            if is_online():
                return {"status": "error", "data": None, "message": str(exc)}
            return {"status": "offline", "data": None, "message": str(exc)}

    return {
        "status": "error",
        "data": None,
        "message": f"failed after {MAX_RETRY_ATTEMPTS} attempts",
    }
