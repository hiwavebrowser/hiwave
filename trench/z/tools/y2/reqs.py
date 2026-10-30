import json, re, subprocess, collections
S = '/Users/petecopeland/Repos/.worktrees/z-y2/'
r = subprocess.run(['node', 'tools/parity_oracle/y2_requests.mjs', 'https://www.yahoo.com/', '30'], cwd=S, capture_output=True, text=True, timeout=120)
chrome = [l.split(' ', 3) for l in r.stdout.strip().split('\n') if l]
print('chrome fetch/xhr', len(chrome))
keep = lambda h: 'yahoo' in h or 'yimg' in h
ck = collections.Counter(c[3] for c in chrome if keep(c[3]))
e = collections.Counter()
types = collections.Counter()
for line in open(S + 'scratch/tall-direct.jsonl'):
    x = json.loads(line)
    if x.get('type') == 'request':
        types[x.get('resource_type')] += 1
        if x.get('resource_type') in ('fetch', 'xhr', 'xmlhttprequest', 'other'):
            u = re.sub(r'^https?://', '', x['url']).split('?')[0][:90]
            if keep(u):
                e[u] += 1
print('engine types', dict(types))
print('--- chrome yahoo fetch/xhr, engine count beside')
for k, v in ck.most_common(40):
    print(v, e.get(k, 0), k)
print('--- engine only')
for k, v in e.items():
    if k not in ck:
        print(v, k)
print('--- first chrome rows')
for c in chrome[:12]:
    print(' '.join(c))
