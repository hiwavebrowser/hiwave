"""wait_for.py <file> <regex> <secs>: poll until regex appears, then print the tail."""
import re, sys, time

path, pat, secs = sys.argv[1], re.compile(sys.argv[2]), float(sys.argv[3])
end = time.time() + secs
text = ''
while time.time() < end:
    try:
        text = open(path, errors='replace').read()
    except FileNotFoundError:
        text = ''
    if pat.search(text):
        break
    time.sleep(10)
else:
    print('[wait_for: timed out]')
print('\n'.join(text.splitlines()[-30:]))
