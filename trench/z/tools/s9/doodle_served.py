"""doodle_served.py <dir>: serve <dir> on 127.0.0.1 (one thread, this process only), capture
static.html with scratch/bins/base and scratch/bins/cand through --url, and write
<dir>/sbs-served.png (Chrome | base | candidate, a third of full size) plus each arm's image
draw rect from the display list."""
import functools, http.server, json, pathlib, subprocess, sys, threading
from PIL import Image

d = pathlib.Path(sys.argv[1]).resolve()
wt = d.parent.parent
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(d))
handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
url = 'http://127.0.0.1:%d/static.html' % srv.server_address[1]
frames = []
for arm in ('base', 'cand'):
    ppm, dl = d / (arm + '-served.ppm'), d / (arm + '-served.dl.json')
    r = subprocess.run([str(wt / 'scratch/bins' / arm), '--url', url, '--dump-frame', str(ppm),
                        '--dump-display-list', str(dl), '--timeout-ms', '60000'], capture_output=True, text=True)
    draws = []
    if dl.exists():
        for c in json.loads(dl.read_text())['commands']:
            if c.get('op') == 'image' and 'doodle' in str(c.get('url')):
                draws.append(c['dest_rect'])
    print(arm, 'rc', r.returncode, 'doodle draws', draws)
    frames.append(Image.open(ppm).convert('RGB'))
srv.shutdown()
imgs = [Image.open(d / 'chrome.png').convert('RGB')] + frames
w = sum(i.width for i in imgs)
out = Image.new('RGB', (w, max(i.height for i in imgs)), 'white')
x = 0
for i in imgs:
    out.paste(i, (x, 0))
    x += i.width
out.resize((w // 3, out.height // 3)).save(d / 'sbs-served.png')
print(d / 'sbs-served.png')
