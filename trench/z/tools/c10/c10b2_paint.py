#!/usr/bin/env python3
"""C10(b2): does the paint follow? A lime box under each 3D transform, frames from the two binaries.
usage: c10b2_paint.py <base binary> <candidate binary> <scratch dir>. Prints each box's lime bounds per binary.
Wanted bounds are the Chromium 143 rects of the same boxes (c10b2_probe.mjs), each box at (20,10) 100x50 on its own page."""
import pathlib, subprocess, sys
base, cand, s = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
s.mkdir(exist_ok=True)
cases = [
    ('translate3d(30px,40px,0)', (50, 50, 149, 99)),
    ('translate3d(-10%,20%,100px)', (10, 20, 109, 69)),
    ('rotateX(60deg)', (20, 22, 119, 47)),
    ('rotateY(60deg)', (45, 10, 94, 59)),
    ('scale3d(.5,.5,1)', (45, 22, 94, 47)),
    ('matrix3d(1,0,0,0, 0,1,0,0, 0,0,1,0, 7,9,0,1)', (27, 19, 126, 68)),
    ('translateX(30px) nonsense(1)', (20, 10, 119, 59)),
]
def bounds(binary, value, i):
    page = s / ('p%d.html' % i)
    page.write_text('<!doctype html><style>html,body{background:#fff;margin:0}'
                    '#a{position:absolute;left:20px;top:10px;width:100px;height:50px;background:#0f0;transform:%s}</style><div id=a></div>' % value)
    frame = s / ('p%d.ppm' % i)
    r = subprocess.run([binary, '--html-file', str(page), '--dump-frame', str(frame), '--width', '300', '--height', '200'],
                       capture_output=True, text=True, timeout=120)
    if r.returncode:
        return 'rc %d' % r.returncode
    d = frame.read_bytes()
    _, w, h, _ = d.split(maxsplit=3)
    w, h = int(w), int(h)
    px = d[len(d) - w * h * 3:]
    pts = [(x, y) for y in range(h) for x in range(w) if px[(y * w + x) * 3:(y * w + x) * 3 + 3] == b'\x00\xff\x00']
    if not pts:
        return None
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))
for i, (value, want) in enumerate(cases):
    print('%-48s want %-22s base %-22s cand %s' % (value, want, bounds(base, value, i), bounds(cand, value, i)))
