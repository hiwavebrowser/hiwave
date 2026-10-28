"""ht27_cap.py <out dir> <binary> <name> <url> [live_ms]
parity-capture frame (+ layout dump) and a pinned Chrome 148 frame of one URL, 1280x800.
Frames are private: keep <out dir> outside any public repo."""
import json, os, pathlib, subprocess, sys, time

out, binary, name, url = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
live = sys.argv[5] if len(sys.argv) > 5 else '8000'
out.mkdir(parents=True, exist_ok=True)
WT = pathlib.Path(__file__).resolve().parent.parent
CHROME = '/Users/petecopeland/Repos/.worktrees/reduce-scratch/cft/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'

t = time.time()
r = subprocess.run([binary, '--url', url, '--width', '1280', '--height', '800', '--live-ms', live,
                    '--timeout-ms', '90000', '--dump-frame', str(out / (name + '-rk.ppm')),
                    '--dump-layout', str(out / (name + '-rk-layout.json'))],
                   capture_output=True, text=True)
print('rk', name, 'exit', r.returncode, '%.1fs' % (time.time() - t), r.stderr[-400:] if r.returncode else '')
ppm = out / (name + '-rk.ppm')
if ppm.exists():
    subprocess.run(['sips', '-s', 'format', 'png', str(ppm), '--out', str(out / (name + '-rk.png'))], capture_output=True)

js = WT / 'tools/parity_oracle' / 'ht27_chrome.mjs'
if os.environ.get('HT27_SKIP_RK'):
    pass
env = dict(os.environ, PARITY_CHROME_PATH=CHROME)
t = time.time()
r = subprocess.run(['node', str(js), url, str(out / (name + '-cr.png')), str(out / (name + '-cr-rects.json'))],
                   capture_output=True, text=True, env=env, cwd=str(WT / 'tools/parity_oracle'), timeout=180)
print('cr', name, 'exit', r.returncode, '%.1fs' % (time.time() - t), (r.stdout + r.stderr)[-600:])
