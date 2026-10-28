"""Capture one site with --event-log and summarise forced-layout / relayout records.
usage: evlog_forced.py <binary> <site id> <out dir>"""
import collections, json, pathlib, subprocess, sys, time

binary, site_id, out = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
wt = pathlib.Path(binary).parents[2]
url = next(s['url'] for s in json.loads((wt / 'websuite/realsite-top20.json').read_text())['sites'] if s['id'] == site_id)
log = out / ('%s-events.jsonl' % site_id)
t = time.time()
r = subprocess.run([binary, '--url', url, '--width', '1280', '--height', '800', '--timeout-ms', '60000',
                    '--event-log', str(log)], capture_output=True, text=True, timeout=240)
print('secs %.2f exit %d' % (time.time() - t, r.returncode))
kinds = collections.Counter()
hits = []
for line in log.read_text().splitlines():
    try:
        rec = json.loads(line)
    except ValueError:
        continue
    k = rec.get('kind') or rec.get('type') or '?'
    kinds[k] += 1
    s = json.dumps(rec)
    if 'forced' in s.lower() or 'relayout' in s.lower() or 'layout' in k.lower():
        hits.append(s[:300])
print(kinds.most_common(25))
print(len(hits), 'layout-ish records')
for h in hits[:40]:
    print(h)
