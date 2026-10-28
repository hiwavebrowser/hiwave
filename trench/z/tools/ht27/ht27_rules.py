"""ht27_rules.py <url> <out.json> <selector>... : run ht27_rules.mjs in pinned Chrome 148."""
import os, pathlib, subprocess, sys

WT = pathlib.Path(__file__).resolve().parent.parent
CHROME = '/Users/petecopeland/Repos/.worktrees/reduce-scratch/cft/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'
r = subprocess.run(['node', str(WT / 'tools/parity_oracle/ht27_rules.mjs')] + sys.argv[1:], capture_output=True, text=True,
                   env=dict(os.environ, PARITY_CHROME_PATH=CHROME), cwd=str(WT / 'tools/parity_oracle'), timeout=180)
print(r.returncode, (r.stdout + r.stderr)[-500:])
