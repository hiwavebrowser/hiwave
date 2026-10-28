"""wait_rows.py <file> <rows> <max seconds>: wait until <file> has <rows> lines
(or the time is up), then print it."""
import pathlib
import sys
import time

path, rows, limit = pathlib.Path(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
end = time.time() + limit
while time.time() < end:
    if path.exists() and len(path.read_text().splitlines()) >= rows:
        break
    time.sleep(10)
print(path.read_text() if path.exists() else "(no file)")
