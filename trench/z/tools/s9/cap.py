"""cap.py <binary> <outdir> [url]: one live capture (frame png + layout + display list)."""
import subprocess, sys, pathlib
b, out = sys.argv[1], pathlib.Path(sys.argv[2])
url = sys.argv[3] if len(sys.argv) > 3 else 'https://www.google.com/'
out.mkdir(parents=True, exist_ok=True)
r = subprocess.run([b, '--url', url, '--dump-frame', str(out / 'f.ppm'), '--dump-layout', str(out / 'layout.json'),
                    '--dump-display-list', str(out / 'dl.json'), '--timeout-ms', '60000'],
                   capture_output=True, text=True)
print(r.returncode, r.stdout[-800:], r.stderr[-400:])
from PIL import Image
Image.open(out / 'f.ppm').save(out / 'f.png')
