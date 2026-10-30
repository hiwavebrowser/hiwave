"""Same bytes in both engines: static.html with one dump script at the end.
Prints the first differences of the canonical DOM (tag, attribute names and
value lengths, text lengths, comment shape). Shape only; nothing is committed."""
import http.server, json, pathlib, socketserver, subprocess, sys, threading, difflib

S = pathlib.Path(__file__).parent
BIN = sys.argv[1]
DUMP = r"""<script>(function(){
var out=[];
function walk(n,d){
  var pad=d+' ';
  if(n.nodeType===3){out.push(pad+'#t'+n.data.length);return;}
  if(n.nodeType===8){var c=n.data;out.push(pad+'#c'+(c.length<4?c:'len'+c.length));return;}
  if(n.nodeType===1){
    var names=[];for(var i=0;i<n.attributes.length;i++){var a=n.attributes[i];names.push(a.name+'='+a.value.length);}
    names.sort();out.push(pad+n.tagName+' '+names.join(','));
  } else out.push(pad+'#n'+n.nodeType);
  var kids=n.childNodes;for(var j=0;j<kids.length;j++)walk(kids[j],d+1);
  if(n.content&&n.content.childNodes){out.push(pad+'[content '+n.content.childNodes.length+']');}
}
walk(document,0);
var x=new XMLHttpRequest();x.open('POST','/dump',true);x.send(out.join('\n'));
})();</script>"""
html = (S / 'static.html').read_text()
at = html.lower().rfind('</body>')
page = (html[:at] + DUMP + html[at:]).encode() if at > 0 else (html + DUMP).encode()


got = []


class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = page if self.path == '/' else b''
        self.send_response(200 if self.path == '/' else 404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        got.append(self.rfile.read(int(self.headers['Content-Length'])).decode())
        self.send_response(200)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def log_message(self, *a):
        pass


srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), H)
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
url = 'http://127.0.0.1:%d/' % port

log = S / 'tree-engine.jsonl'
log.unlink(missing_ok=True)
r = subprocess.run([BIN, '--url', url, '--event-log', str(log), '--event-log-console-text', '--timeout-ms', '60000', '--live-ms', '6000',
                    '--dump-frame', str(S / 'tree-engine.ppm')], capture_output=True, text=True, timeout=120)
engine = got[-1].split('\n') if got else ['NO POST', r.stdout[-300:]]
got.clear()

mjs = S.parent / 'tools/parity_oracle/y2_tree.mjs'
mjs.write_text("""import { chromium } from 'playwright';
import { getDeterministicLaunchOptions } from './deterministic.mjs';
const browser = await chromium.launch(getDeterministicLaunchOptions());
const page = await (await browser.newContext({ viewport: { width: 1280, height: 800 } })).newPage();
await page.goto(process.argv[2], { waitUntil: 'load', timeout: 60000 });
await page.waitForTimeout(500);
await browser.close();
""")
c = subprocess.run(['node', str(mjs)] + [url], cwd=S.parent, capture_output=True, text=True, timeout=120)
mjs.unlink()
chrome = got[-1].split('\n') if got else ['NO POST']
(S / 'tree-engine.txt').write_text('\n'.join(engine))
(S / 'tree-chrome.txt').write_text('\n'.join(chrome))
print('engine lines', len(engine), 'chrome lines', len(chrome), c.stderr[-300:])
shown = 0
sm = difflib.SequenceMatcher(None, engine, chrome, autojunk=False)
ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
print('diff blocks', len(ops))
for tag, i1, i2, j1, j2 in ops[:int(sys.argv[2]) if len(sys.argv) > 2 else 25]:
    print('---', tag, 'engine line', i1, 'chrome line', j1)
    for l in engine[i1:min(i2, i1 + 6)]:
        print('  E', l[:140])
    for l in chrome[j1:min(j2, j1 + 6)]:
        print('  C', l[:140])
