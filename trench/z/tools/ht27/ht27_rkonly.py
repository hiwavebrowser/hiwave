"""ht27_rkonly.py <binary> <out prefix> <url> <width> [live_ms] [extra args...] : one RustKit capture (frame png + layout)."""
import subprocess, sys, time

binary, pre, url, width = sys.argv[1:5]
live = sys.argv[5] if len(sys.argv) > 5 else '8000'
extra = sys.argv[6:]
t = time.time()
src = ['--html-file', url] if url.endswith('.html') and not url.startswith('http') else ['--url', url, '--live-ms', live]
r = subprocess.run([binary] + src + ['--width', width, '--height', '800', '--timeout-ms', '90000',
                    '--dump-frame', pre + '.ppm', '--dump-layout', pre + '-layout.json'] + extra, capture_output=True, text=True)
print('exit', r.returncode, '%.1fs' % (time.time() - t), r.stdout[-300:], r.stderr[-300:])
subprocess.run(['sips', '-s', 'format', 'png', pre + '.ppm', '--out', pre + '.png'], capture_output=True)
