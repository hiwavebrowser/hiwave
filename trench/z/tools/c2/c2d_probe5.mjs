// C2(d), fifth page: a stuck box over an earlier fixed bar, the shape in render_no_clone_tests.
// usage: node c2d_probe5.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = `<!doctype html><style>body{margin:0;height:3000px}
#bar{position:fixed;left:0;top:0;width:400px;height:24px;background:#000}
#stick{position:sticky;top:0;height:20px;background:#08f}</style><body>
<div id=bar></div><div style="height:24px"></div><div id=stick></div></body>`;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 400, height: 300 } });
await p.route('http://probe.test/**', r => r.fulfill({ contentType: 'text/html', body: html }));
await p.goto('http://probe.test/page');
const out = {};
for (const y of [0, 10, 30, 400]) {
  await p.evaluate(y => window.scrollTo(0, y), y);
  out[y] = await p.evaluate(() => [10, 22, 30, 40].map(py => (document.elementFromPoint(200, py) || {}).id || '-').join(' ') + ' stick@' + document.getElementById('stick').getBoundingClientRect().y);
}
console.log(JSON.stringify(out));
await b.close();
