import unittest
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from lc import cli
from lc.cli import build_parser


class CliParserTests(unittest.TestCase):
    def test_test_command_accepts_single_case_argument(self):
        args = build_parser().parse_args(["test", "1", "--case", "2"])

        self.assertEqual(args.id, 1)
        self.assertEqual(args.case, 2)

    def test_command_show_prints_problem_url(self):
        args = SimpleNamespace(id=1, lang="en")
        problem = {
            "id": 1,
            "title_en": "Two Sum",
            "title_zh": "两数之和",
            "difficulty": "easy",
            "categories": ["array", "hash"],
            "url": "https://leetcode.com/problems/two-sum/",
            "function": {"name": "twoSum", "params": [["nums", "List[int]"], ["target", "int"]], "return": "List[int]"},
            "examples": [],
        }

        with patch.object(cli, "find_problem", return_value=problem):
            output = StringIO()
            with redirect_stdout(output):
                cli.command_show(args)

        self.assertIn("URL: https://leetcode.com/problems/two-sum/", output.getvalue())

    def test_command_test_prints_input_for_failed_case(self):
        args = SimpleNamespace(id=1, lang="en", case=1)
        problem = {"id": 1}
        results = [
            {
                "index": 1,
                "input": {"nums": [2, 7, 11, 15], "target": 9},
                "passed": False,
                "expected": [0, 1],
                "actual": [],
            }
        ]

        with patch.object(cli, "find_problem", return_value=problem), patch.object(cli, "run_problem", return_value=(False, results)):
            output = StringIO()
            with redirect_stdout(output):
                cli.command_test(args)

        self.assertIn('Input: {"nums": [2, 7, 11, 15], "target": 9}', output.getvalue())
        self.assertIn("Expected: [0, 1]", output.getvalue())
        self.assertIn("Actual: []", output.getvalue())


if __name__ == "__main__":
    unittest.main()
