"""ctx.py <html> <needle> [before] [after]: print text around a needle; also the open-tag
ancestor chain of the needle's position (a rough stack of unclosed <div>/<a>/... tags)."""
import re, sys
t = open(sys.argv[1]).read()
needle = sys.argv[2]
before = int(sys.argv[3]) if len(sys.argv) > 3 else 0
after = int(sys.argv[4]) if len(sys.argv) > 4 else 0
i = t.find(needle)
print('pos', i)
if before or after:
    print(t[max(0, i - before):i + after])
    print('-----')
VOID = {'img', 'br', 'input', 'meta', 'link', 'hr', 'source', 'path', 'wbr', 'col', 'base', 'area'}
stack = []
body = t.find('<body')
for m in re.finditer(r'<(/?)([a-zA-Z][a-zA-Z0-9-]*)([^>]*)>', t[body:i]):
    close, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
    if tag in ('script', 'style'):
        continue
    if close:
        while stack and stack[-1][0] != tag:
            stack.pop()
        if stack:
            stack.pop()
    elif tag not in VOID and not attrs.endswith('/'):
        stack.append((tag, attrs.strip()[:160]))
for tag, attrs in stack:
    print('<%s %s>' % (tag, attrs))
