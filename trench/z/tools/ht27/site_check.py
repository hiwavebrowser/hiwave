"""site_check.py <url> <chrome png> <out prefix> <y0> <y1> <binary>... : capture each binary (live-ms 8000, as the HT27 triage),
% pixels off the banked Chrome frame (whole frame and rows y0..y1), and one strip PNG of rows y0..y1 (binaries, then Chrome).
Frames are private: out prefix must be under renders-private."""
import pathlib, subprocess, sys
import numpy as np

url, crpng, prefix, y0, y1, bins = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6:]
src = open(pathlib.Path(__file__).with_name('toward.py')).read()
ns = {}
exec(src[src.index('def load_ppm'):src.index('cr = load_png')], {'np': np, '__builtins__': __builtins__}, ns)
c = ns['load_png'](pathlib.Path(crpng))
rows = []
for i, b in enumerate(bins):
    ppm = pathlib.Path('%s-%d.ppm' % (prefix, i))
    r = subprocess.run([b, '--url', url, '--width', '1280', '--height', '800', '--live-ms', '8000', '--timeout-ms', '90000',
                        '--dump-frame', str(ppm)], capture_output=True, text=True)
    f = ns['load_ppm'](ppm)
    h, w = min(f.shape[0], c.shape[0]), min(f.shape[1], c.shape[1])
    d = np.abs(f[:h, :w] - c[:h, :w]).max(axis=2) > 8
    print(pathlib.Path(b).name, 'exit', r.returncode, 'vs Chrome: all %.2f%%  rows %d-%d %.2f%%' % (d.mean() * 100, y0, y1, d[y0:y1].mean() * 100))
    rows += [f[y0:y1, :1280], np.full((4, 1280, 3), 255, np.int16)]
rows.append(c[y0:y1, :1280])
strip = np.concatenate(rows).astype(np.uint8)
out = pathlib.Path(prefix + '-strip.ppm')
out.write_bytes(b'P6 %d %d 255\n' % (1280, strip.shape[0]) + strip.tobytes())
subprocess.run(['sips', '-s', 'format', 'png', str(out), '--out', str(out.with_suffix('.png'))], capture_output=True)
print(out.with_suffix('.png'))
