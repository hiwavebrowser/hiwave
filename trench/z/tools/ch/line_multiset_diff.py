"""line_multiset_diff.py <repo> <path>: lines (whitespace-stripped) whose count differs HEAD vs worktree."""
import collections, subprocess, sys

repo, path = sys.argv[1], sys.argv[2]
old = subprocess.run(['git', '-C', repo, 'show', 'HEAD:' + path], capture_output=True, text=True, check=True).stdout
new = open(repo + '/' + path).read()
a = collections.Counter(l.strip() for l in old.split('\n') if l.strip())
b = collections.Counter(l.strip() for l in new.split('\n') if l.strip())
for line in sorted(set(a) | set(b)):
    if a[line] != b[line]:
        print('%+d  %s' % (b[line] - a[line], line))
