"""t.py <worktree> <cargo args...> : run z-cargo, log to <worktree>/scratch/t-last.log, print errors, test lines, panics and results only."""
import re, subprocess, sys

wt = sys.argv[1]
r = subprocess.run(['python3', '/Users/petecopeland/Repos/.worktrees/z-cargo.py', wt] + sys.argv[2:], capture_output=True, text=True)
log = r.stdout + r.stderr
open(wt + '/scratch/t-last.log', 'w').write(log)
lines = log.splitlines()
for i, l in enumerate(lines):
    if re.match(r'^(test |test result|error(\[|:)|thread .* panicked|  left:|  right:)', l) or l.startswith('---- '):
        print(l[:600])
        if l.startswith('error'):
            print('\n'.join(x[:300] for x in lines[i + 1:i + 12]))
print('exit', r.returncode)
