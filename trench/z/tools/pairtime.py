"""Interleaved paired wall-clock timing of parity-capture binaries on one live site.
usage: pairtime.py <out.jsonl> <site id> <rounds> <label=ABS_BINARY> [label=ABS_BINARY ...]
Each round runs every binary once, in the order given, back to back
(develop, candidate, develop, candidate, ...). Before each run it records the
1-minute load. Each run: --url <site> 1280x800, --timeout-ms 60000, hard
kill at 240 s (a hang reads as secs=240, killed=true). Appends one JSON line
per run to <out.jsonl> and prints it. Site URLs come from the worktree's
websuite/realsite-top20.json next to the first binary."""
import json, os, pathlib, subprocess, sys, time

out, site_id, rounds = pathlib.Path(sys.argv[1]), sys.argv[2], int(sys.argv[3])
arms = [a.split('=', 1) for a in sys.argv[4:]]
wt = pathlib.Path(arms[0][1]).parents[2]
sites = json.loads((wt / 'websuite/realsite-top20.json').read_text())['sites']
url = next(s['url'] for s in sites if s['id'] == site_id)
frames = out.parent / ('frames-' + out.stem)
frames.mkdir(parents=True, exist_ok=True)

for r in range(rounds):
    for label, binary in arms:
        frame = frames / ('%s-%s-%d.ppm' % (site_id, label, r))
        if frame.exists():
            frame.unlink()
        load = os.getloadavg()[0]
        t = time.time()
        killed = False
        try:
            subprocess.run([binary, '--url', url, '--width', '1280', '--height', '800',
                            '--timeout-ms', '60000', '--dump-frame', str(frame)],
                           capture_output=True, text=True, timeout=240)
        except subprocess.TimeoutExpired:
            killed = True
        rec = {'site': site_id, 'round': r, 'arm': label, 'load1': round(load, 2),
               'secs': round(time.time() - t, 2), 'frame': frame.exists(), 'killed': killed,
               'at': time.strftime('%H:%M:%S')}
        print(json.dumps(rec), flush=True)
        with open(out, 'a') as f:
            f.write(json.dumps(rec) + '\n')
