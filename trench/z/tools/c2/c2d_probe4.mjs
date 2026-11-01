// C2(d), fourth page: both insets set, fitting and not fitting; a scroller child vs its extent.
// usage: node c2d_probe4.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const box = (id, left, css, before, after) => `<div class=sc id=${id}-s style="left:${left}px"><div style="height:${before}px"></div><div class=st id=${id} style="${css}"></div><div style="height:${after}px"></div></div>`;
const html = `<!doctype html><style>body{margin:0}
.sc{overflow:auto;width:200px;height:100px;position:absolute;top:0}
.st{position:sticky;width:50px}
</style><body>` +
  box('p', 0, 'top:5px;bottom:5px;height:20px', 300, 300) +
  box('q', 210, 'top:5px;bottom:5px;height:95px', 50, 600) +
  box('r', 420, 'top:5px;bottom:5px;height:90px', 50, 600) +
  box('s', 630, 'top:5px;bottom:5px;height:95px', 300, 300) +
  `</body>`;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1000, height: 600 } });
await p.route('http://probe.test/**', r => r.fulfill({ contentType: 'text/html', body: html }));
await p.goto('http://probe.test/page');
const out = {};
for (const id of ['p', 'q', 'r', 's']) {
  out[id] = await p.evaluate(async (id) => {
    const s = document.getElementById(id + '-s'), e = document.getElementById(id), row = [];
    for (const o of [0, 20, 50, 100, 280, 400]) {
      s.scrollTop = o;
      row.push(s.scrollTop + ':' + e.getBoundingClientRect().y);
    }
    return row.join(' ');
  }, id);
}
console.log(JSON.stringify(out));
await b.close();
