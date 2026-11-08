"""A/B the two page_script timing tests: develop c7209173 vs candidate f8f04b11, one thread, 2 rounds."""
import os
import re
import subprocess

T = ['page_script_tests::a_stalled_subresource_is_dropped_at_the_subresource_budget',
     'page_script_tests::scripts_are_fetched_while_the_subresources_load']
ARMS = [('develop', '/Users/petecopeland/Repos/.worktrees/z-base-c7209173'),
        ('cand', '/Users/petecopeland/Repos/.worktrees/z-ch2-e29b')]
BIN = '/target/debug/deps/rustkit_engine-0bcc04c2cb80b63e'
with open('/Users/petecopeland/Repos/.worktrees/scratch-e29b/timing-ab.log', 'w') as log:
    for rnd in range(2):
        for arm, w in ARMS:
            r = subprocess.run([w + BIN, '--exact'] + T + ['--test-threads', '1'],
                               capture_output=True, text=True, cwd=w + '/crates/rustkit-engine')
            o = r.stdout + r.stderr
            load = os.getloadavg()[0]
            log.write('### %s round %d load %.1f\n%s' % (arm, rnd, load, o))
            res = [x[1] for x in re.findall(r'^test (\S+) \.\.\. (\w+)', o, re.M)]
            print(arm, rnd, 'load %.1f' % load, res, re.findall(r'waited[^\n]*: ([\d.]+s)', o))
