// S1: Chromium on the engine test's shape. Two loopback origins; /start/<port> on the first 302s to
// /app/page on the second, whose page links style.css relatively. Prints what each server saw and
// location.href / baseURI / hash / #box width, with and without a requested fragment.
// node redirect_probe.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
import http from 'node:http';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const seen = { first: [], second: [] };
const PAGE = `<!doctype html><html><head><title>Target</title><link rel="stylesheet" href="style.css"></head>
<body><div id="box">box</div><img src="pic.png" width="1" height="1"></body></html>`;
const second = http.createServer((q, r) => {
  seen.second.push(q.url);
  if (q.url === '/app/page') { r.writeHead(200, { 'content-type': 'text/html' }); r.end(PAGE); }
  else if (q.url === '/app/style.css') { r.writeHead(200, { 'content-type': 'text/css' }); r.end('#box{width:123px;height:45px;display:block}'); }
  else { r.writeHead(404); r.end(); }
});
const first = http.createServer((q, r) => {
  seen.first.push(q.url);
  const m = q.url.match(/^\/start\/(\d+)$/);
  if (m) { r.writeHead(302, { location: `http://127.0.0.1:${m[1]}/app/page` }); r.end(); }
  else { r.writeHead(404); r.end(); }
});
await new Promise((ok) => second.listen(0, '127.0.0.1', ok));
await new Promise((ok) => first.listen(0, '127.0.0.1', ok));
const b = await chromium.launch();
console.log('// ' + b.version());
const p = await b.newPage();
for (const frag of ['', '#box']) {
  seen.first.length = 0; seen.second.length = 0;
  await p.goto(`http://127.0.0.1:${first.address().port}/start/${second.address().port}${frag}`);
  await p.waitForLoadState('load');
  const r = await p.evaluate(() => [location.href, document.baseURI, location.hash,
    document.querySelector('link').href, document.getElementById('box').getBoundingClientRect().width]);
  console.log(JSON.stringify({ frag, href: r[0], baseURI: r[1], hash: r[2], link: r[3], width: r[4],
    first: [...seen.first], second: [...seen.second].filter((u) => u !== '/favicon.ico') }));
}
await b.close(); first.close(); second.close();
