#!/usr/bin/env python3
"""Where develop's binary places an absolute box with no positioned ancestor.
usage: c2c_abs_develop.py <binary> <scratch dir>. Prints the rows of the lime box in the frame."""
import pathlib, subprocess, sys
binary, s = sys.argv[1], pathlib.Path(sys.argv[2])
s.mkdir(exist_ok=True)
page = s / 'abs.html'
page.write_text('<!doctype html><style>html,body{background:#fff}body{margin:0;height:1000px}'
                '#a{position:absolute;left:10px;top:300px;width:20px;height:20px;background:#0f0}</style>'
                '<body><div style="height:200px"></div><div><div id=a></div></div></body>')
frame = s / 'abs.ppm'
r = subprocess.run([binary, '--html-file', str(page), '--dump-frame', str(frame), '--width', '100', '--height', '800'],
                   capture_output=True, text=True, timeout=120)
print('rc', r.returncode, r.stderr[-200:] if r.returncode else '')
d = frame.read_bytes()
magic, w, h, rest = d.split(maxsplit=3)
w, h = int(w), int(h)
px = d[len(d) - w * h * 3:]
rows = [y for y in range(h) if px[(y * w + 15) * 3:(y * w + 15) * 3 + 3] == b'\x00\xff\x00']
print('frame', w, h, 'lime rows', (rows[0], rows[-1]) if rows else None, '(Chromium would be 300..319; from the parent 500..519)')
