"""ht27_rk.py <layout.json> [tag ...] [--y MAX] : flat list of engine boxes (tag, id, class, rect)."""
import json, sys

d = json.load(open(sys.argv[1]))
args = sys.argv[2:]
ymax = 800
if '--y' in args:
    i = args.index('--y'); ymax = float(args[i + 1]); args = args[:i] + args[i + 2:]
tags = set(args)
first = [True]


def walk(n, depth):
    if first[0]:
        print('keys:', sorted(k for k in n if k != 'children'))
        first[0] = False
    tag = (n.get('tag') or n.get('element') or n.get('node_name') or '').lower()
    r = n.get('rect') or n.get('border_box') or n.get('content_rect') or {}
    y = r.get('y', 0) if isinstance(r, dict) else 0
    if (not tags or tag in tags) and y < ymax:
        attrs = n.get('attributes') or {}
        print('  ' * min(depth, 30) + '%s#%s.%s %s %s' % (tag, n.get('id', attrs.get('id', '')),
              str(n.get('class', attrs.get('class', '')))[:50], n.get('box_type', n.get('display', '')),
              {k: round(v) for k, v in r.items()} if isinstance(r, dict) else r))
    for c in n.get('children', []):
        walk(c, depth + 1)


walk(d['root'], 0)
