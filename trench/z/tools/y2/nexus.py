import json
S = '/Users/petecopeland/Repos/.worktrees/z-y2/scratch/tall-direct.jsonl'
ids = {}
print('keys sample')
for line in open(S):
    x = json.loads(line)
    if x.get('type') == 'request' and 'nexus-gateway' in str(x.get('url')):
        ids[x['id']] = round(x['t_ms'])
    if x.get('type') == 'response' and x.get('id') in ids:
        print('req at', ids[x['id']], 'resp at', round(x['t_ms']), {k: x[k] for k in x if k in ('status', 'bytes', 'size', 'encoded_bytes', 'body_bytes', 'outcome', 'failure', 'mime')})
    if x.get('type') == 'failure' and x.get('id') in ids:
        print('FAIL', ids[x['id']], str(x)[:200])
done = [json.loads(l) for l in open(S)]
print('last relayout', max(round(x['t_ms']) for x in done if x.get('type') == 'relayout'), 'end', max(round(x.get('t_ms', 0)) for x in done))
print('console errors', [(round(x['t_ms']), len(str(x.get('message')))) for x in done if x.get('type') == 'console' and x.get('level') == 'error'])
