"""Y2 diagnosis, local only: a pass-through proxy for --replay-proxy that patches
React's hydration-mismatch function to report the unclaimed node's shape.
usage: y2proxy.py <binary> <live_ms>"""
import http.server, json, pathlib, socketserver, ssl, subprocess, sys, threading, urllib.error, urllib.request, gzip

S = pathlib.Path(__file__).parent
PROBE = r"""try{var __s=function(n){if(!n)return null;if(n.nodeType===3)return '#t'+n.data.length;if(n.nodeType===8)return '#c:'+(n.data.length<5?n.data:'len'+n.data.length);return n.nodeName+(n.id?'#'+n.id:'')+(typeof n.className==='string'&&n.className?'.'+n.className.slice(0,60):'')};
var __r={fiberType:typeof e.type==='string'?e.type:String(e.tag),tag:e.tag,next:__s(rJ),nextParent:rJ&&__s(rJ.parentNode),
reactKids:function(){var o=[],c=e.child;while(c&&o.length<40){o.push(typeof c.type==='string'?c.type:(c.tag===6?'#text':'tag'+c.tag));c=c.sibling}return o}(),
domKids:function(){var o=[],k=e.stateNode&&e.stateNode.childNodes;for(var i=0;k&&i<k.length&&i<40;i++)o.push(__s(k[i]));return o}(),
props:Object.keys(e.memoizedProps||{}).slice(0,30),
chain:function(){var o=[],p=e.stateNode;while(p&&o.length<14){o.push(__s(p));p=p.parentNode}return o}(),
t:Date.now()};var __x=new XMLHttpRequest();__x.open('POST','/__y2',true);__x.send(JSON.stringify(__r));}catch(__e){}"""
reports = []


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def relay(self):
        n = int(self.headers.get('Content-Length') or 0)
        data = self.rfile.read(n) if n else None
        if self.path.startswith('/__y2'):
            reports.append(data.decode('utf-8', 'replace'))
            self.send_response(204)
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        url = self.headers.get('x-original-url')
        heads = {k: v for k, v in self.headers.items() if k.lower() not in
                 ('host', 'x-original-url', 'connection', 'content-length', 'accept-encoding')}
        heads['Accept-Encoding'] = 'gzip'
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=heads, method=self.command), timeout=25)
            status, rh, body = r.status, r.headers, r.read()
        except urllib.error.HTTPError as e:
            status, rh, body = e.code, e.headers, e.read()
        except Exception:
            self.send_response(502)
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        if rh.get('Content-Encoding') == 'gzip':
            body = gzip.decompress(body)
        if url and '87c73c54-' in url and url.endswith('.js'):
            old = b'function r4(e){'
            assert body.count(old) == 1
            body = body.replace(old, old + PROBE.encode())
        self.send_response(status)
        for k, v in rh.items():
            if k.lower() in ('transfer-encoding', 'connection', 'content-length', 'content-encoding', 'alt-svc',
                             'content-security-policy', 'content-security-policy-report-only', 'strict-transport-security'):
                continue
            self.send_header(k, v)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

    do_GET = do_POST = do_HEAD = do_OPTIONS = do_PUT = relay

    def log_message(self, *a):
        pass


class Srv(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


srv = Srv(('127.0.0.1', 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
log = S / 'y2-proxy.jsonl'
log.unlink(missing_ok=True)
r = subprocess.run([sys.argv[1], '--url', 'https://www.yahoo.com/', '--replay-proxy', 'http://127.0.0.1:%d' % srv.server_address[1],
                    '--live-ms', sys.argv[2], '--timeout-ms', '120000', '--event-log', str(log), '--event-log-error-text',
                    '--dump-frame', str(S / 'y2-proxy.ppm')], capture_output=True, text=True, timeout=170)
print('rc', r.returncode, 'reports', len(reports))
for line in reports[:4]:
    print(json.dumps(json.loads(line), indent=0)[:3500])
print('418 in log:', log.read_text().count('Minified React error #418'))
