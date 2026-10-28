"""rk_tree.py <binary> <html file> : engine box tree (type + border box) of a static page."""
import json, subprocess, sys

binary, html = sys.argv[1], sys.argv[2]
out = '/Users/petecopeland/Repos/.worktrees/z-786-apple/scratch/rk_tree_last.json'
r = subprocess.run([binary, '--html-file', html, '--width', '1280', '--height', '800', '--dump-layout', out],
                   capture_output=True, text=True)
if r.returncode:
    print('exit', r.returncode, r.stderr[-800:])
d = json.load(open(out))


def w(n, dep):
    b = n.get('border_box') or n.get('rect') or {k: v for k, v in n.items() if k != 'children'}
    print('  ' * dep, json.dumps(n['type'])[:90], [round(b[k]) for k in ('x', 'y', 'width', 'height')] if isinstance(b, dict) else b)
    for c in n.get('children', []):
        w(c, dep + 1)


w(d['root'], 0)
