// The R1's list with var() in an angle, Chromium 143, same page shape as c10b2_r1_probe.mjs.
// node c10b2_var_probe.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log('chromium', b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
for (const v of ['translate(-50%,-50%) rotate(calc(var(--i) * 30deg))', 'rotate(var(--a))', 'scale(var(--i))']) {
  await p.setContent(`<!doctype html><style>body{margin:0}#w{transform:translateY(3px)}#b{--i:2;--a:90deg;position:absolute;left:20px;top:10px;width:100px;height:50px;transform:translateX(7px);transform:${v}}</style><div id=w><div id=b></div></div>`);
  console.log(v, await p.evaluate(() => { const r = document.getElementById('b').getBoundingClientRect(); return [r.x, r.y, r.width, r.height].map((n) => +n.toFixed(3)).join(' '); }));
}
await b.close();
