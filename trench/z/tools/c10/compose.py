#!/usr/bin/env python3
"""compose.py <package> <base> <campaign> <run ...>: run from the worktree (receipt.py reads the cwd). Fills scratch/pr.md into scratch/pr-final.md."""
import json, re, subprocess, sys
package, base, camp, runs = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
r = subprocess.run(['python3', 'scripts/receipt.py', '--package', package, '--binary', 'target/parity/parity-capture', '--base', base,
                    '--campaign', camp, '--runs'] + runs + ['--profile', 'parity'], capture_output=True, text=True, check=True)
receipt = r.stdout.strip()
data = json.loads(receipt)
print(data['candidate_sha'], data['branch'], data['binary_sha256'], data['dirty_state'], data['campaign']['passed'], data['repo'])
s = open('scratch/pr.md').read()
s = s.replace('@@RECEIPT@@', '## Receipt (`scripts/receipt.py`)\n\n```json\n' + receipt + '\n```')
s = s.replace('@@SUITES@@', 'Headless engine 1370/0; layout 881/0; bindings 428/0; engine lib 618/0; `hiwave-app` build rc=0.')
s = s.replace('on the #C10(b2) repeat lyft had none', 'on the C10(b2) repeat lyft had none')
assert '@@' not in s
open('scratch/pr-final.md', 'w').write(s)
