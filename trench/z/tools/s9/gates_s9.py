#!/usr/bin/env python3
"""gates_s9.py <worktree> <base sha> <tag>: c10/gates.py without the crate and headless suites
(the batch runs those, per the 11-04 18:48 plan note). Base worktree + parity builds of both,
both campaigns, campaign diff, then the 20-site A/B on banked binaries. Ends in ALL-DONE."""
import os, shutil, subprocess, sys
W = '/Users/petecopeland/Repos/.worktrees/'
T = W + 'z-hub/trench/z/tools/'
ZC = W + 'z-cargo.py'
SEED = W + '_seed/hiwave-macos.git'
C, base, tag = sys.argv[1], sys.argv[2], sys.argv[3]
B = W + 'z-base-' + base[:8]
if not os.path.exists(B):
    subprocess.run(['git', '-C', SEED, 'worktree', 'add', '-q', '--detach', B, base], check=True)
head = subprocess.run(['git', '-C', C, 'rev-parse', '--short=8', 'HEAD'], capture_output=True, text=True).stdout.strip()
print('head', head, 'base', base[:8], flush=True)
for wt in (B, C):
    with open(wt + '/parity-build.log', 'w') as f:
        print(wt, 'parity rc', subprocess.run(['python3', ZC, wt, 'build', '--profile', 'parity', '-p', 'parity-capture'],
                                              stdout=f, stderr=subprocess.STDOUT).returncode, flush=True)
os.makedirs(C + '/scratch/bins', exist_ok=True)
A_BIN, B_BIN = C + '/scratch/bins/base', C + '/scratch/bins/cand'
shutil.copy2(B + '/target/parity/parity-capture', A_BIN)
shutil.copy2(C + '/target/parity/parity-capture', B_BIN)
for p in (A_BIN, B_BIN):
    print(p, subprocess.run(['shasum', '-a', '256', p], capture_output=True, text=True).stdout.split()[0], flush=True)
subprocess.run(['python3', T + 'camp.py', B, 'base-' + base[:8], A_BIN])
subprocess.run(['python3', T + 'camp.py', C, tag + '-' + head, B_BIN])
print('CAMPAIGNS-DONE', flush=True)
subprocess.run(['python3', T + 'campdiff.py', B + '/scratch/camp-base-' + base[:8] + '.json',
                C + '/scratch/camp-' + tag + '-' + head + '.json'])
print('AB-START', flush=True)
subprocess.run(['python3', T + 'ab5.py', C, tag, A_BIN, B_BIN])
print('AB-DONE', flush=True)
print('ALL-DONE', flush=True)
