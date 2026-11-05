"""wait_for.py <file> <regex> <secs>: poll a log for a regex; print the tail when found or at timeout."""
import re, sys, time
path, pat, secs = sys.argv[1], re.compile(sys.argv[2]), float(sys.argv[3])
end = time.time() + secs
s = ''
while time.time() < end:
    try:
        s = open(path, errors='replace').read()
    except FileNotFoundError:
        s = ''
    if pat.search(s):
        print('FOUND')
        break
    time.sleep(10)
else:
    print('TIMEOUT')
print(s[-2500:])
