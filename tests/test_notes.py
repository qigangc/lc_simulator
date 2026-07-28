import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lc import notes


def make_problem():
    return {"id": 1, "slug": "two-sum", "title_en": "Two Sum"}


class NotePathTests(unittest.TestCase):
    def test_note_path_uses_id_and_slug(self):
        problem = make_problem()
        with patch.object(notes, "NOTES_DIR", Path("/tmp/fake")):
            path = notes.note_path(problem)
        self.assertEqual(path, Path("/tmp/fake/001_two_sum.md"))


class EnsureNoteTests(unittest.TestCase):
    def test_creates_note_file_if_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(notes, "NOTES_DIR", Path(tmpdir)):
                path = notes.ensure_note(make_problem())
                self.assertTrue(path.exists())
                content = path.read_text(encoding="utf-8")
                self.assertIn("Two Sum", content)

    def test_does_not_overwrite_existing_note(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(notes, "NOTES_DIR", Path(tmpdir)):
                problem = make_problem()
                path = notes.ensure_note(problem)
                path.write_text("# my custom notes\n", encoding="utf-8")
                notes.ensure_note(problem)
                self.assertEqual(path.read_text(encoding="utf-8"), "# my custom notes\n")


class ReadNoteTests(unittest.TestCase):
    def test_returns_empty_string_for_missing_note(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(notes, "NOTES_DIR", Path(tmpdir)):
                self.assertEqual(notes.read_note(make_problem()), "")

    def test_returns_content_for_existing_note(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(notes, "NOTES_DIR", Path(tmpdir)):
                problem = make_problem()
                path = notes.ensure_note(problem)
                path.write_text("思路：哈希表\n", encoding="utf-8")
                self.assertEqual(notes.read_note(problem), "思路：哈希表\n")


if __name__ == "__main__":
    unittest.main()
