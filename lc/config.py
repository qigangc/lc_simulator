import os

# LeetCode GraphQL API
GRAPHQL_URL = os.environ.get("LC_GRAPHQL_URL", "https://leetcode.com/graphql")

# Network settings
REQUEST_TIMEOUT = int(os.environ.get("LC_REQUEST_TIMEOUT", "10"))
RATE_LIMIT_DELAY = float(os.environ.get("LC_RATE_LIMIT_DELAY", "2"))
MAX_RETRY_BACKOFF = float(os.environ.get("LC_MAX_RETRY_BACKOFF", "30"))
MAX_RETRY_ATTEMPTS = int(os.environ.get("LC_MAX_RETRY_ATTEMPTS", "5"))
USER_AGENT = os.environ.get("LC_USER_AGENT", "Mozilla/5.0 (compatible; LCProblemFetcher/1.0)")

# Paths (relative to project root)
PROBLEMS_DIR_NAME = os.environ.get("LC_PROBLEMS_DIR", "problems")
WORKSPACE_DIR_NAME = os.environ.get("LC_WORKSPACE_DIR", "workspace")
DATA_DIR_NAME = os.environ.get("LC_DATA_DIR", "data")
BACKUP_DIR_NAME = os.environ.get("LC_BACKUP_DIR", "problems_backup")
CACHE_DIR_NAME = os.environ.get("LC_CACHE_DIR", "cache")

# Problem settings
MAX_TEST_CASES = int(os.environ.get("LC_MAX_TEST_CASES", "20"))
PROGRESS_FILENAME = os.environ.get("LC_PROGRESS_FILE", "progress.json")

# Content validation
MIN_DESCRIPTION_LENGTH = int(os.environ.get("LC_MIN_DESCRIPTION_LENGTH", "50"))
PROBLEM_FILE_PATTERN = os.environ.get("LC_PROBLEM_PATTERN", "[0-9][0-9][0-9]_*.json")

# File encoding
JSON_ENCODING = os.environ.get("LC_JSON_ENCODING", "utf-8-sig")
