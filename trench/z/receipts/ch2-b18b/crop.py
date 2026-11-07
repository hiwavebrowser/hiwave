"""crop.py a.ppm b.ppm x0 y0 x1 y1 out.png scale: base over candidate, scaled, as one PNG."""
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
    return int(fields[1]), int(fields[2]), data[i + 1:]


a, b = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7])
out, s = sys.argv[7], int(sys.argv[8])
rows = []
for path in (a, b):
    w, h, px = ppm(path)
    for y in range(y0, y1):
        row = bytearray()
        for x in range(x0, x1):
            o = (y * w + x) * 3
            row += px[o:o + 3] * s
        for _ in range(s):
            rows.append(bytes(row))
    sep = bytes([255, 0, 0]) * ((x1 - x0) * s)
    rows.append(sep)
    rows.append(sep)
W = (x1 - x0) * s
raw = b"".join(b"\x00" + r for r in rows)


def chunk(t, d):
    c = struct.pack(">I", len(d)) + t + d
    return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)


png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, len(rows), 8, 2, 0, 0, 0))
png += chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
open(out, "wb").write(png)
print(out, W, len(rows))
