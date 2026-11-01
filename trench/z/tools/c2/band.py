#!/usr/bin/env python3
"""band.py <dir> <site>: the bands of rows and columns where the capture frames of a site differ, for each pair. Prints no page content."""
import glob
import itertools
import os
import sys


def ppm(path):
    data = open(path, "rb").read()
    fields, i = [], 0
    while len(fields) < 4:
        while data[i] in b" \t\r\n":
            i += 1
        j = i
        while data[j] not in b" \t\r\n":
            j += 1
        fields.append(data[i:j])
        i = j
    return int(fields[1]), int(fields[2]), data[i + 1 :]


d, site = sys.argv[1], sys.argv[2]
files = sorted(glob.glob(os.path.join(d, f"*{site}*.ppm")))
print([os.path.basename(f) for f in files])
frames = {f: ppm(f) for f in files}
for a, b in itertools.combinations(files, 2):
    wa, ha, pa = frames[a]
    wb, hb, pb = frames[b]
    if (wa, ha) != (wb, hb):
        print(os.path.basename(a), os.path.basename(b), "sizes", wa, ha, wb, hb)
        continue
    rows, x0, x1, n = [], wa, -1, 0
    for y in range(ha):
        ra = pa[y * wa * 3 : (y + 1) * wa * 3]
        rb = pb[y * wa * 3 : (y + 1) * wa * 3]
        if ra == rb:
            continue
        hit = False
        for x in range(wa):
            if max(abs(ra[x * 3 + c] - rb[x * 3 + c]) for c in range(3)) > 8:
                hit = True
                n += 1
                x0, x1 = min(x0, x), max(x1, x)
        if hit:
            rows.append(y)
    bands = []
    for y in rows:
        if bands and y <= bands[-1][1] + 2:
            bands[-1][1] = y
        else:
            bands.append([y, y])
    print(os.path.basename(a), os.path.basename(b), "px", n, "x", x0, x1, "y bands", bands[:12])
