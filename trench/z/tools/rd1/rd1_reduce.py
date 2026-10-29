"""rd1_reduce.py <binary>...: RD1 reduced. An inline SVG whose shape takes its fill from
an author class rule, inside a flex item; the item with and without `z-index: 1`.
Chrome paints #ff4500 in every case."""
import pathlib, subprocess, sys

import numpy as np

d = pathlib.Path(__file__).with_name('rd1_fx')
d.mkdir(exist_ok=True)
PAGE = """<!doctype html><html><head><style>
body{margin:0} main{display:flex} .logo{display:flex;%s}
.logo svg{fill:currentColor;width:200px;height:200px} .a{fill:#ff4500}
</style></head><body><main><div class="logo"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
<rect class="a" x="0" y="0" width="200" height="200"></rect></svg></div></main></body></html>"""
CASES = {'no_z': '', 'z1': 'z-index:1', 'z1_relative': 'z-index:1;position:relative', 'z0': 'z-index:0'}


def ppm(p):
    data = p.read_bytes()
    m, w, h, rest = data.split(maxsplit=3)
    w, h = int(w), int(h)
    px = rest[len(rest.split(maxsplit=1)[0]) + 1:]
    return np.frombuffer(px[:w * h * 3], dtype=np.uint8).reshape(h, w, 3)


for b in sys.argv[1:]:
    print(b)
    for name, css in CASES.items():
        page = d / ('reduce_%s.html' % name)
        page.write_text(PAGE % css)
        out = d / ('reduce_%s.ppm' % name)
        subprocess.run([b, '--html-file', str(page), '--width', '400', '--height', '300', '--dump-frame', str(out)], capture_output=True)
        print('  %-12s %s' % (name, tuple(ppm(out)[100, 100])))
