"""stage.py: copy B18b receipts (small text + two crops) to the hub."""
import os
import shutil

S = '/Users/petecopeland/Repos/.worktrees/.scratch-b18b/'
W = '/Users/petecopeland/Repos/.worktrees/z-ch2-b18b/scratch/'
D = '/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/receipts/ch2-b18b/'
os.makedirs(D, exist_ok=True)
for f in ['make_cases.py', 'crop.py', 'progress.py', 'runlist.py', 'gates_ab.py', 'gates_ab.log',
          'red.log', 'pr-body.md', 'bing.png', 'wiki.png', 'stage.py']:
    shutil.copyfile(S + f, D + f)
for f in ['camp-b18b-18882673.log', 'ab-b18b.txt']:
    shutil.copyfile(W + f, D + f)
for extra in ['suite-18882673.log', 'rerun-1t.log', 'all.txt']:
    if os.path.exists(S + extra):
        shutil.copyfile(S + extra, D + extra)
print(sorted(os.listdir(D)))
