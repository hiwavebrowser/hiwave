import subprocess, sys
from PIL import Image
P = '/Users/petecopeland/Repos/.worktrees/z-ch2-b18c/scratch/probe/'
B = '/Users/petecopeland/Repos/.worktrees/z-ch2-b18c/scratch/bins/'
name = sys.argv[1] if len(sys.argv) > 1 else 'bw'
html = P + name + '.html'
for arm in ('base', 'cand2'):
    r = subprocess.run([B + arm, '--html-file', html, '--width', '400', '--height', '600',
                        '--dump-frame', P + name + '-' + arm + '.ppm'], capture_output=True, text=True, timeout=120)
    print(arm, r.returncode, r.stderr[-300:] if r.returncode else '')
r = subprocess.run(['node', P + 'chrome.mjs', html, P + name + '-chrome.png'], capture_output=True, text=True,
                   cwd='/Users/petecopeland/Repos/.worktrees/z-ch2-b18c/tools/parity_oracle', timeout=120)
print('chrome', r.returncode, r.stdout[-200:], r.stderr[-500:])
ims = [Image.open(P + name + '-base.ppm').convert('RGB'), Image.open(P + name + '-cand2.ppm').convert('RGB'),
       Image.open(P + name + '-chrome.png').convert('RGB')]
w, h = 280, 600
out = Image.new('RGB', (w * 3 + 12, h), 'magenta')
for k, im in enumerate(ims):
    out.paste(im.crop((0, 0, w, h)), (k * (w + 6), 0))
out = out.resize((out.width * 2, out.height * 2), Image.NEAREST)
out.save(P + name + '-cmp.png')
for im, f in zip(ims, ('base', 'cand2', 'chrome')):
    c = im.getcolors(10 ** 7)
    print(f, 'red px', sum(n for n, rgb in c if rgb[0] > 200 and rgb[1] < 60 and rgb[2] < 60))
print('saved base | cand | chrome')
