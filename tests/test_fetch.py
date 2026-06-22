import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import call, patch

from scripts.fetch_content import (
    extract_constraints_from_html,
    fetch_problem,
    html_to_markdown,
    update_problem_json,
)


class HtmlToMarkdownTests(unittest.TestCase):
    """Tests for html_to_markdown conversion."""

    def test_empty_string(self):
        self.assertEqual(html_to_markdown(""), "")

    def test_none_string(self):
        self.assertEqual(html_to_markdown(None), "")

    def test_plain_text_passes_through(self):
        html = "<p>Hello world</p>"
        result = html_to_markdown(html)
        self.assertIn("Hello world", result)

    def test_code_tag(self):
        html = "<p>Use <code>print()</code> to debug</p>"
        result = html_to_markdown(html)
        self.assertIn("`print()`", result)

    def test_pre_code_block(self):
        html = "<pre><code>def hello():\n    pass</code></pre>"
        result = html_to_markdown(html)
        self.assertIn("def hello():", result)
        self.assertIn("pass", result)

    def test_sup_tag(self):
        html = "<p>2<sup>3</sup> = 8</p>"
        result = html_to_markdown(html)
        # Actual: <sup> is replaced with (content)
        self.assertIn("2(3)", result)

    def test_strong_tag(self):
        html = "<p>This is <strong>important</strong></p>"
        result = html_to_markdown(html)
        self.assertIn("**important**", result)

    def test_em_tag(self):
        html = "<p>This is <em>emphasized</em></p>"
        result = html_to_markdown(html)
        self.assertIn("*emphasized*", result)

    def test_img_tag(self):
        html = '<p><img src="https://example.com/img.png" alt="desc"/></p>'
        result = html_to_markdown(html)
        # Actual: <img> is replaced with [image] placeholder
        self.assertIn("[image]", result)

    def test_multiple_paragraphs(self):
        html = "<p>First</p><p>Second</p>"
        result = html_to_markdown(html)
        self.assertIn("First", result)
        self.assertIn("Second", result)

    def test_nested_tags(self):
        html = "<p><strong><em>bold italic</em></strong></p>"
        result = html_to_markdown(html)
        self.assertIn("bold italic", result)

    def test_html_with_line_breaks(self):
        html = "<p>Line1<br/>Line2</p>"
        result = html_to_markdown(html)
        self.assertIn("Line1", result)
        self.assertIn("Line2", result)

    def test_anchor_text_preserved(self):
        """Links are stripped but link text is preserved."""
        html = '<p>See <a href="https://example.com">here</a></p>'
        result = html_to_markdown(html)
        self.assertIn("here", result)

    def test_html_with_entities(self):
        html = "<p>A &amp; B &lt; C</p>"
        result = html_to_markdown(html)
        self.assertIn("&", result)
        self.assertIn("<", result)

    def test_sub_tag(self):
        html = "<p>H<sub>2</sub>O</p>"
        result = html_to_markdown(html)
        self.assertIn("H(2)O", result)

    def test_constraints_section(self):
        html = "<strong>Constraints:</strong></p><ul><li>1 &lt;= n &lt;= 10</li></ul>"
        result = html_to_markdown(html)
        self.assertIn("Constraints", result)
        self.assertIn("n", result)


class ExtractConstraintsTests(unittest.TestCase):
    """Tests for extract_constraints_from_html.

    Actual pattern: Constraints:</strong></p><ul>...</ul>
    Returns: <ul>...</ul> or empty string.
    """

    def test_extracts_constraints(self):
        html = "<p>Some text</p><strong>Constraints:</strong></p><ul><li>1 &lt;= n</li></ul>"
        result = extract_constraints_from_html(html)
        self.assertIn("<ul>", result)
        self.assertIn("<li>", result)

    def test_empty_html(self):
        self.assertEqual(extract_constraints_from_html(""), "")

    def test_no_constraints(self):
        html = "<p>Just content</p>"
        self.assertEqual(extract_constraints_from_html(html), "")

    def test_constraints_with_leading_p(self):
        html = "<p>Description</p><strong>Constraints:</strong></p><ul><li>Item</li></ul>"
        result = extract_constraints_from_html(html)
        self.assertIn("<ul>", result)


class UpdateProblemJsonTests(unittest.TestCase):
    """Tests for update_problem_json.

    Actual signature: update_problem_json(path: Path, data: dict) -> bool
    Reads JSON from path, updates fields, writes back, returns True on success.
    """

    def setUp(self):
        self.base_data = {
            "id": 1,
            "slug": "two-sum",
            "title_en": "Two Sum",
            "title_zh": "两数之和",
            "difficulty": "easy",
            "categories": ["array", "hash"],
            "function": {"name": "twoSum", "params": [["nums", "List[int]"], ["target", "int"]], "return": "List[int]"},
            "examples": [],
            "url": "https://leetcode.com/problems/two-sum/",
        }
        self.update_data = {
            "content": "<p>Given an array of integers...</p>",
            "translatedContent": "<p>给定一个整数数组...</p>",
            "exampleTestcases": "2 7 11 15\n9\n3 2 4\n6",
        }

    def test_adds_description_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "001_two-sum.json"
            path.write_text(json.dumps(self.base_data), encoding="utf-8")

            ok = update_problem_json(path, self.update_data)
            self.assertTrue(ok)

            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("description_en", saved)
            self.assertIn("description_zh", saved)
            self.assertIn("constraints", saved)
            self.assertIn("leetcode_examples", saved)

    def test_preserves_existing_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "001_two-sum.json"
            path.write_text(json.dumps(self.base_data), encoding="utf-8")

            update_problem_json(path, self.update_data)
            saved = json.loads(path.read_text(encoding="utf-8"))

            self.assertEqual(saved["id"], 1)
            self.assertEqual(saved["slug"], "two-sum")
            self.assertEqual(saved["title_en"], "Two Sum")
            self.assertEqual(saved["title_zh"], "两数之和")
            self.assertEqual(saved["difficulty"], "easy")
            self.assertEqual(saved["categories"], ["array", "hash"])
            self.assertEqual(saved["url"], "https://leetcode.com/problems/two-sum/")

    def test_parses_leetcode_examples(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "001_two-sum.json"
            path.write_text(json.dumps(self.base_data), encoding="utf-8")

            update_problem_json(path, self.update_data)
            saved = json.loads(path.read_text(encoding="utf-8"))

            self.assertEqual(saved["leetcode_examples"], ["2 7 11 15", "9", "3 2 4", "6"])

    def test_handles_empty_example_testcases(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "001_two-sum.json"
            path.write_text(json.dumps(self.base_data), encoding="utf-8")

            update_problem_json(path, {"content": "<p>Text</p>", "exampleTestcases": ""})
            saved = json.loads(path.read_text(encoding="utf-8"))

            self.assertEqual(saved["leetcode_examples"], [])

    def test_handles_null_translated_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "001_two-sum.json"
            path.write_text(json.dumps(self.base_data), encoding="utf-8")

            update_problem_json(path, {"content": "<p>English</p>", "translatedContent": None})
            saved = json.loads(path.read_text(encoding="utf-8"))

            # Falls back to English
            self.assertIn("English", saved["description_zh"])

    def test_returns_false_on_missing_file(self):
        result = update_problem_json(Path("nonexistent.json"), self.update_data)
        self.assertFalse(result)

    def test_returns_false_on_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad.json"
            path.write_text("not json", encoding="utf-8")

            result = update_problem_json(path, self.update_data)
            self.assertFalse(result)

    def test_handles_content_with_constraints(self):
        data_with_constraints = {
            "content": "<p>Description</p><strong>Constraints:</strong></p><ul><li>1 &lt;= n</li></ul>",
            "translatedContent": None,
            "exampleTestcases": "",
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "001_two-sum.json"
            path.write_text(json.dumps(self.base_data), encoding="utf-8")

            update_problem_json(path, data_with_constraints)
            saved = json.loads(path.read_text(encoding="utf-8"))

            self.assertIn("constraints", saved)
            self.assertGreater(len(saved["constraints"]), 0)


class FetchProblemCacheTests(unittest.TestCase):
    """Tests for fetch_problem cache behavior.

    Actual signature: fetch_problem(slug: str, force: bool = False) -> dict | None
    Cache is at cache/{slug}.json. force=True skips cache.
    """

    @patch("scripts.fetch_content.CACHE_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("scripts.fetch_content.requests.post")
    def test_cache_hit_returns_cached_data(self, mock_post, mock_cache_dir):
        cached = {"content": "<p>Cached</p>", "translatedContent": None, "exampleTestcases": ""}
        cache_path = mock_cache_dir / "two-sum.json"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cached), encoding="utf-8")

        result = fetch_problem("two-sum")

        mock_post.assert_not_called()
        self.assertEqual(result, cached)

    @patch("scripts.fetch_content.CACHE_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("scripts.fetch_content.requests.post")
    def test_cache_miss_fetches_from_api(self, mock_post, mock_cache_dir):
        mock_post.return_value.json.return_value = {
            "data": {"question": {"content": "<p>API</p>", "translatedContent": None, "exampleTestcases": ""}}
        }
        mock_post.return_value.status_code = 200

        result = fetch_problem("two-sum")

        mock_post.assert_called_once()
        self.assertEqual(result["content"], "<p>API</p>")

    @patch("scripts.fetch_content.CACHE_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("scripts.fetch_content.requests.post")
    def test_cache_miss_writes_cache(self, mock_post, mock_cache_dir):
        api_data = {"content": "<p>API</p>", "translatedContent": None, "exampleTestcases": ""}
        mock_post.return_value.json.return_value = {"data": {"question": api_data}}
        mock_post.return_value.status_code = 200

        fetch_problem("two-sum")

        cache_path = mock_cache_dir / "two-sum.json"
        self.assertTrue(cache_path.exists())
        saved = json.loads(cache_path.read_text(encoding="utf-8"))
        self.assertEqual(saved, api_data)

    @patch("scripts.fetch_content.CACHE_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("scripts.fetch_content.requests.post")
    def test_force_skips_cache(self, mock_post, mock_cache_dir):
        cached = {"content": "<p>Cached</p>", "translatedContent": None, "exampleTestcases": ""}
        cache_path = mock_cache_dir / "two-sum.json"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cached), encoding="utf-8")

        mock_post.return_value.json.return_value = {
            "data": {"question": {"content": "<p>Fresh</p>", "translatedContent": None, "exampleTestcases": ""}}
        }
        mock_post.return_value.status_code = 200

        result = fetch_problem("two-sum", force=True)

        mock_post.assert_called_once()
        self.assertEqual(result["content"], "<p>Fresh</p>")


class FetchProblemApiTests(unittest.TestCase):
    """Tests for fetch_problem API interaction."""

    @patch("scripts.fetch_content.CACHE_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("scripts.fetch_content.requests.post")
    def test_sends_graphql_query(self, mock_post, mock_cache_dir):
        mock_post.return_value.json.return_value = {
            "data": {"question": {"content": "", "translatedContent": None, "exampleTestcases": ""}}
        }
        mock_post.return_value.status_code = 200

        fetch_problem("two-sum")

        call_kwargs = mock_post.call_args[1]
        self.assertIn("json", call_kwargs)
        self.assertIn("query", call_kwargs["json"])

    @patch("scripts.fetch_content.CACHE_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("scripts.fetch_content.requests.post")
    def test_uses_graphql_url(self, mock_post, mock_cache_dir):
        mock_post.return_value.json.return_value = {
            "data": {"question": {"content": "", "translatedContent": None, "exampleTestcases": ""}}
        }
        mock_post.return_value.status_code = 200

        fetch_problem("two-sum")

        url = mock_post.call_args[0][0]
        self.assertIn("leetcode.com/graphql", url)

    @patch("scripts.fetch_content.CACHE_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("scripts.fetch_content.requests.post")
    def test_handles_empty_response(self, mock_post, mock_cache_dir):
        mock_post.return_value.json.return_value = {}
        mock_post.return_value.status_code = 200

        result = fetch_problem("two-sum")
        self.assertIsNone(result)

    @patch("scripts.fetch_content.CACHE_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("scripts.fetch_content.requests.post")
    def test_handles_missing_question_key(self, mock_post, mock_cache_dir):
        mock_post.return_value.json.return_value = {"data": {}}
        mock_post.return_value.status_code = 200

        result = fetch_problem("two-sum")
        self.assertIsNone(result)

    @patch("scripts.fetch_content.CACHE_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("scripts.fetch_content.requests.post")
    def test_handles_http_404(self, mock_post, mock_cache_dir):
        mock_post.return_value.status_code = 404

        result = fetch_problem("two-sum")
        self.assertIsNone(result)

    @patch("scripts.fetch_content.CACHE_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("scripts.fetch_content.time.sleep")
    @patch("scripts.fetch_content.requests.post")
    def test_retries_on_server_error(self, mock_post, mock_sleep, mock_cache_dir):
        mock_post.return_value.status_code = 500

        result = fetch_problem("two-sum")

        # Should have retried (5 attempts max)
        self.assertEqual(mock_post.call_count, 5)
        self.assertIsNone(result)

    @patch("scripts.fetch_content.CACHE_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("scripts.fetch_content.time.sleep")
    @patch("scripts.fetch_content.requests.post")
    def test_retries_on_rate_limit(self, mock_post, mock_sleep, mock_cache_dir):
        mock_post.return_value.status_code = 429

        result = fetch_problem("two-sum")

        self.assertEqual(mock_post.call_count, 5)
        self.assertIsNone(result)

    @patch("scripts.fetch_content.CACHE_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("scripts.fetch_content.time.sleep")
    @patch("scripts.fetch_content.requests.post")
    def test_recovers_after_retry(self, mock_post, mock_sleep, mock_cache_dir):
        """Returns data after a transient 500 error."""
        responses = [
            unittest.mock.MagicMock(status_code=500),
            unittest.mock.MagicMock(status_code=200, json=lambda: {
                "data": {"question": {"content": "<p>OK</p>", "translatedContent": None, "exampleTestcases": ""}}
            }),
        ]
        mock_post.side_effect = responses

        result = fetch_problem("two-sum")

        self.assertIsNotNone(result)
        self.assertEqual(result["content"], "<p>OK</p>")


class FetchProblemEdgeCases(unittest.TestCase):
    """Edge cases for fetch_problem."""

    @patch("scripts.fetch_content.CACHE_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
    @patch("scripts.fetch_content.requests.post")
    def test_handles_corrupted_cache(self, mock_post, mock_cache_dir):
        cache_path = mock_cache_dir / "two-sum.json"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text("not valid json", encoding="utf-8")

        mock_post.return_value.json.return_value = {
            "data": {"question": {"content": "<p>Fresh</p>", "translatedContent": None, "exampleTestcases": ""}}
        }
        mock_post.return_value.status_code = 200

        result = fetch_problem("two-sum")

        # Falls through to API on corrupted cache
        mock_post.assert_called_once()
        self.assertEqual(result["content"], "<p>Fresh</p>")


if __name__ == "__main__":
    unittest.main()
