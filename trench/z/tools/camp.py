"""26-case campaign on a built parity-capture binary, without a build.
usage: camp.py <worktree> <tag> <binary path>
parity_test.py builds with bare cargo into target/release; here cargo is a
stub and the binary under test is copied to where parity_test.py looks.
Writes <worktree>/scratch/camp-<tag>.json and camp-<tag>.log.
(Adapted from Prometheus's scratch/prom/camp.py; kept in the hub because
lane scratch dies with its worktree.)"""
import hashlib, os, pathlib, shutil, subprocess, sys

WT, tag, binary = pathlib.Path(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3])
S = WT / 'scratch'
stub = S / 'stubbin'
stub.mkdir(parents=True, exist_ok=True)
(stub / 'cargo').write_text('#!/bin/sh\nexit 0\n')
(stub / 'cargo').chmod(0o755)
dest = WT / 'target/release/parity-capture'
dest.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(binary, dest)
sha = hashlib.sha256(dest.read_bytes()).hexdigest()
env = dict(os.environ, PATH=str(stub) + ':' + os.environ['PATH'])
out = S / ('camp-%s.json' % tag)
r = subprocess.run(['python3', 'scripts/parity_test.py', '--output', str(out)], cwd=WT, env=env,
                   capture_output=True, text=True)
(S / ('camp-%s.log' % tag)).write_text('binary %s sha256 %s\n' % (binary, sha) + r.stdout + r.stderr)
print('binary', binary.name, 'sha256', sha)
print(r.stdout[-1500:])
print('exit', r.returncode)
