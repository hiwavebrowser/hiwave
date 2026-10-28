"""ev.py <url> <expr file> <out file> : evaluate an expression file in pinned Chrome 148 after load; full output to a file."""
import json, os, pathlib, subprocess, sys

WT = pathlib.Path(__file__).resolve().parent.parent
CHROME = '/Users/petecopeland/Repos/.worktrees/reduce-scratch/cft/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'
url, expr, out = sys.argv[1], open(sys.argv[2]).read(), sys.argv[3]
r = subprocess.run(['node', str(WT / 'tools/parity_oracle/ht27_eval.mjs'), url, expr], capture_output=True, text=True,
                   env=dict(os.environ, PARITY_CHROME_PATH=CHROME), cwd=str(WT / 'tools/parity_oracle'), timeout=180)
txt = r.stdout
try:
    txt = json.loads(txt[txt.index('"'):]) if txt.lstrip().startswith('"') else txt
except Exception:
    pass
open(out, 'w').write(txt if isinstance(txt, str) else str(txt))
print(r.returncode, len(txt), r.stderr[-500:])
