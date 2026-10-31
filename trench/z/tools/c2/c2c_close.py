"""C2(c): PR body from head + receipt, receipts to the hub."""
import shutil
W = '/Users/petecopeland/Repos/.worktrees/'
B = W + 'z-c2c/'
D = W + 'z-dev-546d6196/'
R = W + 'z-hub/trench/z/receipts/2026-10-31-'
body = open(B + 'scratch/pr-head.md').read() + open(B + 'scratch/receipt.md').read().rstrip() + \
    '\n\n\U0001F916 Generated with [Claude Code](https://claude.com/claude-code)\n'
open(B + 'scratch/pr.md', 'w').write(body)
for a, b in [(B + 'scratch/pr.md', R + 'c2c-pr.md'),
             (B + 'scratch/ab-c2c.txt', R + 'c2c-ab.txt'),
             (B + 'scratch/ab-c2c-swap.txt', R + 'c2c-ab-swap.txt'),
             (B + 'scratch/ab-c2c-shop.txt', R + 'c2c-ab-shop.txt'),
             (B + 'scratch/ab-c2c-shop2.txt', R + 'c2c-ab-shop2.txt'),
             (B + 'scratch/camp-c2c-f490aa7a.json', R + 'campaign-c2c-f490aa7a.json'),
             (D + 'scratch/camp-dev-546d6196.json', R + 'campaign-dev-546d6196.json')]:
    shutil.copyfile(a, b)
keep = []
for l in open(B + 'suite.log'):
    if l.startswith('test result') or ' rc=' in l:
        keep.append(l.rstrip())
for l in open(B + 'crates.log'):
    if l.startswith('===') or l.startswith('test result') or ' rc=' in l:
        keep.append(l.rstrip())
open(R + 'c2c-suite.txt', 'w').write('\n'.join(keep) + '\n')
s = open(D + 'devcheck.log').read()
open(R + 'dev-546d6196-suites.txt', 'w').write(s[s.rindex('--- SUMMARY'):])
print(len(body))
