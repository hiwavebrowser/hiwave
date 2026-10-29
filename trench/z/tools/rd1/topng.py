"""topng.py <ppm> <png> [y0 y1 x0 x1]: crop a P6 frame and write a PNG (scaled 2x)."""
import pathlib, struct, sys, zlib

import numpy as np

data = pathlib.Path(sys.argv[1]).read_bytes()
magic, w, h, rest = data.split(maxsplit=3)
w, h = int(w), int(h)
px = rest[len(rest.split(maxsplit=1)[0]) + 1:]
img = np.frombuffer(px[:w * h * 3], dtype=np.uint8).reshape(h, w, 3)
if len(sys.argv) > 3:
    y0, y1, x0, x1 = map(int, sys.argv[3:7])
    img = img[y0:y1, x0:x1]
img = np.repeat(np.repeat(img, 2, axis=0), 2, axis=1)
H, W, _ = img.shape
raw = b''.join(b'\x00' + img[r].tobytes() for r in range(H))


def chunk(t, d):
    return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)


pathlib.Path(sys.argv[2]).write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
                                      + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))
