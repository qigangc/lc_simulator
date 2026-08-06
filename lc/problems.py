import json
import sys
from .paths import PROBLEMS_DIR
from .config import MAX_TEST_CASES, PROBLEM_FILE_PATTERN, JSON_ENCODING
from .color import yellow


def default_output(return_type):
    if return_type.startswith("List"):
        return []
    if return_type == "bool":
        return False
    if return_type in ("int", "float"):
        return 0
    return ""


def default_input(typ, index):
    if typ == "int":
        return index
    if typ == "float":
        return float(index)
    if typ == "bool":
        return index % 2 == 0
    if typ == "str":
        return "abc"[: index % 4]
    if typ == "List[int]":
        return list(range(index % 5))
    if typ == "List[str]":
        return ["a", "b", "c"][: index % 4]
    if typ == "List[float]":
        return [float(i) for i in range(index % 5)]
    if typ == "List[List[int]]":
        return [list(range((index + row) % 4)) for row in range(index % 3)]
    if typ == "List[List[str]]":
        return [["1" if (row + col + index) % 2 else "0" for col in range(2)] for row in range(index % 3)]
    if typ == "List[object]":
        return []
    return []


def make_default_case(problem, index):
    func_sig = problem["function"]
    return {
        "input": {name: default_input(typ, index) for name, typ in func_sig["params"]},
        "output": default_output(func_sig["return"]),
        "generated": True,
    }


def ensure_examples(problem):
    if not isinstance(problem, dict):
        return problem
    if "function" not in problem or not isinstance(problem.get("function"), dict):
        problem["tests"] = []
        return problem
    problem.setdefault("examples", [make_default_case(problem, 0)])
    cases = list(problem.get("tests", problem["examples"]))
    for index in range(len(cases), MAX_TEST_CASES):
        cases.append(make_default_case(problem, index))
    problem["tests"] = cases[:MAX_TEST_CASES]
    return problem


def load_problems():
    problems = []
    for path in sorted(PROBLEMS_DIR.glob(PROBLEM_FILE_PATTERN)):
        try:
            with path.open("r", encoding=JSON_ENCODING) as f:
                problem_data = json.load(f)
            if isinstance(problem_data, dict) and "id" in problem_data:
                problems.append(problem_data)
        except (json.JSONDecodeError, OSError) as e:
            print(yellow(f"Warning: skipping {path.name}: {e}"), file=sys.stderr)
    return [ensure_examples(prob) for prob in sorted(problems, key=lambda prob: prob.get("id", 0))]


def find_problem(problem_id):
    for problem in load_problems():
        if problem["id"] == problem_id:
            return problem
    return None


def solution_filename(problem):
    return f"{problem['id']:03d}_{problem['slug'].replace('-', '_')}.py"


def note_filename(problem):
    return f"{problem['id']:03d}_{problem['slug'].replace('-', '_')}.md"
