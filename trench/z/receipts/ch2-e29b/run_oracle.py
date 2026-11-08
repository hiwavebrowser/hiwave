import os, subprocess, sys
CHROME = os.path.expanduser("~/Repos/hiwave/hiwave-macos/.browsers/chrome/mac_arm-148.0.7778.216/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing")
WT = "/Users/petecopeland/Repos/.worktrees/z-ch2-e29b/tools/parity_oracle"
env = dict(os.environ, PARITY_CHROME_PATH=CHROME)
# argv: script.mjs [args...] [> outfile via --out=]
out = None
args = []
for a in sys.argv[1:]:
    if a.startswith("--out="):
        out = a[6:]
    else:
        args.append(a)
r = subprocess.run(["node", os.path.join(WT, args[0])] + args[1:], cwd=WT, env=env, capture_output=True, text=True)
text = r.stdout + r.stderr
if out:
    open(out, "w").write(text)
    print("exit", r.returncode, "bytes", len(text))
else:
    print(text)
    print("exit", r.returncode)
