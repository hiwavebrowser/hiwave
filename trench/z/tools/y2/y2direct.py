"""Direct engine load with the React probe (local diag build, Y2_PROBE env).
usage: y2direct.py <binary> <live_ms> [tag]"""
import json, os, pathlib, re, subprocess, sys

S = pathlib.Path(__file__).parent
tag = sys.argv[3] if len(sys.argv) > 3 else 'd'
log = S / ('y2-%s.jsonl' % tag)
log.unlink(missing_ok=True)
env = dict(os.environ, Y2_PROBE=str(S / 'probe.js'))
r = subprocess.run([sys.argv[1], '--url', 'https://www.yahoo.com/', '--live-ms', sys.argv[2], '--timeout-ms', '120000',
                    '--event-log', str(log), '--event-log-error-text', '--event-log-console-text',
                    '--width', '1280', '--height', '800', '--dump-frame', str(S / ('y2-%s.ppm' % tag))],
                   capture_output=True, text=True, timeout=170, env=env)
parts = []
n418 = 0
for line in log.read_text().splitlines():
    if 'Minified React error #418' in line:
        n418 += 1
    if 'Y2' not in line:
        continue
    for m in re.finditer(r'Y2:((?:[^"\\]|\\.)*)', line):
        parts.append(json.loads('"' + m[1] + '"'))
    if 'Y2FAIL' in line:
        print('probe failed', line[:300])
print('rc', r.returncode, '418 records', n418, 'chunks', len(parts))
text = ''.join(parts)
print(text[:5000])
