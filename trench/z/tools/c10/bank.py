#!/usr/bin/env python3
"""bank.py: small text receipts of C10(b) and C10(b2) to the hub; fills #852 into the b2 body and b's next-PR line."""
import shutil
W = '/Users/petecopeland/Repos/.worktrees/'
R = W + 'z-hub/trench/z/receipts/2026-11-01-'
B, B2 = W + 'z-c10b/', W + 'z-c10b2/'
p = B2 + 'scratch/pr-final.md'
s = open(p).read().replace('**Stacked on the C10(b) PR:**', '**Stacked on #852 (C10(b)):**').replace('until that lands', 'until #852 lands').replace('(from the C10(b) PR)', '(from #852)')
open(p, 'w').write(s)
pairs = [
    (B + 'scratch/pr-final.md', 'c10b-pr.md'), (B2 + 'scratch/pr-final.md', 'c10b2-pr.md'),
    (B + 'scratch/ab-c10b.txt', 'c10b-ab.txt'), (B + 'scratch/ab-c10b-rep.txt', 'c10b-ab-rep.txt'), (B + 'scratch/ab-c10b-rep-cnn.txt', 'c10b-ab-cnn.txt'),
    (B2 + 'scratch/ab-c10b2.txt', 'c10b2-ab.txt'), (B2 + 'scratch/ab-c10b2-rep.txt', 'c10b2-ab-rep.txt'), (B2 + 'scratch/ab-c10b2-rep-cnn.txt', 'c10b2-ab-cnn.txt'),
    (B + 'scratch/red.txt', 'c10b-red.txt'), (B2 + 'scratch/red.txt', 'c10b2-red.txt'),
    (B + 'scratch/camp-c10b-9551f252.json', 'campaign-c10b-9551f252.json'), (B2 + 'scratch/camp-c10b2-64e4081e.json', 'campaign-c10b2-64e4081e.json'),
    (W + 'z-base-546d6196/scratch/camp-base-546d6196.json', 'campaign-base-546d6196.json'),
]
for a, b in pairs:
    shutil.copyfile(a, R + b)
for wt, tag in ((B, 'c10b'), (B2, 'c10b2')):
    keep = []
    for f in ('crates.log', 'suite.log'):
        keep += [l for l in open(wt + f, errors='replace').read().splitlines() if l.startswith(('===', 'test result')) or ' rc=' in l]
    open(R + tag + '-suite.txt', 'w').write('\n'.join(keep) + '\n')
print('banked', len(pairs) + 2)
