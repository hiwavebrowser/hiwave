#!/usr/bin/env python3
"""run851red.py <log>: #851's new held tests through the lease; output in <worktree>/scratch/<log> and printed."""
import subprocess
import sys

subprocess.run(["python3", "/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/tools/c10/ct.py",
                "/Users/petecopeland/Repos/.worktrees/z-c2d-g", sys.argv[1],
                "test", "-p", "rustkit-engine", "--lib", "--features", "headless", "--", "transform_rect_tests::", "sticky_scroll_tests::", "--test-threads=4"])
print("RED-DONE", flush=True)
