import json
import tempfile
import unittest
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from lc import settings, color, cli


class LoadSettingsTests(unittest.TestCase):
    def test_returns_defaults_when_no_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(settings, "SETTINGS_FILE", Path(tmpdir) / "missing.json"):
                result = settings.load_settings()
                self.assertEqual(result["theme"], "dark")
                self.assertEqual(result["font_size"], 16)

    def test_returns_saved_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "settings.json"
            f.write_text(json.dumps({"theme": "light", "font_size": 18}), encoding="utf-8")
            with patch.object(settings, "SETTINGS_FILE", f):
                result = settings.load_settings()
                self.assertEqual(result["theme"], "light")
                self.assertEqual(result["font_size"], 18)


class SaveUpdateSettingsTests(unittest.TestCase):
    def test_save_then_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "settings.json"
            with patch.object(settings, "SETTINGS_FILE", f), \
                 patch.object(settings, "DATA", Path(tmpdir)):
                settings.save_settings({"theme": "light", "font_size": 14})
                loaded = settings.load_settings()
                self.assertEqual(loaded["theme"], "light")
                self.assertEqual(loaded["font_size"], 14)

    def test_update_setting_preserves_others(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "settings.json"
            with patch.object(settings, "SETTINGS_FILE", f), \
                 patch.object(settings, "DATA", Path(tmpdir)):
                settings.save_settings({"theme": "dark", "font_size": 16})
                result = settings.update_setting("theme", "light")
                self.assertEqual(result["theme"], "light")
                self.assertEqual(result["font_size"], 16)


class ColorThemeTests(unittest.TestCase):
    def test_dark_mode_applies_color(self):
        with patch.object(color, "_use_color", return_value=True):
            result = color.red("hello")
            self.assertIn("hello", result)
            self.assertNotEqual(result, "hello")

    def test_light_mode_strips_color(self):
        with patch.object(color, "_use_color", return_value=False):
            self.assertEqual(color.red("hello"), "hello")
            self.assertEqual(color.green("hi"), "hi")
            self.assertEqual(color.bold("x"), "x")


class CommandConfigTests(unittest.TestCase):
    def test_shows_current_settings(self):
        args = SimpleNamespace(lang="en", theme=None, font_size=None)
        with patch.object(cli, "load_settings", return_value={"theme": "dark", "font_size": 16}):
            buf = StringIO()
            with redirect_stdout(buf):
                cli.command_config(args)
        self.assertIn("dark", buf.getvalue())
        self.assertIn("16", buf.getvalue())

    def test_sets_theme_to_light(self):
        args = SimpleNamespace(lang="en", theme="light", font_size=None)
        with patch.object(cli, "load_settings", return_value={"theme": "light", "font_size": 16}), \
             patch.object(cli, "update_setting", return_value={"theme": "light", "font_size": 16}):
            buf = StringIO()
            with redirect_stdout(buf):
                cli.command_config(args)
        self.assertIn("light", buf.getvalue())
        self.assertIn("saved", buf.getvalue().lower())

    def test_sets_font_size(self):
        args = SimpleNamespace(lang="en", theme=None, font_size=18)
        with patch.object(cli, "load_settings", return_value={"theme": "dark", "font_size": 18}), \
             patch.object(cli, "update_setting", return_value={"theme": "dark", "font_size": 18}):
            buf = StringIO()
            with redirect_stdout(buf):
                cli.command_config(args)
        self.assertIn("18", buf.getvalue())
        self.assertIn("saved", buf.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
