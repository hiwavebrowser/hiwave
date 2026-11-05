import json, sys


def load(p):
    d = json.load(open(p))
    rows = d['rows'] if isinstance(d, dict) and 'rows' in d else d
    out = {}
    for r in rows:
        key = tuple(str(r.get(k)) for k in ('page', 'state', 'size'))
        out[key] = (r.get('pixel_diff_pct'), r.get('geometry_diffs', r.get('geo')))
    return out, rows


a, ra = load(sys.argv[1])
b, rb = load(sys.argv[2])
diff = [(k, a[k], b.get(k)) for k in a if a[k] != b.get(k)]
print(len(a), len(b), 'differ', len(diff))
for x in diff[:15]:
    print(x)
if ra:
    print('keys', sorted(ra[0].keys()))
