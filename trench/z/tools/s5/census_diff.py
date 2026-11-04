#!/usr/bin/env python3
"""census_diff.py <worktree> <base rev>: declaration-census gaps at base vs the working tree."""
import subprocess, sys
from pathlib import Path
wt, base = sys.argv[1], sys.argv[2]
sys.path.insert(0, wt + '/scripts/tests'); sys.path.insert(0, wt + '/scripts')
import os
os.chdir(wt)
import test_declaration_census as t
base_src = subprocess.run(['git', '-C', wt, 'show', base + ':crates/rustkit-engine/src/lib.rs'],
                          capture_output=True, text=True, check=True).stdout
for name, src in (('base', base_src), ('head', t.ENGINE_SOURCE.read_text())):
    r = t.run_census(src, t.load_registry(include_holdout=False), t.load_ledger())
    print(name, len(r['gaps']), sorted((g['property'], g['declarations']) for g in r['gaps']))
    print('  buckets', [(b['key'], b['declarations']) for b in r['top_three_buckets']])
