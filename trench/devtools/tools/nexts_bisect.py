"""Serve each inline __next_s script of yahoo's HTML as its own page; run parity-capture
on each with error text kept; print which ones throw and where. Local only (error text).
usage: env PC_BIN=<parity-capture> python3 -I nexts_bisect.py parser|inner [snippet.js]
  parser: the script as a parser <script>; inner: inserted via script.innerHTML (Next's way).
Event logs go to $PC_BIN's directory/nexts/. Found #777's two SyntaxErrors (2026-10-24)."""
import http.server, json, os, pathlib, re, subprocess, sys, threading, urllib.request

BIN = pathlib.Path(os.environ["PC_BIN"])
OUT = BIN.parent / "nexts"
OUT.mkdir(exist_ok=True)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15 HiWave/1.0"


def entries(html):
    for m in re.finditer(r"__next_s\s*=\s*self\.__next_s\s*\|\|\s*\[\]\)\.push\(", html):
        start, depth, i, in_str = m.end(), 0, m.end(), False
        while i < len(html):
            ch = html[i]
            if in_str:
                if ch == "\\":
                    i += 2
                    continue
                if ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
            elif ch in "[{(":
                depth += 1
            elif ch in "]})":
                depth -= 1
                if depth < 0:
                    break
            i += 1
        item = json.loads(html[start:i])
        props = item[1] if len(item) > 1 else {}
        if (props or {}).get("children"):
            yield props.get("id"), props["children"]


MODE = sys.argv[1] if len(sys.argv) > 1 else "parser"
pages = {}
if len(sys.argv) > 2:
    pages["snippet"] = pathlib.Path(sys.argv[2]).read_text()
else:
    html = urllib.request.urlopen(urllib.request.Request("https://www.yahoo.com/", headers={"User-Agent": UA}), timeout=30).read().decode("utf-8", "replace")
    for ident, code in entries(html):
        pages[ident] = code


class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        name = self.path.strip("/")
        code = pages.get(name, "")
        if MODE == "inner":
            # As Next's __next_s loader does it: script.innerHTML = children, then append.
            loader = "var s=document.createElement('script');s.innerHTML=" + json.dumps(code).replace("</", "<\\/") + ";document.head.appendChild(s);"
        else:
            loader = code.replace("</script", "<\\/script")
        body = ("<!doctype html><html><head><script>" + loader + "</script></head><body>x</body></html>").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]
for name in pages:
    log = OUT / (name + ".jsonl")
    cmd = [str(BIN), "--url", "http://127.0.0.1:%d/%s" % (port, name), "--live-ms", "500", "--timeout-ms", "30000",
           "--event-log", str(log), "--event-log-error-text"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    errs = [rec for rec in map(json.loads, open(log)) if rec["type"] == "script_error"] if log.exists() else []
    print(name, "exit", r.returncode, "len", len(pages[name]),
          [(e.get("name"), e.get("message")) for e in errs] or "no error")
srv.shutdown()
