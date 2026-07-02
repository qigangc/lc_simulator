import copy
import importlib.util
import json
from .paths import WORKSPACE
from .problems import solution_filename


def load_solution(path):
    try:
        spec = importlib.util.spec_from_file_location("lc_user_solution", path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "Solution"):
            raise AttributeError(f"No Solution class found in {path}")
        return module.Solution()
    except Exception as e:
        raise RuntimeError(f"Failed to load solution from {path}: {e}")


def normalize(value):
    if isinstance(value, tuple):
        return list(value)
    return value


def run_problem(problem, case_index=None):
    if not isinstance(problem, dict):
        return False, [{"error": "invalid problem data"}]
    if "function" not in problem or not isinstance(problem["function"], dict):
        return False, [{"error": "problem missing function definition"}]
    if "name" not in problem["function"]:
        return False, [{"error": "problem function missing name"}]
    path = WORKSPACE / solution_filename(problem)
    if not path.exists():
        return False, [{"error": f"missing solution file: {path}"}]

    cases = list(problem.get("tests", problem.get("examples", [])))
    if case_index is not None:
        if case_index < 1 or case_index > len(cases):
            return False, [{"error": f"case {case_index} out of range (1..{len(cases)})"}]
        indexed_cases = [(case_index, cases[case_index - 1])]
    else:
        indexed_cases = enumerate(cases, start=1)

    solution = load_solution(path)
    fn = getattr(solution, problem["function"]["name"])
    results = []
    ok = True
    for index, case in indexed_cases:
        original_input = copy.deepcopy(case["input"])
        args = [copy.deepcopy(case["input"][name]) for name, _ in problem["function"]["params"]]
        expected = case["output"]
        try:
            actual = normalize(fn(*args))
            passed = actual == expected
        except Exception as exc:
            actual = f"{type(exc).__name__}: {exc}"
            passed = False
        ok = ok and passed
        results.append({"index": index, "input": original_input, "passed": passed, "expected": expected, "actual": actual})
    return ok, results


def format_value(value):
    return json.dumps(value, ensure_ascii=False)
