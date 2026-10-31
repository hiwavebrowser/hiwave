"""grep_asset.py <url> <out file> <needle> [context] : fetch a script asset (product UA) once to a private file, print context around each needle hit."""
import os, sys, urllib.request

url, out, needle = sys.argv[1], sys.argv[2], sys.argv[3]
ctx = int(sys.argv[4]) if len(sys.argv) > 4 else 300
if not os.path.exists(out):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15 HiWave/1.0'})
    open(out, 'wb').write(urllib.request.urlopen(req, timeout=60).read())
s = open(out, encoding='utf-8', errors='replace').read()
i = 0
n = 0
while n < 6:
    i = s.find(needle, i)
    if i < 0:
        break
    print('---', i)
    print(s[max(0, i - ctx):i + ctx])
    i += len(needle)
    n += 1
