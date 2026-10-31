import shutil
Z = '/Users/petecopeland/Repos/.worktrees/z-c2/'
D = '/Users/petecopeland/Repos/.worktrees/z-dev-3bc6a2fb/'
R = '/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/receipts/2026-10-31-'
pairs = [
    (Z + 'scratch/pr.md', R + 'c2a-pr.md'),
    (Z + 'scratch/ab-c2a.txt', R + 'c2a-ab.txt'),
    (Z + 'scratch/ab-c2a-rep.txt', R + 'c2a-ab-rep.txt'),
    (Z + 'scratch/ab-c2a-swap.txt', R + 'c2a-ab-swap.txt'),
    (Z + 'scratch/camp-c2a-77457291.json', R + 'campaign-c2a-77457291.json'),
    (Z + 'scratch/camp-dev-3bc6a2fb.json', R + 'campaign-dev-3bc6a2fb.json'),
]
for a, b in pairs:
    shutil.copyfile(a, b)
s = open(D + 'devcheck.log').read()
open(R + 'dev-3bc6a2fb-suites.txt', 'w').write(s[s.rindex('--- SUMMARY'):])
s = open(Z + 'suite.log').read()
keep = [l for l in s.splitlines() if l.startswith('test result') or ' rc=' in l]
s = open(Z + 'scratch/crates.log').read()
keep += [l for l in s.splitlines() if l.startswith('===') or l.startswith('test result') or ' rc=' in l]
open(R + 'c2a-suite.txt', 'w').write('\n'.join(keep) + '\n')
