#!/usr/bin/env python3
"""ppm_bands.py <frame.ppm> <out.png> [band px]: ink per horizontal band, and a half-size PNG to look at."""
import pathlib
import re
import struct
import sys
import zlib

data = pathlib.Path(sys.argv[1]).read_bytes()
band = int(sys.argv[3]) if len(sys.argv) > 3 else 200
m = re.match(rb"P6\s+(\d+)\s+(\d+)\s+(\d+)\s", data)
w, h = int(m[1]), int(m[2])
px = data[m.end():]
for top in range(0, h, band):
    ink = total = 0
    for y in range(top, min(top + band, h), 4):
        row = px[y * w * 3:(y + 1) * w * 3]
        for x in range(0, w * 3, 12):
            total += 1
            ink += min(row[x:x + 3]) < 235
    print(f"y {top}..{top + band}: ink {100 * ink / total:.1f}%")
rows = bytearray()
for y in range(0, h, 2):
    rows.append(0)
    row = px[y * w * 3:(y + 1) * w * 3]
    for x in range(0, w * 3, 6):
        rows += row[x:x + 3]


def chunk(kind, body):
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))


png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w // 2 + w % 2, h // 2 + h % 2, 8, 2, 0, 0, 0))
png += chunk(b"IDAT", zlib.compress(bytes(rows))) + chunk(b"IEND", b"")
pathlib.Path(sys.argv[2]).write_bytes(png)
