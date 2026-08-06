from .paths import WORKSPACE
from .problems import solution_filename


def type_imports(problem):
    text = " ".join([param[1] for param in problem["function"]["params"]] + [problem["function"]["return"]])
    names = []
    for name in ["List", "Optional", "Dict", "Set", "Tuple"]:
        if name in text:
            names.append(name)
    if not names:
        return ""
    return f"from typing import {', '.join(names)}\n\n"


def stub_value(return_type):
    if return_type.startswith("List"):
        return "[]"
    if return_type == "bool":
        return "False"
    if return_type == "int":
        return "0"
    if return_type == "str":
        return "\"\""
    return "None"


def render_solution(problem):
    if not isinstance(problem, dict) or "function" not in problem:
        return "class Solution:\n    pass\n"
    func_sig = problem["function"]
    if not isinstance(func_sig, dict) or "name" not in func_sig:
        return "class Solution:\n    pass\n"
    params = ", ".join([f"{name}: {typ}" for name, typ in func_sig["params"]])
    if params:
        params = ", " + params
    lines = [
        type_imports(problem),
        "class Solution:\n",
        f"    def {func_sig['name']}(self{params}) -> {func_sig['return']}:\n",
        f"        return {stub_value(func_sig['return'])}\n",
    ]
    return "".join(lines)


def create_solution(problem):
    if not isinstance(problem, dict):
        return None, False
    WORKSPACE.mkdir(exist_ok=True)
    path = WORKSPACE / solution_filename(problem)
    if path.exists():
        return path, False
    path.write_text(render_solution(problem), encoding="utf-8")
    return path, True
