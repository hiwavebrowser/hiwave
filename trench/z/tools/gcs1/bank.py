"""Bank GCS1's small text receipts on the hub and print what the PR body needs."""
import hashlib, shutil
W = '/Users/petecopeland/Repos/.worktrees/'
R = W + 'z-hub/trench/z/receipts/2026-10-30-'
shutil.copy(W + 'z-gcs1/scratch/camp-0b85919b.log', R + 'campaign-gcs1-0b85919b.txt')
with open(R + 'gcs1-ab.txt', 'w') as out:
    for tag in ('gcs1', 'gcs1b', 'gcs1c'):
        out.write('--- pass %s (A develop 62e745f1, B candidate 0b85919b)\n' % tag)
        out.write(open(W + 'z-gcs1/scratch/ab-%s.txt' % tag).read())
s = open(W + 'z-dev-gcs1/gcs1-suite.log', errors='replace').read()
rows = [l for l in s.splitlines() if l.startswith('test result') or 'FAILED' in l or l.startswith('error')]
open(R + 'gcs1-suite-0b85919b.txt', 'w').write('candidate 0b85919b headless engine suite\n' + '\n'.join(rows) + '\n')
print('\n'.join(rows))
for name, wt in (('develop', 'z-dev-gcs1'), ('candidate', 'z-gcs1')):
    print(name, hashlib.sha256(open(W + wt + '/target/parity/parity-capture', 'rb').read()).hexdigest())
for line in open(W + 'z-gcs1/scratch/ab-gcs1.txt'):
    if line.split()[0] in ('netflix', 'apple', 'github'):
        print(line.strip()[:160])
