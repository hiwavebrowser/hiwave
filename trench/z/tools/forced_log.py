"""Run one live capture with RUST_LOG=rustkit_engine=debug and summarise forced layouts.
usage: forced_log.py <binary> <site id> <out log>
Prints: wall secs, number of "Forced layout" lines with total/median ms, the
"Forced layouts in the script task" counts, and relayout lines (ms)."""
import json, os, pathlib, re, statistics, subprocess, sys, time

binary, site_id, out = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
wt = pathlib.Path(binary).parents[2]
url = next(s['url'] for s in json.loads((wt / 'websuite/realsite-top20.json').read_text())['sites'] if s['id'] == site_id)
env = dict(os.environ, RUST_LOG='rustkit_engine=debug', NO_COLOR='1')
t = time.time()
r = subprocess.run([binary, '--url', url, '--width', '1280', '--height', '800', '--timeout-ms', '60000'],
                   capture_output=True, text=True, timeout=240, env=env)
secs = time.time() - t
text = re.sub(r'\x1b\[[0-9;]*m', '', r.stdout + r.stderr)
out.write_text(text)
forced = [float(m.group(1)) for m in re.finditer(r'Forced layout\b(?! skipped)(?!s in).*?ms=([0-9.]+)', text)]
forced += [float(m.group(1)) for m in re.finditer(r'ms=([0-9.]+).*?Forced layout\b(?! skipped)(?!s in)', text)]
tasks = re.findall(r'.*Forced layouts in the script task.*', text)
skipped = len(re.findall(r'Forced layout skipped', text))
print('secs %.2f exit %d log lines %d' % (secs, r.returncode, len(text.splitlines())))
if forced:
    print('forced layouts %d total %.0f ms median %.1f max %.1f' % (len(forced), sum(forced), statistics.median(forced), max(forced)))
else:
    print('forced layouts 0')
print('skipped', skipped)
for line in tasks[:20]:
    print(line[-200:])
