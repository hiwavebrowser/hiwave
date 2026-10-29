"""pseudo_probe.py <binary>: abspos ::before with display:none / opacity, as reddit's
interstitial disc (main:before{...;opacity:.75;position:absolute;animation:...}).
Prints the colour at the pseudo's centre. Chrome: none -> white; opacity .75 of #d93900
over white -> about (227,107,64)."""
import pathlib, subprocess, sys

import numpy as np

d = pathlib.Path(__file__).with_name('rd1_fx')
d.mkdir(exist_ok=True)
PAGE = """<!doctype html><html><head><style>
body{margin:0} main{position:relative;width:300px;height:300px}
main:before{%s background-color:#d93900;content:'';height:100px;width:100px;position:absolute}
</style></head><body><main></main></body></html>"""
CASES = {
    'plain': ('', (217, 57, 0)),
    'display_none': ('display:none;', (255, 255, 255)),
    'opacity': ('opacity:.75;', (227, 107, 64)),
    'opacity_anim': ('animation:s 1.5s infinite ease-in-out;opacity:.75;', (227, 107, 64)),
}
EXTRA = '@keyframes s{0%{transform:scale(1)}100%{transform:scale(1.5);opacity:0}}'


def ppm(p):
    data = p.read_bytes()
    m, w, h, rest = data.split(maxsplit=3)
    w, h = int(w), int(h)
    px = rest[len(rest.split(maxsplit=1)[0]) + 1:]
    return np.frombuffer(px[:w * h * 3], dtype=np.uint8).reshape(h, w, 3)


for name, (css, want) in CASES.items():
    page = d / ('pseudo_%s.html' % name)
    page.write_text((PAGE % css).replace('</style>', EXTRA + '</style>'))
    out = d / ('pseudo_%s.ppm' % name)
    subprocess.run([sys.argv[1], '--html-file', str(page), '--width', '400', '--height', '300', '--dump-frame', str(out)], capture_output=True)
    got = tuple(int(x) for x in ppm(out)[50, 50])
    ok = all(abs(a - b) <= 8 for a, b in zip(got, want))
    print('%-14s want %-16s got %-16s %s' % (name, want, got, 'ok' if ok else 'WRONG'))
