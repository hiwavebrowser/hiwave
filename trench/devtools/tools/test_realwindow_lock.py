#!/usr/bin/env python3
"""Tests for realwindow_lock.py (T33). Run: python3 trench/devtools/tools/test_realwindow_lock.py

Scratch lock paths only; never touches ~/.claude. The last test is the red
one against the live hook: it fails while quiet-board-daily.sh runs the board
without holding the real-window lock.
"""
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import realwindow_lock as rw  # noqa: E402

TOOL = [sys.executable, str(HERE / "realwindow_lock.py")]
HOOK = Path(os.environ.get("QUIET_BOARD_HOOK") or Path.home() / ".claude" / "hooks" / "quiet-board-daily.sh")


def dead_pid():
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    return p.pid


class LockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.lock = Path(self.tmp.name) / "realwindow.lock"

    def tearDown(self):
        self.tmp.cleanup()

    def run_tool(self, *cmd, wait=1, timeout=30):
        return subprocess.run(TOOL + ["--wait", str(wait), "--poll", "0.2", "--lock", str(self.lock), "--"]
                              + list(cmd), capture_output=True, text=True, timeout=timeout)

    def test_free_lock_runs_the_command_under_the_lock_and_releases(self):
        probe = "import pathlib,sys;p=pathlib.Path(sys.argv[1]);print(p.is_dir(), (p/'pid').read_text())"
        r = self.run_tool(sys.executable, "-c", probe, str(self.lock))
        self.assertEqual(r.returncode, 0, r.stderr)
        held, pid = r.stdout.split()
        self.assertEqual(held, "True")
        self.assertTrue(pid.isdigit())
        self.assertFalse(self.lock.exists(), "lock left behind")

    def test_exit_status_is_the_commands(self):
        r = self.run_tool(sys.executable, "-c", "raise SystemExit(3)")
        self.assertEqual(r.returncode, 3)
        self.assertFalse(self.lock.exists())

    def test_live_holder_blocks_and_the_command_never_runs(self):
        holder = subprocess.Popen([sys.executable, "-c", "import time;time.sleep(30)"])
        try:
            self.lock.mkdir()
            (self.lock / "pid").write_text(str(holder.pid))
            marker = Path(self.tmp.name) / "ran"
            r = self.run_tool(sys.executable, "-c", "open(%r,'w')" % str(marker), wait=1)
            self.assertEqual(r.returncode, rw.EX_TEMPFAIL, r.stderr)
            self.assertIn("busy (holder pid %d)" % holder.pid, r.stderr)
            self.assertFalse(marker.exists())
            self.assertEqual((self.lock / "pid").read_text(), str(holder.pid))
        finally:
            holder.kill()
            holder.wait()

    def test_bare_dir_is_never_stale(self):
        self.lock.mkdir()
        r = self.run_tool(sys.executable, "-c", "pass", wait=1)
        self.assertEqual(r.returncode, rw.EX_TEMPFAIL)
        self.assertTrue(self.lock.is_dir())
        self.assertFalse((self.lock / "pid").exists())

    def test_dead_holder_is_recovered_with_no_stale_dir_left(self):
        self.lock.mkdir()
        (self.lock / "pid").write_text(str(dead_pid()))
        r = self.run_tool(sys.executable, "-c", "pass")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(list(Path(self.tmp.name).iterdir()), [])

    def test_holder_leaving_mid_wait_lets_us_in(self):
        self.lock.mkdir()
        subprocess.Popen([sys.executable, "-c",
                          "import time,os;time.sleep(1);os.rmdir(%r)" % str(self.lock)])
        t0 = time.monotonic()
        r = self.run_tool(sys.executable, "-c", "pass", wait=10)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertGreaterEqual(time.monotonic() - t0, 0.8)

    def test_release_never_removes_a_foreign_lock(self):
        lk = rw.RealWindowLock(self.lock, wait_s=0)
        self.assertTrue(lk.acquire())
        (self.lock / "pid").write_text("1")  # someone else's now
        lk.release()
        self.assertTrue(self.lock.is_dir())

    def test_sigterm_stops_the_child_and_releases(self):
        p = subprocess.Popen(TOOL + ["--lock", str(self.lock), "--", sys.executable, "-c",
                                     "import time;time.sleep(60)"], stderr=subprocess.DEVNULL)
        for _ in range(100):
            if (self.lock / "pid").exists():
                break
            time.sleep(0.05)
        self.assertTrue(self.lock.is_dir())
        time.sleep(0.3)  # let the child start
        t0 = time.monotonic()
        p.send_signal(signal.SIGTERM)
        self.assertEqual(p.wait(timeout=15), 128 + signal.SIGTERM)
        # Forwarded: the child stops at once, not after the 10 s fallback kill.
        self.assertLess(time.monotonic() - t0, 5.0)
        self.assertFalse(self.lock.exists(), "lock left after SIGTERM")


class HookTests(unittest.TestCase):
    @unittest.skipUnless(HOOK.exists(), "no live hook on this seat")
    def test_quiet_board_runs_the_board_under_the_realwindow_lock(self):
        """RED until the T33 hook patch is applied: the board line must go through realwindow_lock."""
        board_lines = [l for l in HOOK.read_text().splitlines()
                       if "realsite_board.py" in l and not l.lstrip().startswith("#")]
        self.assertTrue(board_lines, "no realsite_board.py line in the hook")
        for l in board_lines:
            self.assertIn("realwindow-lock", l, "board runs without the real-window lock: " + l.strip())


if __name__ == "__main__":
    unittest.main(verbosity=2)
