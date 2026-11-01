// The z part of `translate`, Chromium 143. A 100x50 box at (20,10) under translate:7px first, so a refusal reads 27 10.
// node translate_z_probe.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log(b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
const values = ['1px 2px 3%', '1px 2px 0%', '1px 2px auto', '1px 2px AUTO', '1px 2px fit-content', '1px 2px calc(1px + 1%)', '1px 2px calc(0% + 1px)', '1px 2px min(1%, 2px)', '1px 2px max(1px, calc(1px + 1%))', '1px 2px clamp(1px, 1%, 2px)',
  '1px 2px 0', '1px 2px 3px', '1px 2px -3px', '1px 2px 3em', '1px 2px 3vw', '1px 2px calc(1px + 1em)', '1px 2px min(1px, 2px)', '1px 2px 3', '10% 10% 3px'];
for (const v of values) {
  await p.setContent(`<!doctype html><style>body{margin:0}#b{position:absolute;left:20px;top:10px;width:100px;height:50px;translate:7px;translate:${v}}</style><div id=b></div>`);
  console.log(JSON.stringify(v), await p.evaluate(() => { const r = document.getElementById('b').getBoundingClientRect(); return [r.x, r.y, r.width, r.height].map((n) => +n.toFixed(3)).join(' '); }));
}
await b.close();
