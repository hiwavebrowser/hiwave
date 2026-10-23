"""t2_fixture.py <parity-capture> <out dir> [extra args...]: T2 acceptance fixture, end to end.

Serves a page on 127.0.0.1 whose subresources are: a script on a shield-listed
host (doubleclick.net, blocked before any DNS or connect), a route that never
answers (/hang, for the timeout), and a plain image. Runs parity-capture
--shield --url on it with an event log, then prints each request's outcome.
"""
import http.server
import json
import pathlib
import socketserver
import subprocess
import sys
import threading
import time

binary, out = sys.argv[1], pathlib.Path(sys.argv[2])
extra = sys.argv[3:]
out.mkdir(parents=True, exist_ok=True)

PNG = bytes([
    137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82, 0, 0, 0, 1, 0, 0, 0, 1, 8, 2, 0, 0, 0, 144, 119,
    83, 222, 0, 0, 0, 12, 73, 68, 65, 84, 120, 156, 99, 248, 207, 192, 0, 0, 3, 1, 1, 0, 201, 254, 146, 239, 0, 0, 0,
    0, 73, 69, 78, 68, 174, 66, 96, 130,
])
PAGE = b"""<html><body><p>t2 fixture</p>
<img src="/ok.png">
<img src="/hang">
<script src="https://securepubads.g.doubleclick.net/tag/js/gpt.js"></script>
</body></html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path == "/hang":
            time.sleep(60)
            return
        body, ctype = (PNG, "image/png") if self.path == "/ok.png" else (PAGE, "text/html")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


srv = Server(("127.0.0.1", 0), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]
log = out / "fixture.jsonl"
args = [binary, "--url", "http://127.0.0.1:%d/" % port, "--shield", "--timeout-ms", "120000", "--event-log", str(log)] + extra
r = subprocess.run(args, capture_output=True, text=True, timeout=150)
(out / "fixture.err").write_text(r.stderr)
print(r.stdout[-600:])
print("exit", r.returncode, [l for l in r.stderr.splitlines() if l.startswith("shield:")])
reqs, outcome = {}, {}
for line in log.open():
    rec = json.loads(line)
    if rec["type"] == "request":
        reqs[rec["id"]] = rec
    elif rec["type"] in ("response", "failure"):
        outcome[rec["id"]] = rec
for i, q in sorted(reqs.items()):
    o = outcome.get(i, {})
    url = q["url"].replace("127.0.0.1:%d" % port, "127.0.0.1:PORT")
    desc = o.get("type", "open")
    if desc == "response":
        desc += " %s" % o["status"]
    elif desc == "failure":
        desc += " %s %s blocked_by=%s ms=%s" % (o.get("stage"), o.get("reason"), json.dumps(o.get("blocked_by")), o.get("duration_ms"))
    print(i, q["resource_type"], q["initiator"], url, "->", desc)
srv.shutdown()
