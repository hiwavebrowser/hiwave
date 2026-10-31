#!/usr/bin/env python3
"""gh_bar.py <frame.ppm|png>...: first y of the saturated blue bar at x=100 and the rightmost dark pixel in the header band."""
import sys
import numpy as np
from PIL import Image


def load(path):
    if path.endswith(".png"):
        return np.array(Image.open(path).convert("RGB")).astype(int)
    data = open(path, "rb").read()
    magic, w, h, rest = data.split(maxsplit=3)
    w, h = int(w), int(h)
    px = rest[len(rest.split(maxsplit=1)[0]) + 1:]
    return np.frombuffer(px[: w * h * 3], dtype=np.uint8).reshape(h, w, 3).astype(int)


for p in sys.argv[1:]:
    a = load(p)
    col = a[:, 100]
    blue = np.where((col[:, 2] > 200) & (col[:, 0] < 60))[0]
    print(p.split("/")[-1], "blue bar y", (int(blue[0]), int(blue[-1])) if len(blue) else None)
