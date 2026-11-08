import os, subprocess, sys
CHROME = os.path.expanduser("~/Repos/hiwave/hiwave-macos/.browsers/chrome/mac_arm-148.0.7778.216/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing")
WT = "/Users/petecopeland/Repos/.worktrees/z-ch2-e37/tools/parity_oracle"
env = dict(os.environ, PARITY_CHROME_PATH=CHROME)
r = subprocess.run(["node", os.path.join(WT, sys.argv[1])] + sys.argv[2:], cwd=WT, env=env, capture_output=True, text=True)
print(r.stdout + r.stderr)
print("exit", r.returncode)
