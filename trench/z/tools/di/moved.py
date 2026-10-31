#!/usr/bin/env python3
"""moved.py <a.ppm> <b.ppm> <out.png> [chrome.png]: y bands and x extent where two frames differ; a stacked PNG of A, B (and Chrome) cropped to the changed band."""
import sys
import numpy as np
from PIL import Image


def ppm(path):
    data = open(path, "rb").read()
    magic, w, h, rest = data.split(maxsplit=3)
    w, h = int(w), int(h)
    pixels = rest[len(rest.split(maxsplit=1)[0]) + 1:]
    return np.frombuffer(pixels[: w * h * 3], dtype=np.uint8).reshape(h, w, 3)


a, b = ppm(sys.argv[1]), ppm(sys.argv[2])
if a.shape != b.shape:
    print("shapes differ", a.shape, b.shape)
    sys.exit(0)
d = (np.abs(a.astype(np.int16) - b.astype(np.int16)).max(axis=2) > 8)
print("differs %.2f%%" % (d.mean() * 100))
rows = np.where(d.any(axis=1))[0]
if not len(rows):
    sys.exit(0)
bands, start, prev = [], rows[0], rows[0]
for r in rows[1:]:
    if r > prev + 4:
        bands.append((start, prev)); start = r
    prev = r
bands.append((start, prev))
for y0, y1 in bands:
    cols = np.where(d[y0 : y1 + 1].any(axis=0))[0]
    print("y %d-%d x %d-%d px %d" % (y0, y1, cols[0], cols[-1], d[y0 : y1 + 1].sum()))
y0, y1 = max(0, rows[0] - 20), min(a.shape[0], rows[-1] + 20)
parts = [a[y0:y1], np.full((4, a.shape[1], 3), 255, np.uint8), b[y0:y1]]
if len(sys.argv) > 4:
    c = np.array(Image.open(sys.argv[4]).convert("RGB"))
    parts += [np.full((4, a.shape[1], 3), 255, np.uint8), c[y0:y1, : a.shape[1]]]
Image.fromarray(np.vstack(parts)).save(sys.argv[3])
