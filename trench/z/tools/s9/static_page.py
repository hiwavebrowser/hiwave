"""static_page.py <served.html> <out.html>: the archived google page with scripts removed and
root-relative URLs made absolute (https://www.google.com), so Chromium and the engine get the
same bytes from a file."""
import re, sys
t = open(sys.argv[1]).read()
t = re.sub(r'<script\b.*?</script>', '', t, flags=re.S | re.I)
t = re.sub(r'(src|href|srcset)="/(?!/)', r'\1="https://www.google.com/', t)
t = re.sub(r'url\(/(?!/)', 'url(https://www.google.com/', t)
open(sys.argv[2], 'w').write(t)
print(len(t))
