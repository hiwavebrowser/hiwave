"""Open a held Z-lane PR from its hub receipt body.
usage: openpr.py <receipt.md> <branch> <merge-note>
Drops the title line and the 'PR body, ready to open' paragraph, adds the merge note."""
import subprocess, sys

rec, branch, note = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(rec).read()
title, _, rest = text.partition('\n')
paras = rest.strip('\n').split('\n\n')
paras = [p for p in paras if not p.startswith('PR body, ready to open')]
body = note + '\n\n' + '\n\n'.join(paras) + '\n'
out = '/Users/petecopeland/Repos/.worktrees/z-ch2-b14/scratch/body-' + branch.replace('/', '_') + '.md'
open(out, 'w').write(body)
r = subprocess.run(['gh', 'pr', 'create', '-R', 'hiwavebrowser/hiwave-macos', '--draft', '--base', 'develop',
                    '--head', branch, '--title', title.strip(), '--body-file', out], capture_output=True, text=True)
print(r.stdout, r.stderr)
