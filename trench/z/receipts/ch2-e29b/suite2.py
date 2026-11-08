"""suite2.py filter <substr> <log> [threads] | full <log> | fails <log> <out> | rerun <names.txt> <log>
Engine headless test binary at the merge head f8f04b11 (develop c7209173 merged in)."""
import re, subprocess, sys, time

BIN = '/Users/petecopeland/Repos/.worktrees/z-ch2-e29b/target/debug/deps/rustkit_engine-0bcc04c2cb80b63e'
CWD = '/Users/petecopeland/Repos/.worktrees/z-ch2-e29b/crates/rustkit-engine'


def names():
    out = subprocess.run([BIN, '--list'], capture_output=True, text=True, cwd=CWD).stdout
    return [l[:-len(': test')] for l in out.split('\n') if l.endswith(': test')]


def run(cmd, log):
    with open(log, 'a') as f:
        f.write('### %s %s\n' % (time.strftime('%H:%M:%S'), ' '.join(cmd[1:4])))
        f.flush()
        subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=CWD)


def chunks(ns, log, threads=None):
    for i in range(0, len(ns), 200):
        cmd = [BIN, '--exact'] + ns[i:i + 200]
        if threads:
            cmd += ['--test-threads', threads]
        run(cmd, log)
    open(log, 'a').write('### runlist done %s\n' % time.strftime('%H:%M:%S'))


mode = sys.argv[1]
if mode == 'filter':
    cmd = [BIN, sys.argv[2]]
    if len(sys.argv) > 4:
        cmd += ['--test-threads', sys.argv[4]]
    run(cmd, sys.argv[3])
elif mode == 'full':
    ns = names()
    print('tests', len(ns))
    chunks(ns, sys.argv[2])
elif mode == 'rerun':
    ns = [n for n in open(sys.argv[2]).read().split('\n') if n]
    chunks(ns, sys.argv[3], '1')
elif mode == 'fails':
    txt = open(sys.argv[2], errors='replace').read()
    res = dict(re.findall(r'^test (\S+) \.\.\. (ok|FAILED|ignored)', txt, re.M))
    fails = sorted(n for n, r in res.items() if r == 'FAILED')
    open(sys.argv[3], 'w').write('\n'.join(fails) + ('\n' if fails else ''))
    allnames = names()
    print('binary', len(allnames), 'ran', len(res), 'ok', sum(r == 'ok' for r in res.values()),
          'ignored', sum(r == 'ignored' for r in res.values()), 'failed', len(fails),
          'not reached', len([n for n in allnames if n not in res]))
