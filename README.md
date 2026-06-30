# lc-simulator

Local Python-only LeetCode Hot 100 CLI simulator.

![Python](https://img.shields.io/badge/python-%3E%3D3.9-blue)

`lc-simulator` is a local command line practice tool for the LeetCode Hot 100. It ships 100 problem definitions as JSON, generates Python solution stubs, runs examples against your code, and tracks completed problems on your machine.

The project uses only the Python standard library at runtime. Your solutions stay in `workspace/`, while progress is stored in `.data/progress.json`.

---

## Features

- Practice the LeetCode Hot 100 locally from the terminal.
- Browse all 100 bundled problem JSON files.
- Filter problem lists by difficulty or category.
- Show a single problem by ID or all problems in one category.
- Generate Python solution stubs in `workspace/`.
- Run all examples for a problem or only one case with `--case N`.
- Mark problems as done and view completion stats.
- Switch command output between English and Chinese with `--lang en|zh`.
- Use pure Python runtime code with no external runtime dependencies.
- Keep user work and runtime progress out of source problem definitions.

---

## Quick Start

### Prerequisites

- Python 3.9 or newer
- `pip`, recommended for editable installation
- `pytest`, only needed when running the test suite

### Install

```bash
git clone <repo-url>
cd lc_simulator
python -m pip install -e .
```

The install registers the `lc` command from `lc.cli:main`.

If you don't want to install the package, you can run the CLI as a module instead:

```bash
python -m lc list
```

### Walkthrough of all 6 commands

#### 1. List problems

```bash
lc list
```

Filter by category or difficulty:

```bash
lc list --category array
lc list --difficulty easy
lc list --category dp --lang zh
```

#### 2. Show a problem

```bash
lc show 1
```

Show all problems in a category:

```bash
lc show --category sliding_window
lc show --category binary_tree --lang zh
```

#### 3. Create a solution file

```bash
lc new 1
```

This creates a Python stub in `workspace/` for the selected problem. If the file already exists, the CLI leaves it in place and reports that it already exists.

#### 4. Test a solution

```bash
lc test 1
```

Run only one test case, using a 1-based case number:

```bash
lc test 1 --case 1
```

#### 5. Mark a problem as done

```bash
lc done 1
```

This records completion in `.data/progress.json`.

#### 6. View stats

```bash
lc stats
lc stats --lang zh
```

---

## Commands Reference

| Command | Description | Example |
| --- | --- | --- |
| `lc list` | List problems with ID, difficulty, status, and title. Supports `--category`, `--difficulty`, and `--lang`. | `lc list --category hash --lang zh` |
| `lc show [id]` | Show full problem details, examples, categories, URL, and expected Python signature. | `lc show 1` |
| `lc show --category <type>` | Show all full problem details for a category. | `lc show --category graph` |
| `lc new <id>` | Create a solution stub in `workspace/`. Existing files are not overwritten. | `lc new 49` |
| `lc test <id>` | Run examples from the problem JSON against the matching solution file. | `lc test 49` |
| `lc test <id> --case N` | Run only the N-th example, where `N` is 1-based. | `lc test 49 --case 2` |
| `lc done <id>` | Mark a problem as completed in `.data/progress.json`. | `lc done 49` |
| `lc stats` | Print total problem count and completed count. | `lc stats --lang en` |

Common flags:

| Flag | Used by | Description | Example |
| --- | --- | --- | --- |
| `--lang en|zh` | All commands | Choose English or Chinese output. | `lc show 1 --lang zh` |
| `--category <type>` | `list`, `show` | Filter a list or show all problems in a category. | `lc list --category two_pointers` |
| `--difficulty easy|medium|hard` | `list` | Filter listed problems by difficulty. | `lc list --difficulty medium` |
| `--case N` | `test` | Run one example case by 1-based index. | `lc test 1 --case 1` |

---

## Architecture

### Directory tree

```text
lc_simulator/
├── lc/                    # Core library, 9 modules
│   ├── cli.py             # CLI entry and command handlers
│   ├── problems.py        # Problem loading, lookup, and solution filenames
│   ├── runner.py          # Dynamic import and test execution
│   ├── progress.py        # JSON-based completion tracking
│   ├── templates.py       # Solution stub generation
│   ├── paths.py           # Path constants for problems, workspace, and data
│   ├── i18n.py            # Translations and category names
│   ├── __init__.py        # Package version
│   └── __main__.py        # python -m lc support
├── problems/              # 100 LeetCode Hot 100 JSON files
├── workspace/             # User solution .py files, gitignored
├── tests/                 # pytest test suite
├── scripts/               # Content fetch and validation helpers
├── cache/                 # API response cache
├── .data/                 # Runtime data, including progress.json
└── pyproject.toml         # Project metadata and lc entry point
```

### Data flow

```text
problems/*.json
      |
      v
lc/problems.py
      |
      v
lc/cli.py + lc/runner.py + lc/progress.py
      |
      +--------------------+--------------------+
      |                    |                    |
      v                    v                    v
terminal output       workspace/*.py       .data/progress.json
```

### Problem JSON shape

Each problem is a JSON document with metadata, bilingual titles and descriptions, categories, a Python function signature, examples, constraints, and the source URL.

```json
{
  "id": 1,
  "slug": "two-sum",
  "title_en": "Two Sum",
  "title_zh": "两数之和",
  "difficulty": "easy",
  "categories": ["array", "hash"],
  "function": {
    "name": "twoSum",
    "params": [["nums", "List[int]"], ["target", "int"]],
    "return": "List[int]"
  },
  "examples": [
    {
      "input": {"nums": [2, 7, 11, 15], "target": 9},
      "output": [0, 1]
    }
  ],
  "description_en": "...",
  "description_zh": "...",
  "constraints": "...",
  "leetcode_examples": [],
  "url": "https://leetcode.com/problems/two-sum/"
}
```

---

## Problem Categories

| Key | English | 中文 |
| --- | --- | --- |
| `array` | Array | 数组 |
| `hash` | Hash Table | 哈希表 |
| `two_pointers` | Two Pointers | 双指针 |
| `sliding_window` | Sliding Window | 滑动窗口 |
| `subarray` | Subarray | 子数组 |
| `matrix` | Matrix | 矩阵 |
| `linked_list` | Linked List | 链表 |
| `binary_tree` | Binary Tree | 二叉树 |
| `graph` | Graph | 图 |
| `backtracking` | Backtracking | 回溯 |
| `binary_search` | Binary Search | 二分查找 |
| `stack` | Stack | 栈 |
| `heap` | Heap | 堆 |
| `greedy` | Greedy | 贪心 |
| `dp` | Dynamic Programming | 动态规划 |
| `trie` | Trie | 字典树 |
| `interval` | Interval | 区间 |

---

## Testing

Runtime use of the CLI needs no external dependencies. The test suite uses `pytest`.

Install test tooling if needed:

```bash
python -m pip install pytest
```

Run all tests:

```bash
python -m pytest
```

Run tests for one area:

```bash
python -m pytest tests/test_cli.py
python -m pytest tests/test_runner.py
python -m pytest tests/test_fetch.py
```

You can also test the installed CLI directly:

```bash
lc list
lc new 1
lc test 1 --case 1
lc done 1
lc stats
```

---

## TODO

Future features that would fit the project:

- Add more LeetCode tags beyond the current 17 categories.
- Add `lc random` to pick a problem by category, difficulty, or unfinished status.
- Add `lc review` for spaced repetition of completed or failed problems.
- Add `lc hint` to show a small clue without revealing the full solution.
- Track time spent per problem and across sessions.
- Export progress to JSON, CSV, or Markdown.
- Add multi-language templates for solution stubs.
- Add an interactive mode for browsing, creating, testing, and marking problems.
- Add a daily challenge command that selects one problem per day.

---

## License

License: Not specified in this repository.
