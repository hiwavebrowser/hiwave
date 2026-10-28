"""Which script DOM writes dirtied the page before each forced layout.
usage: dirty_census.py <binary> <url> <out log> [timeout_ms]
Runs one live capture with RUST_LOG=rustkit_engine=debug,rustkit_bindings=trace
and groups the "DOM write dirtied the page" lines (rustkit-bindings
trace_dirty) between consecutive "Forced layout" lines. Prints, per forced
layout, the writes that preceded it as op:tag:detail counts, then a summary of
which write shapes precede how many forced layouts. Form value writes do not
go through trace_dirty and are not counted."""
import collections, os, pathlib, re, subprocess, sys, time

binary, url, out = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
timeout_ms = sys.argv[4] if len(sys.argv) > 4 else '60000'
if binary == '--reread':
    secs, r, text = 0.0, subprocess.CompletedProcess([], 0), out.read_text()
else:
    env = dict(os.environ, RUST_LOG='rustkit_engine=debug,rustkit_bindings=trace', NO_COLOR='1')
    t = time.time()
    r = subprocess.run([binary, '--url', url, '--width', '1280', '--height', '800', '--timeout-ms', timeout_ms],
                       capture_output=True, text=True, timeout=400, env=env)
    secs = time.time() - t
    text = re.sub(r'\x1b\[[0-9;]*m', '', r.stdout + r.stderr)
    out.write_text(text)

write_re = re.compile(r'DOM write dirtied the page op="?([^" ]*)"? tag=(\S*) connected=(\S+) detail=(.*?) bucket=(\S+)')
pending = collections.Counter()
forced = []
for line in text.splitlines():
    m = write_re.search(line)
    if m:
        op, tag, connected, detail, bucket = m.groups()
        # setAttr/removeAttr detail is the attribute name; other ops' detail is page text: keep its shape only.
        shape = detail if op in ('setAttr', 'removeAttr') else ''
        pending['%s:%s:%s%s' % (op, tag, shape, '' if connected == 'true' else ':detached')] += 1
    elif re.search(r'Forced layout\b(?! skipped)(?!s in)', line):
        ms = re.search(r'ms=([0-9.]+)', line)
        forced.append((float(ms.group(1)) if ms else 0.0, pending))
        pending = collections.Counter()
    elif 'Forced layouts in the script task' in line:
        pending = collections.Counter()

print('secs %.1f exit %d forced %d' % (secs, r.returncode, len(forced)))
for i, (ms, writes) in enumerate(forced):
    print('%3d %6.1f ms  %s' % (i, ms, ', '.join('%s x%d' % kv for kv in writes.most_common(6))))
precede = collections.Counter()
for _, writes in forced:
    for k in writes:
        precede[k] += 1
print('write shape -> forced layouts it preceded')
for k, v in precede.most_common(25):
    print('  %3d  %s' % (v, k))
