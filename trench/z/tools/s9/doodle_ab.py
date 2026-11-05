"""doodle_ab.py <dir>: render <dir>/static.html with scratch/bins/base and scratch/bins/cand
(worktree = dir/../..), print the #hplogo image box from each layout, and write
<dir>/sbs.png (Chrome | base | candidate, half size)."""
import json, pathlib, subprocess, sys
from PIL import Image

d = pathlib.Path(sys.argv[1]).resolve()
wt = d.parent.parent
rows = []


def find(node, out):
    if isinstance(node, dict):
        if node.get('selector', '').startswith('#hplogo'):
            out.append(node.get('border_box'))
        for v in node.values():
            find(v, out)
    elif isinstance(node, list):
        for v in node:
            find(v, out)


for arm in ('base', 'cand'):
    lay, ppm = d / (arm + '.layout.json'), d / (arm + '.ppm')
    r = subprocess.run([str(wt / 'scratch/bins' / arm), '--html-file', str(d / 'static.html'),
                        '--dump-layout', str(lay), '--dump-frame', str(ppm), '--timeout-ms', '60000'],
                       capture_output=True, text=True)
    hits = []
    if lay.exists():
        find(json.loads(lay.read_text()), hits)
    print(arm, 'rc', r.returncode, 'hplogo', hits[:2])
    rows.append(Image.open(ppm).convert('RGB'))
chrome = Image.open(d / 'chrome.png').convert('RGB')
imgs = [chrome] + rows
w = sum(i.width for i in imgs)
out = Image.new('RGB', (w, max(i.height for i in imgs)), 'white')
x = 0
for i in imgs:
    out.paste(i, (x, 0))
    x += i.width
out.resize((w // 3, out.height // 3)).save(d / 'sbs.png')
print(d / 'sbs.png')
