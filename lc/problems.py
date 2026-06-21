import json
from .paths import PROBLEMS_DIR


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
    fn = problem["function"]
    return {
        "input": {name: default_input(typ, index) for name, typ in fn["params"]},
        "output": default_output(fn["return"]),
        "generated": True,
    }


def ensure_examples(problem):
    problem.setdefault("examples", [make_default_case(problem, 0)])
    cases = list(problem.get("tests", problem["examples"]))
    for index in range(len(cases), 20):
        cases.append(make_default_case(problem, index))
    problem["tests"] = cases[:20]
    return problem


def load_problems():
    problems = []
    for path in sorted(PROBLEMS_DIR.glob("[0-9][0-9][0-9]_*.json")):
        with path.open("r", encoding="utf-8") as f:
            problems.append(json.load(f))
    return [ensure_examples(p) for p in sorted(problems, key=lambda p: p["id"])]


def find_problem(problem_id):
    for problem in load_problems():
        if problem["id"] == problem_id:
            return problem
    return None


def solution_filename(problem):
    return f"{problem['id']:03d}_{problem['slug'].replace('-', '_')}.py"
