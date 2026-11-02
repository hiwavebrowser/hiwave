// C10 17:45 items: which depth and perspective values a transform function takes. Chromium 143.
// node depth_persp_probe.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log(b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
const values = [
  'translateZ(10px)', 'translateZ(0)', 'translateZ(10%)', 'translateZ(calc(10%))', 'translateZ(calc(10% + 1px))', 'translateZ(calc(10px + 1px))', 'translateZ(calc(1vw))', 'translateZ(calc(0% + 0px))', 'translateZ(calc(1px * 2))', 'translateZ(calc(5% - 5%))', 'translateZ(1)', 'translateZ(calc(1))',
  'translate3d(1px,2px,3px)', 'translate3d(1px,2px,3%)', 'translate3d(1px,2px,calc(3%))', 'translate3d(1px,2px,calc(3% + 1px))', 'translate3d(1px,2px,calc(3px + 1px))', 'translate3d(10%,20%,0)', 'translate3d(calc(10% + 1px),0,0)', 'translate3d(0,0,calc(1em))', 'translate3d(0,0,calc(0%))',
  'perspective(100px)', 'perspective(0)', 'perspective(0px)', 'perspective(-1px)', 'perspective(none)', 'perspective(1)', 'perspective(10%)', 'perspective(1vw)', 'perspective(-1vw)', 'perspective(-1vh)', 'perspective(-1vmin)', 'perspective(-1vmax)', 'perspective(-1em)', 'perspective(-1rem)', 'perspective(calc(100px))', 'perspective(calc(1vw - 100px))', 'perspective(calc(100px - 1vw))', 'perspective(calc(10vw - 100px))', 'perspective(calc(-1px))', 'perspective(calc(100vw - 1000px))', 'perspective(calc(1000px - 100vw))', 'perspective(calc(1em - 100px))', 'perspective(calc(100px - 1em))', 'perspective(calc(10%))',
];
for (const v of values) {
  await p.setContent(`<!doctype html><style>body{margin:0}</style><div id=t style="width:100px;height:100px;transform:${v}"></div>`);
  console.log(JSON.stringify(v), await p.evaluate(() => { const t = document.getElementById('t'); return getComputedStyle(t).transform; }));
}
await b.close();
