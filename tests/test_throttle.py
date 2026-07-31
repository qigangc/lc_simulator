import datetime
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lc import throttle


class CheckCooldownTests(unittest.TestCase):
    def test_allows_run_when_no_progress_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(throttle, "PROGRESS_FILE", Path(tmpdir) / "missing.json"), \
                 patch.object(throttle, "DATA", Path(tmpdir)):
                can_run, remaining = throttle.check_cooldown(1)
                self.assertTrue(can_run)
                self.assertEqual(remaining, 0)

    def test_blocks_run_within_cooldown_window(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            prog = Path(tmpdir) / "progress.json"
            now = datetime.datetime.now().isoformat(timespec="seconds")
            prog.write_text(json.dumps({"last_test": {"1": now}}), encoding="utf-8")
            with patch.object(throttle, "PROGRESS_FILE", prog), \
                 patch.object(throttle, "TEST_COOLDOWN_SECONDS", 5.0):
                can_run, remaining = throttle.check_cooldown(1)
                self.assertFalse(can_run)
                self.assertGreater(remaining, 0)
                self.assertLessEqual(remaining, 5)

    def test_allows_run_after_cooldown_expires(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            prog = Path(tmpdir) / "progress.json"
            old = (datetime.datetime.now() - datetime.timedelta(seconds=10)).isoformat(timespec="seconds")
            prog.write_text(json.dumps({"last_test": {"1": old}}), encoding="utf-8")
            with patch.object(throttle, "PROGRESS_FILE", prog), \
                 patch.object(throttle, "TEST_COOLDOWN_SECONDS", 3.0):
                can_run, remaining = throttle.check_cooldown(1)
                self.assertTrue(can_run)
                self.assertEqual(remaining, 0)


class AcquireReleaseLockTests(unittest.TestCase):
    def test_acquire_then_block_second_acquire(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(throttle, "LOCK_FILE", Path(tmpdir) / ".test_lock"), \
                 patch.object(throttle, "DATA", Path(tmpdir)):
                self.assertTrue(throttle.acquire_lock())
                self.assertFalse(throttle.acquire_lock())

    def test_release_allows_reacquire(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(throttle, "LOCK_FILE", Path(tmpdir) / ".test_lock"), \
                 patch.object(throttle, "DATA", Path(tmpdir)):
                throttle.acquire_lock()
                throttle.release_lock()
                self.assertTrue(throttle.acquire_lock())

    def test_stale_lock_is_overwritten(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lock = Path(tmpdir) / ".test_lock"
            old = (datetime.datetime.now() - datetime.timedelta(seconds=120)).isoformat(timespec="seconds")
            lock.write_text(json.dumps({"pid": 999, "at": old}), encoding="utf-8")
            with patch.object(throttle, "LOCK_FILE", lock), \
                 patch.object(throttle, "DATA", Path(tmpdir)), \
                 patch.object(throttle, "LOCK_TIMEOUT_SECONDS", 60.0):
                self.assertTrue(throttle.acquire_lock())


class RecordTestTimeTests(unittest.TestCase):
    def test_writes_timestamp_to_progress(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            prog = Path(tmpdir) / "progress.json"
            with patch.object(throttle, "PROGRESS_FILE", prog), \
                 patch.object(throttle, "DATA", Path(tmpdir)):
                throttle.record_test_time(42)
                data = json.loads(prog.read_text(encoding="utf-8"))
                self.assertIn("42", data["last_test"])


if __name__ == "__main__":
    unittest.main()
