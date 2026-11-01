#!/usr/bin/env python3
"""ppm2png.py <in.ppm> <out.png> [scale divisor]: a frame as a PNG the Read tool can show. Local only; frames stay out of the repo."""
import struct
import sys
import zlib


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


w, h, p = ppm(sys.argv[1])
div = int(sys.argv[3]) if len(sys.argv) > 3 else 1
rows = []
for y in range(0, h, div):
    row = p[y * w * 3 : (y + 1) * w * 3]
    if div > 1:
        row = b"".join(row[x * 3 : x * 3 + 3] for x in range(0, w, div))
    rows.append(b"\0" + row)
raw = b"".join(rows)
nw, nh = len(rows[0]) // 3, len(rows)


def chunk(t, d):
    return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))


open(sys.argv[2], "wb").write(
    b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", nw, nh, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 3)) + chunk(b"IEND", b"")
)
print(nw, nh)
