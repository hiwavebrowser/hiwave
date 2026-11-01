#!/usr/bin/env python3
"""gates2.py: C10(b2) against the banked C10(b) candidate: campaign, A/B, crates, suite. Ends ALL-DONE."""
import os, shutil, subprocess
W = '/Users/petecopeland/Repos/.worktrees/'
T = W + 'z-hub/trench/z/tools/'
C = W + 'z-c10b2'
head = subprocess.run(['git', '-C', C, 'rev-parse', '--short=8', 'HEAD'], capture_output=True, text=True).stdout.strip()
print('head', head, flush=True)
os.makedirs(C + '/scratch/bins', exist_ok=True)
A_BIN, B_BIN = C + '/scratch/bins/base', C + '/scratch/bins/cand'
shutil.copy2(W + 'z-c10b/scratch/bins/cand', A_BIN)
shutil.copy2(C + '/target/parity/parity-capture', B_BIN)
subprocess.run(['python3', T + 'camp.py', C, 'c10b2-' + head, B_BIN])
print('CAMPAIGNS-DONE', flush=True)
subprocess.run(['python3', T + 'campdiff.py', W + 'z-c10b/scratch/camp-c10b-9551f252.json', C + '/scratch/camp-c10b2-' + head + '.json'])
print('AB-START', flush=True)
subprocess.run(['python3', T + 'ab5.py', C, 'c10b2', A_BIN, B_BIN])
print('AB-DONE', flush=True)
subprocess.run(['python3', T + 'c2/crates.py', C, C + '/crates.log'])
subprocess.run(['python3', T + 'c2/suite.py', C])
print('ALL-DONE', flush=True)
