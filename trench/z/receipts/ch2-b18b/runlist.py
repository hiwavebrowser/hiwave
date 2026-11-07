"""runlist.py list|run|fails ...  (copy of receipts/ch2-e20/runlist.py, paths for z-ch2-b18b)
  list                      -> write all.txt (test names from the built binary)
  run <names.txt> <log> [threads] -> run names by exact name in 200-test chunks, append to log
  fails <log> <out.txt>     -> write FAILED test names from log
"""
import re, subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = '/Users/petecopeland/Repos/.worktrees/z-ch2-b18b/target/debug/deps/rustkit_engine-0bcc04c2cb80b63e'
CWD = '/Users/petecopeland/Repos/.worktrees/z-ch2-b18b/crates/rustkit-engine'

mode = sys.argv[1]
if mode == 'list':
    out = subprocess.run([BIN, '--list'], cwd=CWD, capture_output=True, text=True).stdout
    names = [l[:-len(': test')] for l in out.split('\n') if l.endswith(': test')]
    open(os.path.join(HERE, 'all.txt'), 'w').write('\n'.join(names) + '\n')
    print(len(names))
elif mode == 'run':
    names_file, log = sys.argv[2], sys.argv[3]
    threads = sys.argv[4] if len(sys.argv) > 4 else None
    names = [n for n in open(names_file).read().split('\n') if n]
    with open(log, 'a') as f:
        for i in range(0, len(names), 200):
            cmd = [BIN, '--exact'] + names[i:i + 200]
            if threads:
                cmd += ['--test-threads', threads]
            f.write('### chunk %d (%d tests)\n' % (i // 200, len(names[i:i + 200])))
            f.flush()
            subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=CWD)
        f.write('### runlist done\n')
elif mode == 'fails':
    log, out = sys.argv[2], sys.argv[3]
    txt = open(log, errors='replace').read()
    fails = sorted(set(re.findall(r'^test (\S+) \.\.\. FAILED', txt, re.M)))
    oks = len(re.findall(r'^test \S+ \.\.\. ok', txt, re.M))
    ign = len(re.findall(r'^test \S+ \.\.\. ignored', txt, re.M))
    open(out, 'w').write('\n'.join(fails) + ('\n' if fails else ''))
    print('ok', oks, 'failed', len(fails), 'ignored', ign,
          'results', re.findall(r'^test result: .*', txt, re.M))
