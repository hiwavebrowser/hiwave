"""px.py <binary> <html> x,y ... : render a static page and print the frame's RGB at each point; also text colours in the display list."""
import json, subprocess, sys

binary, html, pts = sys.argv[1], sys.argv[2], sys.argv[3:]
ppm = '/Users/petecopeland/Repos/.worktrees/z-786-apple/scratch/px_last.ppm'
dl = '/Users/petecopeland/Repos/.worktrees/z-786-apple/scratch/px_last_dl.json'
r = subprocess.run([binary, '--html-file', html, '--dump-frame', ppm, '--dump-display-list', dl], capture_output=True, text=True)
if r.returncode:
    print('exit', r.returncode, r.stderr[-500:])
data = open(ppm, 'rb').read()
magic, w, h, rest = data.split(maxsplit=3)
w, h = int(w), int(h)
px = rest[len(rest.split(maxsplit=1)[0]) + 1:]
for p in pts:
    x, y = map(int, p.split(','))
    i = (y * w + x) * 3
    print(p, tuple(px[i:i + 3]))
d = json.load(open(dl))
cmds = d.get('commands', d) if isinstance(d, dict) else d
for c in cmds[:40]:
    s = json.dumps(c)
    print(s[:220])
