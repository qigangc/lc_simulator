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


    def test_command_show_category_filters_and_prints_matches(self):
        args = SimpleNamespace(id=None, category="array", lang="en")
        problems = [
            {
                "id": 1,
                "title_en": "Two Sum",
                "title_zh": "两数之和",
                "difficulty": "easy",
                "categories": ["array", "hash"],
                "url": "https://leetcode.com/problems/two-sum/",
                "function": {"name": "twoSum", "params": [["nums", "List[int]"], ["target", "int"]], "return": "List[int]"},
                "examples": [],
            },
            {
                "id": 2,
                "title_en": "Add Two Numbers",
                "title_zh": "两数相加",
                "difficulty": "medium",
                "categories": ["linked_list", "math"],
                "url": "https://leetcode.com/problems/add-two-numbers/",
                "function": {"name": "addTwoNumbers", "params": [["l1", "ListNode"], ["l2", "ListNode"]], "return": "ListNode"},
                "examples": [],
            },
            {
                "id": 3,
                "title_en": "Longest Substring Without Repeating Characters",
                "title_zh": "无重复字符的最长子串",
                "difficulty": "medium",
                "categories": ["hash", "sliding_window", "string"],
                "url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
                "function": {"name": "lengthOfLongestSubstring", "params": [["s", "str"]], "return": "int"},
                "examples": [],
            },
        ]

        with patch.object(cli, "load_problems", return_value=problems):
            output = StringIO()
            with redirect_stdout(output):
                cli.command_show(args)

        text = output.getvalue()
        # Should contain the array problem (id=1) but not the others
        self.assertIn("ID: 1", text)
        self.assertIn("Two Sum", text)
        self.assertNotIn("ID: 2", text)
        self.assertNotIn("Add Two Numbers", text)
        self.assertNotIn("ID: 3", text)

    def test_command_show_category_nonexistent_prints_message(self):
        args = SimpleNamespace(id=None, category="nonexistent", lang="en")
        problems = [
            {
                "id": 1,
                "title_en": "Two Sum",
                "title_zh": "两数之和",
                "difficulty": "easy",
                "categories": ["array", "hash"],
                "url": "",
                "function": {"name": "twoSum", "params": [["nums", "List[int]"], ["target", "int"]], "return": "List[int]"},
                "examples": [],
            },
        ]

        with patch.object(cli, "load_problems", return_value=problems):
            output = StringIO()
            with redirect_stdout(output):
                cli.command_show(args)

        self.assertIn("No problems found in category: nonexistent", output.getvalue())

    def test_command_show_no_id_no_category_prints_error(self):
        args = SimpleNamespace(id=None, category=None, lang="en")

        output = StringIO()
        with redirect_stdout(output):
            cli.command_show(args)

        self.assertIn("Please provide a problem ID or --category", output.getvalue())

    def test_command_show_with_id_still_works(self):
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

        self.assertIn("ID: 1", output.getvalue())
        self.assertIn("Two Sum", output.getvalue())

    def test_show_parser_accepts_category_without_id(self):
        args = build_parser().parse_args(["show", "--category", "array"])
        self.assertIsNone(args.id)
        self.assertEqual(args.category, "array")

    def test_show_parser_accepts_id_without_category(self):
        args = build_parser().parse_args(["show", "1"])
        self.assertEqual(args.id, 1)
        self.assertIsNone(args.category)


if __name__ == "__main__":
    unittest.main()
