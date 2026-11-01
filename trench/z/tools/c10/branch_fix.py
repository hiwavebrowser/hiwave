#!/usr/bin/env python3
"""The receipt's branch reads HEAD in a detached lane worktree; name the pushed branch."""
W = '/Users/petecopeland/Repos/.worktrees/'
for wt, branch in (('z-c10b', 'atlas/z-c10b-transform-rects'), ('z-c10b2', 'atlas/z-c10b2-transform-3d')):
    p = W + wt + '/scratch/pr-final.md'
    s = open(p).read()
    assert '"branch": "HEAD"' in s
    open(p, 'w').write(s.replace('"branch": "HEAD"', '"branch": "%s"' % branch))
