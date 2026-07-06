import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lc import runner
from lc.problems import default_input


def make_problem():
    return {
        "id": 1,
        "slug": "two-sum",
        "function": {
            "name": "twoSum",
            "params": [["nums", "List[int]"], ["target", "int"]],
            "return": "List[int]",
        },
        "tests": [
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "output": [0, 1]},
            {"input": {"nums": [3, 2, 4], "target": 6}, "output": [1, 2]},
        ],
    }


class RunProblemTests(unittest.TestCase):
    def write_solution(self, root, body):
        workspace = Path(root) / "workspace"
        workspace.mkdir()
        solution_path = workspace / "001_two_sum.py"
        solution_path.write_text(body, encoding="utf-8")
        return workspace

    def test_run_problem_includes_input_for_failed_case(self):
        with tempfile.TemporaryDirectory() as root:
            workspace = self.write_solution(
                root,
                "class Solution:\n"
                "    def twoSum(self, nums, target):\n"
                "        return []\n",
            )
            with patch.object(runner, "WORKSPACE", workspace):
                ok, results = runner.run_problem(make_problem())

        self.assertFalse(ok)
        self.assertEqual(results[0]["input"], {"nums": [2, 7, 11, 15], "target": 9})
        self.assertEqual(results[0]["expected"], [0, 1])
        self.assertEqual(results[0]["actual"], [])

    def test_run_problem_can_run_single_case(self):
        with tempfile.TemporaryDirectory() as root:
            workspace = self.write_solution(
                root,
                "class Solution:\n"
                "    def twoSum(self, nums, target):\n"
                "        return [1, 2]\n",
            )
            with patch.object(runner, "WORKSPACE", workspace):
                ok, results = runner.run_problem(make_problem(), case_index=2)

        self.assertTrue(ok)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["index"], 2)
        self.assertEqual(results[0]["input"], {"nums": [3, 2, 4], "target": 6})

    def test_run_problem_preserves_input_when_solution_mutates_args(self):
        problem = make_problem()
        with tempfile.TemporaryDirectory() as root:
            workspace = self.write_solution(
                root,
                "class Solution:\n"
                "    def twoSum(self, nums, target):\n"
                "        nums.clear()\n"
                "        return []\n",
            )
            with patch.object(runner, "WORKSPACE", workspace):
                ok, results = runner.run_problem(problem, case_index=1)

        self.assertFalse(ok)
        self.assertEqual(results[0]["input"], {"nums": [2, 7, 11, 15], "target": 9})
        self.assertEqual(problem["tests"][0]["input"], {"nums": [2, 7, 11, 15], "target": 9})

    def test_run_problem_rejects_out_of_range_case(self):
        with tempfile.TemporaryDirectory() as root:
            workspace = self.write_solution(
                root,
                "class Solution:\n"
                "    def twoSum(self, nums, target):\n"
                "        return []\n",
            )
            with patch.object(runner, "WORKSPACE", workspace):
                ok, results = runner.run_problem(make_problem(), case_index=3)

        self.assertFalse(ok)
        self.assertEqual(results, [{"error": "case 3 out of range (1..2)"}])


class DefaultInputTests(unittest.TestCase):
    def test_int_returns_index(self):
        self.assertEqual(default_input("int", 0), 0)
        self.assertEqual(default_input("int", 5), 5)
        self.assertEqual(default_input("int", 100), 100)

    def test_float_returns_float_index(self):
        self.assertEqual(default_input("float", 0), 0.0)
        self.assertEqual(default_input("float", 3), 3.0)
        self.assertIsInstance(default_input("float", 7), float)

    def test_bool_returns_even_odd(self):
        self.assertTrue(default_input("bool", 0))
        self.assertFalse(default_input("bool", 1))
        self.assertTrue(default_input("bool", 2))
        self.assertFalse(default_input("bool", 3))

    def test_str_returns_slice_of_abc(self):
        self.assertEqual(default_input("str", 0), "")
        self.assertEqual(default_input("str", 1), "a")
        self.assertEqual(default_input("str", 2), "ab")
        self.assertEqual(default_input("str", 3), "abc")
        self.assertEqual(default_input("str", 4), "")
        self.assertEqual(default_input("str", 5), "a")

    def test_List_int_returns_range(self):
        self.assertEqual(default_input("List[int]", 0), [])
        self.assertEqual(default_input("List[int]", 1), [0])
        self.assertEqual(default_input("List[int]", 4), [0, 1, 2, 3])
        self.assertEqual(default_input("List[int]", 5), [])
        self.assertEqual(default_input("List[int]", 6), [0])

    def test_List_str_returns_abc_slice(self):
        self.assertEqual(default_input("List[str]", 0), [])
        self.assertEqual(default_input("List[str]", 1), ["a"])
        self.assertEqual(default_input("List[str]", 3), ["a", "b", "c"])
        self.assertEqual(default_input("List[str]", 4), [])

    def test_List_float_returns_float_range(self):
        self.assertEqual(default_input("List[float]", 0), [])
        self.assertEqual(default_input("List[float]", 2), [0.0, 1.0])
        self.assertIsInstance(default_input("List[float]", 3)[0], float)

    def test_List_List_int_returns_matrix(self):
        self.assertEqual(default_input("List[List[int]]", 0), [])
        self.assertEqual(default_input("List[List[int]]", 1), [[0]])
        self.assertEqual(default_input("List[List[int]]", 2), [[0, 1], [0, 1, 2]])

    def test_List_List_str_returns_string_matrix(self):
        self.assertEqual(default_input("List[List[str]]", 0), [])
        result = default_input("List[List[str]]", 1)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0][0], str)

    def test_List_object_returns_empty(self):
        self.assertEqual(default_input("List[object]", 0), [])
        self.assertEqual(default_input("List[object]", 10), [])

    def test_unknown_type_returns_empty(self):
        self.assertEqual(default_input("UnknownType", 5), [])
        self.assertEqual(default_input("Dict[str, int]", 3), [])
        self.assertEqual(default_input("", 7), [])


if __name__ == "__main__":
    unittest.main()
