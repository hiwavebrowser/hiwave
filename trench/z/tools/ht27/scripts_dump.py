"""scripts_dump.py <binary> <url> <out json> : parity-capture --dump-scripts (live-ms 8000); print each record's outcome and any error (no page text)."""
import json, subprocess, sys

binary, url, out = sys.argv[1:4]
r = subprocess.run([binary, '--url', url, '--live-ms', '8000', '--timeout-ms', '90000', '--dump-scripts', out,
                    '--dump-frame', out + '.ppm'], capture_output=True, text=True)
print('exit', r.returncode)
d = json.load(open(out))
recs = d if isinstance(d, list) else d.get('scripts') or d.get('records') or d
if isinstance(recs, dict):
    print('keys', list(recs)[:20])
    recs = next((v for v in recs.values() if isinstance(v, list)), [])
for x in recs:
    s = {k: (v if not isinstance(v, str) else v[:160]) for k, v in x.items() if k not in ('source', 'text', 'body')}
    print(json.dumps(s)[:400])
