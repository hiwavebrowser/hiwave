#!/usr/bin/env python3
"""selfuse.py <lib.rs> name...: for each `fn name` in an impl, the `self.<x>` it uses (fields and methods)."""
import re, sys, collections
src = open(sys.argv[1]).read().split('\n')
names = sys.argv[2:]
starts = {}
for i, l in enumerate(src):
    m = re.match(r'^    (?:pub(?:\(crate\))? )?fn (\w+)', l)
    if m:
        starts.setdefault(m.group(1), []).append(i)
def body(i):
    depth, seen = 0, False
    for j in range(i, len(src)):
        depth += src[j].count('{') - src[j].count('}')
        if '{' in src[j]:
            seen = True
        if seen and depth == 0:
            return i, j
    return i, len(src)
for n in names:
    for s in starts.get(n, []):
        a, b = body(s)
        uses = collections.Counter()
        for l in src[a:b + 1]:
            code = l.split('//')[0]
            for m in re.finditer(r'\bself\.(\w+)(\s*\()?', code):
                uses[m.group(1) + ('()' if m.group(2) else '')] += 1
        print(f"{n} L{a + 1}-{b + 1} ({b - a + 1} lines):", ', '.join(f"{k}x{v}" for k, v in sorted(uses.items())))
