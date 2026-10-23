"""All-site A/B of two parity-capture binaries on the live top-20.
usage: ab5.py <worktree> <tag> <binary A> <binary B> [site ...]
Binaries must be ABSOLUTE paths. Each site is captured A, B, A, B (1280x800,
30 s limit). A pixel differs when any channel is more than 8 apart. Per site:
the difference inside each arm, the four cross pairs, failures, seconds and
script-log sizes. Appends one line per site to <worktree>/scratch/ab-<tag>.txt;
frames in <worktree>/scratch/x-<tag>/.
(Adapted from Prometheus's scratch/prom/ab5.py; kept in the hub because lane
scratch dies with its worktree.)"""
import json, pathlib, subprocess, sys, time

import numpy as np

WT, tag, A, B = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
S = WT / 'scratch'
S.mkdir(exist_ok=True)
sites = json.loads((WT / 'websuite/realsite-top20.json').read_text())['sites']
if sys.argv[5:]:
    sites = [s for s in sites if s['id'] in sys.argv[5:]]
frames = S / ('x-' + tag)
frames.mkdir(exist_ok=True)
table = S / ('ab-%s.txt' % tag)


def ppm(path):
    data = path.read_bytes()
    # P6, width, height, maxval, then ONE whitespace byte and the pixels (which
    # may themselves start with a whitespace byte: do not split past maxval).
    magic, w, h, rest = data.split(maxsplit=3)
    w, h = int(w), int(h)
    pixels = rest[len(rest.split(maxsplit=1)[0]) + 1:]
    return np.frombuffer(pixels[:w * h * 3], dtype=np.uint8).astype(np.int16).reshape(h, w, 3)


def diff(a, b):
    if a is None or b is None:
        return None
    if a.shape != b.shape:
        return 100.0
    return float((np.abs(a - b).max(axis=2) > 8).mean() * 100)


def fmt(v):
    return 'n/a' if v is None else '%.2f' % v


for site in sites:
    shots, secs, scripts, failed = [], [], [], 0
    for i, binary in enumerate([A, B, A, B]):
        frame = frames / ('%s-%d.ppm' % (site['id'], i))
        log = frames / ('%s-%d.scripts.json' % (site['id'], i))
        for p in (frame, log):
            if p.exists():
                p.unlink()
        t = time.time()
        subprocess.run([binary, '--url', site['url'], '--width', '1280', '--height', '800',
                        '--timeout-ms', '30000', '--dump-frame', str(frame), '--dump-scripts', str(log)],
                       capture_output=True, text=True)
        secs.append('%.1f' % (time.time() - t))
        if frame.exists():
            shots.append(ppm(frame))
        else:
            shots.append(None)
            failed += 1
        try:
            records = json.loads(log.read_text())
            records = records.get('scripts', records) if isinstance(records, dict) else records
            scripts.append(str(len(records)))
        except (OSError, ValueError):
            scripts.append('-')
    line = '%-12s within A %s%%  within B %s%%  across %s  failed: %d  secs A,B,A,B %s  script records A,B,A,B %s' % (
        site['id'], fmt(diff(shots[0], shots[2])), fmt(diff(shots[1], shots[3])),
        ' '.join(fmt(diff(shots[a], shots[b])) + '%' for a, b in [(0, 1), (0, 3), (2, 1), (2, 3)]),
        failed, ','.join(secs), ','.join(scripts))
    print(line, flush=True)
    with open(table, 'a') as f:
        f.write(line + '\n')
