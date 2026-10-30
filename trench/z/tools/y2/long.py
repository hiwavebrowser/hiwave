import json, subprocess, time
S = '/Users/petecopeland/Repos/.worktrees/z-y2/scratch/'
B = '/Users/petecopeland/Repos/.worktrees/z-rd3/scratch/parity-dev-702154ef'
r = subprocess.run([B, '--url', 'https://www.yahoo.com/', '--live-ms', '70000', '--timeout-ms', '110000', '--width', '1280', '--height', '2400',
                    '--dump-frame', S + 'tall-70.ppm', '--event-log', S + 'tall-70.jsonl', '--event-log-error-text'], capture_output=True, text=True, timeout=150)
print('rc', r.returncode, time.ctime())
rows = [json.loads(l) for l in open(S + 'tall-70.jsonl')]
print('end', max(round(x.get('t_ms', 0)) for x in rows), 'last relayout', max(round(x['t_ms']) for x in rows if x.get('type') == 'relayout'),
      '418', sum('Minified React error #418' in str(x.get('message')) for x in rows))
gw = [x for x in rows if x.get('type') == 'request' and 'nexus-gateway' in str(x.get('url'))]
print('gateway at', [round(x['t_ms']) for x in gw])
if gw:
    print('first gateway record', {k: str(v)[:160] for k, v in gw[0].items() if k != 'url'})
    t = gw[0]['t_ms']
    before = [x for x in rows if t - 3000 < x.get('t_ms', 0) <= t + 50 and x.get('type') in ('script', 'console', 'relayout', 'response')]
    for x in before[-14:]:
        print(' ', round(x['t_ms']), x['type'], str(x.get('script') or x.get('url') or x.get('reason') or x.get('cause') or '')[:70], x.get('ran_ms', ''), x.get('waited_ms', ''))
scr = [x for x in rows if x.get('type') == 'script' and x.get('ran_ms')]
big = sorted(scr, key=lambda x: -(x.get('ran_ms') or 0))[:8]
print('longest scripts', [(round(x['t_ms']), round(x['ran_ms']), str(x['script']).split('/')[-1][:24]) for x in big])
print('total script ms', round(sum(x.get('ran_ms') or 0 for x in scr)))
