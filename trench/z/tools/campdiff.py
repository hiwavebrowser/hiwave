"""Compare two campaign JSONs case by case (results[].pixel.diffPixels).
usage: campdiff.py a.json b.json
Prints one row per case and asserts no case is missing from either side."""
import json, sys


def load(p):
    d = json.load(open(p))
    rows = {}
    for r in d['results']:
        name = r['case_id']
        rows[name] = (r.get('pixel') or {}).get('diffPixels')
    return rows


a, b = load(sys.argv[1]), load(sys.argv[2])
assert set(a) == set(b), ('case sets differ', sorted(set(a) ^ set(b)))
moved = 0
for k in sorted(a):
    flag = '' if a[k] == b[k] else '  MOVED'
    moved += bool(flag)
    print('%-40s %10s %10s%s' % (k, a[k], b[k], flag))
print('cases %d, moved %d' % (len(a), moved))
