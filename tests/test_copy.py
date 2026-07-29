import tempfile
import unittest
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from lc import cli


def make_problem():
    return {"id": 1, "slug": "two-sum", "title_en": "Two Sum"}


class CommandCopyTests(unittest.TestCase):
    def test_export_to_file_writes_solution_code(self):
        problem = make_problem()
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir) / "workspace"
            workspace.mkdir()
            (workspace / "001_two_sum.py").write_text("class Solution:\n    pass\n", encoding="utf-8")
            out_file = str(Path(tmpdir) / "exported.py")

            args = SimpleNamespace(id=1, lang="en", out=out_file)
            with patch.object(cli, "find_problem", return_value=problem), \
                 patch.object(cli, "WORKSPACE", workspace):
                buf = StringIO()
                with redirect_stdout(buf):
                    cli.command_copy(args)

            self.assertTrue(Path(out_file).exists())
            self.assertEqual(Path(out_file).read_text(encoding="utf-8"), "class Solution:\n    pass\n")
            self.assertIn("exported", buf.getvalue())

    def test_prints_error_when_solution_missing(self):
        problem = make_problem()
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir) / "workspace"
            workspace.mkdir()

            args = SimpleNamespace(id=1, lang="en", out=None)
            with patch.object(cli, "find_problem", return_value=problem), \
                 patch.object(cli, "WORKSPACE", workspace):
                buf = StringIO()
                with redirect_stdout(buf):
                    cli.command_copy(args)

            self.assertIn("not found", buf.getvalue())

    def test_clipboard_fallback_prints_code(self):
        problem = make_problem()
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir) / "workspace"
            workspace.mkdir()
            (workspace / "001_two_sum.py").write_text("# my solution\n", encoding="utf-8")

            args = SimpleNamespace(id=1, lang="en", out=None)
            with patch.object(cli, "find_problem", return_value=problem), \
                 patch.object(cli, "WORKSPACE", workspace), \
                 patch.object(cli, "copy_to_clipboard", return_value=False):
                buf = StringIO()
                with redirect_stdout(buf):
                    cli.command_copy(args)

            self.assertIn("# my solution", buf.getvalue())

    def test_clipboard_success_prints_copied(self):
        problem = make_problem()
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir) / "workspace"
            workspace.mkdir()
            (workspace / "001_two_sum.py").write_text("# my solution\n", encoding="utf-8")

            args = SimpleNamespace(id=1, lang="en", out=None)
            with patch.object(cli, "find_problem", return_value=problem), \
                 patch.object(cli, "WORKSPACE", workspace), \
                 patch.object(cli, "copy_to_clipboard", return_value=True):
                buf = StringIO()
                with redirect_stdout(buf):
                    cli.command_copy(args)

            self.assertIn("copied", buf.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
