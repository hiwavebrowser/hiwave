"""toward.py <ab frames dir> <site> <url> : Chrome 148 frame of url, then % differing pixels (any channel > 8) of
arm A frame 0 and arm B frame 1 against it. Lower = nearer Chrome. Frames private (renders-private/ht27)."""
import os, pathlib, subprocess, sys
import numpy as np

frames, site, url = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
WT = pathlib.Path(__file__).resolve().parent.parent
out = pathlib.Path('/Users/petecopeland/Repos/.worktrees/renders-private/ht27')
CHROME = '/Users/petecopeland/Repos/.worktrees/reduce-scratch/cft/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'
png = out / ('dir-%s-cr.png' % site)
subprocess.run(['node', str(WT / 'tools/parity_oracle/ht27_chrome.mjs'), url, str(png), str(out / ('dir-%s-rects.json' % site))],
               capture_output=True, text=True, env=dict(os.environ, PARITY_CHROME_PATH=CHROME), cwd=str(WT / 'tools/parity_oracle'), timeout=180)
ppm = out / ('dir-%s-cr.ppm' % site)
subprocess.run(['sips', '-s', 'format', 'pbm', str(png), '--out', str(ppm)], capture_output=True)


def load_ppm(p):
    data = p.read_bytes()
    magic, w, h, rest = data.split(maxsplit=3)
    w, h = int(w), int(h)
    px = rest[len(rest.split(maxsplit=1)[0]) + 1:]
    return np.frombuffer(px[:w * h * 3], dtype=np.uint8).astype(np.int16).reshape(h, w, 3)


def load_png(p):
    # sips -> tiff is awkward; use sips to produce a ppm via 'pbm' is not RGB. Decode PNG with zlib instead.
    import struct, zlib
    b = p.read_bytes()
    pos, idat, w, h, ct = 8, b'', 0, 0, 0
    while pos < len(b):
        n = struct.unpack('>I', b[pos:pos + 4])[0]; t = b[pos + 4:pos + 8]; d = b[pos + 8:pos + 8 + n]
        if t == b'IHDR': w, h, bd, ct = struct.unpack('>IIBB', d[:10])
        elif t == b'IDAT': idat += d
        pos += 12 + n
    ch = 4 if ct == 6 else 3
    raw = zlib.decompress(idat); stride = w * ch
    img = np.zeros((h, stride), dtype=np.int16); prev = np.zeros(stride, dtype=np.int16); i = 0
    for y in range(h):
        f = raw[i]; line = np.frombuffer(raw[i + 1:i + 1 + stride], dtype=np.uint8).astype(np.int16); i += 1 + stride
        if f == 0: cur = line
        elif f == 2: cur = (line + prev) & 255
        else:
            cur = np.zeros(stride, dtype=np.int16)
            for x in range(stride):
                a = cur[x - ch] if x >= ch else 0; c = prev[x - ch] if x >= ch else 0; up = prev[x]
                if f == 1: pr = a
                elif f == 3: pr = (a + up) // 2
                else:
                    pa, pb, pc = abs(up - c), abs(a - c), abs(a + up - 2 * c)
                    pr = a if pa <= pb and pa <= pc else (up if pb <= pc else c)
                cur[x] = (line[x] + pr) & 255
        img[y] = cur; prev = cur
    return img.reshape(h, w, ch)[:, :, :3]


cr = load_png(png)
for arm, idx in (('A develop', 0), ('B #786', 1)):
    f = load_ppm(frames / ('%s-%d.ppm' % (site, idx)))
    hh, ww = min(f.shape[0], cr.shape[0]), min(f.shape[1], cr.shape[1])
    d = (np.abs(f[:hh, :ww] - cr[:hh, :ww]).max(axis=2) > 8).mean() * 100
    print(site, arm, 'vs Chrome %.2f%%' % d)
