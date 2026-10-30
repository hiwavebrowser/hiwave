"""Bank SV1's small text receipts on the hub, then show the plan's Z-lane rows' state."""
import re, shutil
W = '/Users/petecopeland/Repos/.worktrees/'
R = W + 'z-hub/trench/z/receipts/2026-10-30-'
shutil.copy(W + 'z-sv1/scratch/camp-57e44dd2.log', R + 'campaign-sv1-57e44dd2.log')
shutil.copy(W + 'z-dev-62e745f1/scratch/camp-62e745f1.log', R + 'campaign-dev-62e745f1.log')
with open(R + 'sv1-ab.txt', 'w') as out:
    for tag in ('sv1', 'sv1b', 'sv1c'):
        out.write('--- pass %s (A develop 62e745f1, B candidate 57e44dd2)\n' % tag)
        out.write(open(W + 'z-sv1/scratch/ab-%s.txt' % tag).read())
def summary(path):
    s = open(path, errors='replace').read()
    i = s.find('--- SUMMARY ---')
    if i >= 0:
        return s[i:]
    return '\n'.join(l for l in s.splitlines() if l.startswith('test result') or 'FAILED' in l) + '\n'
open(R + 'dev-62e745f1-suites.txt', 'w').write('develop 62e745f1 standing check (devcheck.py)\n' + summary(W + 'z-dev-62e745f1/devcheck.log'))
open(R + 'sv1-suite-57e44dd2.txt', 'w').write('candidate 57e44dd2 headless engine suite\n' + summary(W + 'z-dev-62e745f1/sv1-suite.log'))
for line in open(W + 'z-hub/trench/z/PLAN-z.md'):
    m = re.match(r'\| *([A-Za-z0-9 #()-]+?) *\|', line)
    if m and line.count('|') >= 6 and 'Z lane' in line:
        cells = line.split('|')
        print(m.group(1), '| state:', cells[5].strip()[:30], '| notes:', cells[6].strip()[:230])
