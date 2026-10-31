#!/usr/bin/env python3
"""C2(c) suites through the lease, one after another: the develop check, then the candidate's."""
import subprocess
T = '/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/tools/'
W = '/Users/petecopeland/Repos/.worktrees/'
D, C = W + 'z-dev-546d6196', W + 'z-c2c'
subprocess.run(['python3', T + 'devcheck.py', D, D + '/devcheck.log'])
subprocess.run(['python3', T + 'c2/suite.py', C])
subprocess.run(['python3', T + 'c2/crates.py', C, C + '/crates.log'])
print('GATES-DONE')
