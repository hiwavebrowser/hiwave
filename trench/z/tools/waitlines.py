"""Wait until <file> has at least <n> lines or <secs> pass; print the lines.
usage: waitlines.py <file> <n> <secs>"""
import pathlib, sys, time

path, n, secs = pathlib.Path(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
end = time.time() + secs
while time.time() < end:
    if path.exists() and len(path.read_text().splitlines()) >= n:
        break
    time.sleep(5)
print(path.read_text() if path.exists() else '(missing)')
