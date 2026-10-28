"""strip.py <site> <rows> : develop / #786 / Chrome top strips stacked into renders-private/ht27/<site>-strip.png."""
import pathlib, subprocess, sys
import numpy as np

site, rows = sys.argv[1], int(sys.argv[2])
src = open(pathlib.Path(__file__).with_name('toward.py')).read()
ns = {}
exec(src[src.index('def load_ppm'):src.index('cr = load_png')], {'np': np, '__builtins__': __builtins__}, ns)
X = pathlib.Path('/Users/petecopeland/Repos/.worktrees/z-786-gate/scratch/x-c786')
R = pathlib.Path('/Users/petecopeland/Repos/.worktrees/renders-private/ht27')
a = ns['load_ppm'](X / ('%s-0.ppm' % site))[:rows]
b = ns['load_ppm'](X / ('%s-1.ppm' % site))[:rows]
c = ns['load_png'](R / ('dir-%s-cr.png' % site))[:rows]
sep = np.full((4, 1280, 3), 255, np.int16)
img = np.concatenate([a, sep, b, sep, c]).astype(np.uint8)
h, w, _ = img.shape
ppm = R / ('%s-strip.ppm' % site)
ppm.write_bytes(b'P6 %d %d 255\n' % (w, h) + img.tobytes())
subprocess.run(['sips', '-s', 'format', 'png', str(ppm), '--out', str(R / ('%s-strip.png' % site))], capture_output=True)
print(R / ('%s-strip.png' % site))
