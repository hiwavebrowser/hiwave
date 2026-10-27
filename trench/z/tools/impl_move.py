#!/usr/bin/env python3
"""move.py <lib.rs> name...: move the named `impl Engine` methods into `impl LayoutCtx`
blocks in place (the impl block is closed before each run of moved methods and
reopened after), rewrite `self.lctx.` to `self.` inside them, and route the other
Engine methods' `self.<moved>(` calls through `self.lctx.`."""
import re, sys
path, names = sys.argv[1], set(sys.argv[2:])
src = open(path).read().split('\n')

# Top-level impl blocks: (start line, end line, header).
blocks, i = [], 0
while i < len(src):
    if re.match(r'^impl\b', src[i]):
        depth, j = 0, i
        while True:
            depth += src[j].count('{') - src[j].count('}')
            if depth == 0 and '{' in ''.join(src[i:j + 1]):
                break
            j += 1
        blocks.append((i, j, src[i]))
        i = j + 1
    else:
        i += 1

def method_span(i):
    """(first line incl. docs/attrs, last line) of the method starting at i."""
    a = i
    while a > 0 and re.match(r'^    (///|#\[|//)', src[a - 1]):
        a -= 1
    depth, seen, j = 0, False, i
    while True:
        depth += src[j].count('{') - src[j].count('}')
        seen = seen or '{' in src[j]
        if seen and depth == 0:
            return a, j
        j += 1

spans = []  # (a, b, name, moved)
for (s, e, h) in blocks:
    if h.strip() != 'impl Engine {':
        continue
    for k in range(s + 1, e):
        m = re.match(r'^    (?:pub(?:\(crate\))? )?fn (\w+)', src[k])
        if m:
            a, b = method_span(k)
            spans.append((a, b, m.group(1), m.group(1) in names))
found = {n for (_, _, n, mv) in spans if mv}
missing = names - found
if missing:
    sys.exit('not found in impl Engine: %s' % sorted(missing))

moved_lines = set()
for (a, b, n, mv) in spans:
    if mv:
        moved_lines.update(range(a, b + 1))
engine_lines = set()
for (s, e, h) in blocks:
    if h.strip() == 'impl Engine {':
        engine_lines.update(range(s, e + 1))
call = re.compile(r'\bself\.(%s)\s*\(' % '|'.join(sorted(names)))
for k in range(len(src)):
    if k in moved_lines:
        src[k] = src[k].replace('self.lctx.', 'self.')
    elif k in engine_lines:
        src[k] = call.sub(lambda m: 'self.lctx.%s(' % m.group(1), src[k])

# Runs of moved methods, separated only by blank lines.
ins = []  # (line index, text) inserted before that line
spans.sort()
r = 0
while r < len(spans):
    if not spans[r][3]:
        r += 1
        continue
    q = r
    while q + 1 < len(spans) and spans[q + 1][3] and all(not src[x].strip() for x in range(spans[q][1] + 1, spans[q + 1][0])):
        q += 1
    ins.append((spans[r][0], '}\n\nimpl layout_ctx::LayoutCtx {'))
    ins.append((spans[q][1] + 1, '}\n\nimpl Engine {'))
    r = q + 1
for (k, t) in sorted(ins, reverse=True):
    src.insert(k, t)
open(path, 'w').write('\n'.join(src))
print('moved', len(found), 'methods in', len(ins) // 2, 'runs')
