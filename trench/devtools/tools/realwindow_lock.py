#!/usr/bin/env python3
"""Run a command while holding ~/.claude/realwindow.lock (T33, dev-tools lane).

Why: the daily quiet board (~/.claude/hooks/quiet-board-daily.sh) runs
scripts/realsite_board.py from the atlas/trench-realsite hub, whose Chrome
oracle is headed (A1) by default and took no lock. On 11-08 it took frontmost
twice during a locked real-window run. Wrapping the board in this command
makes it wait for (or skip past) any real-window holder, and makes later
real-window runners wait for it.

    python3 realwindow_lock.py [--wait S] [--lock PATH] -- CMD ARGS...

Exit status: the command's; 75 (EX_TEMPFAIL) if the lock stayed busy for
--wait seconds (the command is not run). The lock is released on every exit
path, including SIGTERM/SIGINT/SIGHUP (forwarded to the child first).

The lock protocol is copied unchanged from RealWindowLock in
scripts/realsite_board.py on hiwave-macos develop (46ea55e3): a mkdir lock with
a pid file; a dead holder's lock is recovered by rename-then-mkdir; a lock
with no pid file (the batch recipe's bare mkdir) is never stale.
"""
import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

REALWINDOW_LOCK = Path.home() / ".claude" / "realwindow.lock"
EX_TEMPFAIL = 75


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


class RealWindowLock:
    """mkdir lock with a pid file (copied from realsite_board.py @ develop 46ea55e3)."""

    def __init__(self, path=None, wait_s=1200, poll_s=5.0, sleep=time.sleep, clock=time.monotonic):
        self.path = Path(path) if path else REALWINDOW_LOCK
        self.wait_s, self.poll_s, self.sleep, self.clock = wait_s, poll_s, sleep, clock
        self.held = False

    def holder(self):
        try:
            return int((self.path / "pid").read_text().strip())
        except (OSError, ValueError):
            return None

    def _mkdir(self):
        try:
            self.path.mkdir()
        except FileExistsError:
            return False
        (self.path / "pid").write_text(str(os.getpid()))
        self.held = True
        return True

    def _try(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self._mkdir():
            return True
        pid = self.holder()
        if pid is not None and pid != os.getpid() and not _pid_alive(pid):
            return self._recover(pid)
        return False

    def _recover(self, dead_pid):
        stale = self.path.with_name("%s.stale-%d-%d-%d" % (
            self.path.name, dead_pid, time.time_ns(), os.getpid()))
        try:
            os.rename(self.path, stale)
        except OSError:
            return False
        try:
            got = int((stale / "pid").read_text().strip())
        except (OSError, ValueError):
            got = None
        if got != dead_pid:
            if not os.path.lexists(self.path):
                try:
                    os.rename(stale, self.path)
                except OSError:
                    pass
            return False
        shutil.rmtree(stale, ignore_errors=True)
        return self._mkdir()

    def acquire(self):
        deadline = self.clock() + self.wait_s
        while True:
            if self._try():
                return True
            if self.clock() >= deadline:
                return False
            self.sleep(self.poll_s)

    def release(self):
        if not self.held:
            return
        self.held = False
        if self.holder() == os.getpid():
            shutil.rmtree(self.path, ignore_errors=True)


def run_locked(cmd, lock, log=lambda m: print(m, file=sys.stderr, flush=True)):
    t0 = time.monotonic()
    if not lock.acquire():
        log("realwindow_lock: %s busy (holder pid %s) after %ds; not running %s"
            % (lock.path, lock.holder(), lock.wait_s, cmd[0]))
        return EX_TEMPFAIL
    log("realwindow_lock: holding %s (waited %.0fs)" % (lock.path, time.monotonic() - t0))
    child = None

    def forward(signum, _frame):
        if child is not None and child.poll() is None:
            child.send_signal(signum)
        raise SystemExit(128 + signum)

    old = {s: signal.signal(s, forward) for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)}
    try:
        child = subprocess.Popen(cmd)
        return child.wait()
    finally:
        if child is not None and child.poll() is None:
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
        for s, h in old.items():
            signal.signal(s, h)
        lock.release()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--wait", type=int, default=3600, help="seconds to wait for the lock (default 3600)")
    ap.add_argument("--lock", default=str(REALWINDOW_LOCK))
    ap.add_argument("--poll", type=float, default=15.0)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not cmd:
        ap.error("no command (use: -- CMD ARGS...)")
    return run_locked(cmd, RealWindowLock(a.lock, wait_s=a.wait, poll_s=a.poll))


if __name__ == "__main__":
    sys.exit(main())
