"""apple_check.py <binary> <tag> : capture apple.com, % pixels off Chrome 148's banked frame (all, nav rows 0-44), strip PNG. Private frames."""
import pathlib, subprocess, sys
import numpy as np

binary, tag = sys.argv[1], sys.argv[2]
R = pathlib.Path('/Users/petecopeland/Repos/.worktrees/renders-private/ht27')
src = open(pathlib.Path(__file__).with_name('toward.py')).read()
ns = {}
exec(src[src.index('def load_ppm'):src.index('cr = load_png')], {'np': np, '__builtins__': __builtins__}, ns)
ppm = R / ('apple-%s.ppm' % tag)
r = subprocess.run([binary, '--url', 'https://www.apple.com/', '--width', '1280', '--height', '800', '--timeout-ms', '90000',
                    '--dump-frame', str(ppm)], capture_output=True, text=True)
print('exit', r.returncode)
f = ns['load_ppm'](ppm)
c = ns['load_png'](R / 'dir-apple-cr.png')
h, w = min(f.shape[0], c.shape[0]), min(f.shape[1], c.shape[1])
d = np.abs(f[:h, :w] - c[:h, :w]).max(axis=2) > 8
print('%s vs Chrome: all %.2f%%  nav rows 0-44 %.2f%%' % (tag, d.mean() * 100, d[:44].mean() * 100))
strip = np.concatenate([f[:44, :w], np.full((4, w, 3), 255, np.int16), c[:44, :w]]).astype(np.uint8)
out = R / ('apple-%s-strip.ppm' % tag)
out.write_bytes(b'P6 %d %d 255\n' % (w, strip.shape[0]) + strip.tobytes())
subprocess.run(['sips', '-s', 'format', 'png', str(out), '--out', str(out.with_suffix('.png'))], capture_output=True)
print(out.with_suffix('.png'))
