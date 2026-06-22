import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lc import runner


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


if __name__ == "__main__":
    unittest.main()
