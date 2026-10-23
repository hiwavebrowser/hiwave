"""For each worktree name under ~/Repos/.worktrees: its git common dir, tracked
changes, HEAD, and whether HEAD is on some remote branch (safe to remove).
usage: wt_check.py <name> [name ...]"""
import subprocess, sys
W = '/Users/petecopeland/Repos/.worktrees/'
for name in sys.argv[1:]:
    g = ['git', '-C', W + name]
    run = lambda *a: subprocess.run(g + list(a), capture_output=True, text=True).stdout.strip()
    head = run('rev-parse', 'HEAD')
    on_remote = run('branch', '-r', '--contains', head)
    print('==', name)
    print('  common', run('rev-parse', '--git-common-dir'))
    print('  head', run('log', '--oneline', '-1'))
    print('  tracked changes:', run('status', '--short', '-uno') or 'none')
    print('  head on remote:', on_remote.splitlines()[:3] or 'NO')
