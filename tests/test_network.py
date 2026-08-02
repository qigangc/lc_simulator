import unittest
from io import StringIO
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from lc import cli
from lc import network


class IsOnlineTests(unittest.TestCase):
    def test_returns_false_on_connection_error(self):
        with patch("lc.network.socket.create_connection", side_effect=OSError("refused")):
            self.assertFalse(network.is_online())

    def test_returns_true_on_successful_connection(self):
        class FakeSocket:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass

        with patch("lc.network.socket.create_connection", return_value=FakeSocket()):
            self.assertTrue(network.is_online())


class FetchProblemContentOfflineTests(unittest.TestCase):
    def test_returns_offline_when_not_online(self):
        with patch.object(network, "is_online", return_value=False):
            result = network.fetch_problem_content("two-sum")
        self.assertEqual(result["status"], "offline")
        self.assertIsNone(result["data"])

    def test_returns_missing_dependency_when_no_requests(self):
        import builtins

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "requests":
                raise ImportError("no requests")
            return real_import(name, *args, **kwargs)

        with patch.object(network, "is_online", return_value=True), \
             patch.object(builtins, "__import__", side_effect=fake_import):
            result = network.fetch_problem_content("two-sum")
        self.assertEqual(result["status"], "missing_dependency")


class CommandFetchOfflineTests(unittest.TestCase):
    def test_prints_offline_message_when_not_online(self):
        args = SimpleNamespace(id=None, lang="en", limit=None, force=False)
        with patch.object(cli, "is_online", return_value=False):
            buf = StringIO()
            with redirect_stdout(buf):
                cli.command_fetch(args)
        self.assertIn("offline", buf.getvalue().lower())
        self.assertNotIn("Traceback", buf.getvalue())

    def test_prints_offline_message_in_chinese(self):
        args = SimpleNamespace(id=None, lang="zh", limit=None, force=False)
        with patch.object(cli, "is_online", return_value=False):
            buf = StringIO()
            with redirect_stdout(buf):
                cli.command_fetch(args)
        self.assertIn("离线模式", buf.getvalue())


class CommandFetchOnlineTests(unittest.TestCase):
    def test_fetch_single_problem_success(self):
        problem = {"id": 1, "slug": "two-sum", "title_en": "Two Sum"}
        fetch_result = {"status": "ok", "data": {"content": "<p>hi</p>"}, "message": "ok"}
        args = SimpleNamespace(id=1, lang="en", limit=None, force=False)
        with patch.object(cli, "is_online", return_value=True), \
             patch.object(cli, "find_problem", return_value=problem), \
             patch.object(cli, "fetch_problem_content", return_value=fetch_result):
            buf = StringIO()
            with redirect_stdout(buf):
                cli.command_fetch(args)
        self.assertIn("Fetched", buf.getvalue())

    def test_fetch_midway_offline_stops_gracefully(self):
        problems = [
            {"id": 1, "slug": "two-sum"},
            {"id": 2, "slug": "add-two-numbers"},
        ]
        fetch_result = {"status": "offline", "data": None, "message": "disconnected"}
        args = SimpleNamespace(id=None, lang="en", limit=None, force=False)
        with patch.object(cli, "is_online", return_value=True), \
             patch.object(cli, "load_problems", return_value=problems), \
             patch.object(cli, "fetch_problem_content", return_value=fetch_result):
            buf = StringIO()
            with redirect_stdout(buf):
                cli.command_fetch(args)
        self.assertIn("offline", buf.getvalue().lower())
        self.assertNotIn("Traceback", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
