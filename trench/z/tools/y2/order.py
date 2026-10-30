"""When did the ad loader run against the page's chunks? (hosts and times only)"""
import json, re, sys
for path in sys.argv[1:]:
    rows = []
    for line in open(path):
        r = json.loads(line)
        if r.get('type') != 'script':
            continue
        u = str(r.get('script'))
        host = re.sub(r'^https?://([^/]+).*', r'\1', u)
        rows.append((round(r.get('t_ms', 0)), host, re.sub(r'.*/', '', u)[:34], r.get('kind'), r.get('outcome')))
    tb = [x for x in rows if 'taboola' in x[1]]
    own = [x for x in rows if 'yahoo.com' in x[1]]
    err = [round(json.loads(l)['t_ms']) for l in open(path) if 'Minified React error #418' in l]
    print(path.split('/')[-1], 'scripts', len(rows), 'own last', own[-1][0] if own else None, '418 at', err)
    print('  taboola', tb[:6])
    print('  own chunks by time', [x[0] for x in own][::6])
