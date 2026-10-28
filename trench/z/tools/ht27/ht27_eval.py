"""ht27_eval.py [--ua UA] [--save PREFIX] <url> <js expression> : evaluate in pinned Chrome 148 after load."""
import os, pathlib, subprocess, sys

WT = pathlib.Path(__file__).resolve().parent.parent
CHROME = '/Users/petecopeland/Repos/.worktrees/reduce-scratch/cft/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'
args, env = sys.argv[1:], dict(os.environ, PARITY_CHROME_PATH=CHROME)
while args and args[0] in ('--ua', '--save', '--init'):
    env[{'--ua': 'HT27_UA', '--save': 'HT27_SAVE', '--init': 'HT27_INIT'}[args[0]]] = args[1]
    args = args[2:]
r = subprocess.run(['node', str(WT / 'tools/parity_oracle/ht27_eval.mjs')] + args, capture_output=True, text=True,
                   env=env, cwd=str(WT / 'tools/parity_oracle'), timeout=180)
print(r.returncode, (r.stdout + r.stderr)[-6000:])
