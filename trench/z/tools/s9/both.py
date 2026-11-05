"""both.py <binary> <page.html>...: rects of every id in Chromium and in the engine (layout dump).
Rows: id  chrome x y w h  |  engine x y w h  (engine = first layout box whose element id matches)."""
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).parent
PW = '/Users/petecopeland/Repos/.worktrees/handtest-atlasa3fa/tools/parity_oracle'
binary = sys.argv[1]


def walk(node, out):
    if isinstance(node, dict):
        eid = None
        sel = node.get('selector')
        if isinstance(sel, str) and sel.startswith('#'):
            eid = sel[1:].split('.')[0]
        r = node.get('rect') or node.get('border_box') or node.get('box')
        if eid and isinstance(r, dict) and eid not in out:
            out[eid] = (r.get('x'), r.get('y'), r.get('width'), r.get('height'))
        for v in node.values():
            walk(v, out)
    elif isinstance(node, list):
        for v in node:
            walk(v, out)


for page in sys.argv[2:]:
    page = pathlib.Path(page)
    c = subprocess.run(['node', str(HERE / 'rects_probe.mjs'), PW, str(page)], capture_output=True, text=True)
    chrome = {}
    for line in c.stdout.splitlines():
        if line.startswith('//'):
            ver = line
            continue
        p = line.split()
        chrome[p[0]] = tuple(float(x) for x in p[1:])
    lay = page.with_suffix('.layout.json')
    e = subprocess.run([binary, '--html-file', str(page), '--dump-layout', str(lay),
                        '--dump-frame', str(page.with_suffix('.ppm'))], capture_output=True, text=True)
    eng = {}
    if lay.exists():
        walk(json.loads(lay.read_text()), eng)
    else:
        print('engine failed', e.stderr[-300:])
    print('==', page.name, c.stderr[-200:])
    for k in chrome:
        er = eng.get(k)
        es = ' '.join('%.2f' % v for v in er) if er and None not in er else str(er)
        print('%-8s %-32s | %s' % (k, ' '.join('%.2f' % v for v in chrome[k]), es))
