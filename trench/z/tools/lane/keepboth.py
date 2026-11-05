"""Resolve conflicts made only of `mod` / `#[cfg]` lines by keeping both sides (ours first).
Refuses any hunk with other content."""
import re, sys

p = sys.argv[1]
s = open(p).read()
pat = re.compile(r'<<<<<<< [^\n]*\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n', re.S)
n = 0
def fix(m):
    global n
    body = m.group(1) + m.group(2)
    for line in body.splitlines():
        t = line.strip()
        if t and not (t.startswith('mod ') or t.startswith('#[cfg') or t.startswith('pub mod ')):
            sys.exit('refusing: non-mod line in hunk: %r' % line)
    n += 1
    ours = m.group(1)
    theirs = m.group(2)
    if not ours.endswith('\n'):
        ours += '\n'
    # ours ends with a mod line; theirs starts with a mod line: insert the cfg between
    sep = '' if theirs.lstrip().startswith('#[cfg') else '#[cfg(test)]\n'
    return ours + sep + theirs
s = pat.sub(fix, s)
open(p, 'w').write(s)
print('resolved', n, 'left markers', s.count('<<<<<<<'))
