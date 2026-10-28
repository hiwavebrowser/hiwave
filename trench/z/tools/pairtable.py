"""Markdown table + medians for pairtime.py JSONL files.
usage: pairtable.py <base arm> <file.jsonl> [...]"""
import json, statistics, sys

base = sys.argv[1]
for path in sys.argv[2:]:
    rows = [json.loads(l) for l in open(path) if l.strip()]
    site = rows[0]['site']
    arms = list(dict.fromkeys(r['arm'] for r in rows))
    print('### %s\n' % site)
    print('| round | ' + ' | '.join('%s s (load1)' % a for a in arms) + ' |')
    print('|---|' + '---|' * len(arms))
    for rnd in sorted(set(r['round'] for r in rows)):
        cells = []
        for a in arms:
            r = next(x for x in rows if x['round'] == rnd and x['arm'] == a)
            flag = ' KILLED' if r['killed'] else ('' if r['frame'] else ' no frame')
            cells.append('%.2f (%.1f)%s' % (r['secs'], r['load1'], flag))
        print('| %d | %s |' % (rnd, ' | '.join(cells)))
    med = {a: statistics.median(r['secs'] for r in rows if r['arm'] == a) for a in arms}
    print('\nmedians: ' + ', '.join('%s %.2f s' % (a, m) for a, m in med.items()))
    print('ratios vs %s: ' % base + ', '.join('%s %.3f' % (a, m / med[base]) for a, m in med.items() if a != base))
    print('load1 range %.1f-%.1f, killed %d, no frame %d\n' % (
        min(r['load1'] for r in rows), max(r['load1'] for r in rows),
        sum(r['killed'] for r in rows), sum(not r['frame'] for r in rows)))
