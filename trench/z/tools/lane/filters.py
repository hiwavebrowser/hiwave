"""Run targeted rustkit-engine lib filters through z-cargo; print each result line."""
import subprocess, sys

WT = '/Users/petecopeland/Repos/.worktrees/z-ch2-b14'
for f in sys.argv[1:]:
    r = subprocess.run(['python3', '/Users/petecopeland/Repos/.worktrees/z-cargo.py', WT, 'test', '-p', 'rustkit-engine',
                        '--features', 'headless', '--lib', f], capture_output=True, text=True)
    out = (r.stdout + r.stderr).splitlines()
    res = [l for l in out if l.startswith('test result')]
    bad = [l for l in out if l.endswith('FAILED') or 'GPU test guard' in l]
    print(f, res[-1] if res else 'NO RESULT (rc %d)' % r.returncode, *bad[:12], sep='\n  ', flush=True)
    if not res:
        print('\n'.join(out[-15:]))
