"""wait_for.py <file> <regex> <secs> : poll a file until the regex appears or the time runs out."""
import re, sys, time

path, pat, secs = sys.argv[1], re.compile(sys.argv[2]), float(sys.argv[3])
end = time.time() + secs
while time.time() < end:
    try:
        txt = open(path, errors='replace').read()
    except OSError:
        txt = ''
    m = pat.search(txt)
    if m:
        print('found', m.group(0)[:200])
        sys.exit(0)
    time.sleep(10)
print('timeout')
