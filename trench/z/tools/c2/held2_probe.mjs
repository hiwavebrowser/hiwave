// will-change and contain values that hold a fixed box, Chromium 143, at window scroll 500 (held reads y -396, not 4). Then the same wrappers inside a scroller at scrollTop 40.
// node held2_probe.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log(b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
const styles = ['will-change:auto', 'will-change:transform', 'will-change:TRANSFORM', 'will-change:top, transform', 'will-change:top,transform', 'will-change:translate', 'will-change:scale', 'will-change:rotate', 'will-change:perspective', 'will-change:filter', 'will-change:backdrop-filter', 'will-change:contain', 'will-change:position', 'will-change:transform-style', 'will-change:scroll-position', 'will-change:contents', 'will-change:-webkit-transform', 'will-change:transform;will-change:auto', 'will-change:top;will-change:bogus,',
  'contain:none', 'contain:paint', 'contain:PAINT', 'contain:layout', 'contain:strict', 'contain:content', 'contain:size', 'contain:style', 'contain:inline-size', 'contain:size style', 'contain:layout paint', 'contain:paint;contain:none', 'contain:paint;contain:bogus', 'contain:paint paint',
  'transform:translate(0)', 'transform:none', 'transform:scale(1)'];
for (const s of styles) {
  await p.setContent(`<!doctype html><style>body{margin:0;height:3000px}</style><div style="height:100px"></div><div id=w style="width:200px;height:50px;${s}"><div id=f style="position:fixed;left:3px;top:4px;width:10px;height:10px"></div></div>`);
  await p.evaluate('window.scrollTo(0, 500)');
  console.log(JSON.stringify(s), await p.evaluate(() => { const r = document.getElementById('f').getBoundingClientRect(); return r.x + ' ' + r.y; }));
}
for (const s of ['', 'filter:blur(1px)', 'will-change:transform', 'contain:paint', 'transform:translateX(0)']) {
  await p.setContent(`<!doctype html><style>body{margin:0}</style><div id=s style="width:200px;height:100px;overflow:auto"><div id=w style="width:100px;height:20px;${s}"><div id=f style="position:fixed;left:3px;top:4px;width:10px;height:10px"></div><div id=a style="position:absolute;left:5px;top:6px;width:10px;height:10px"></div></div><div style="height:800px"></div></div>`);
  await p.evaluate(`document.getElementById('s').scrollTop = 40`);
  console.log('scroller ' + JSON.stringify(s), await p.evaluate(() => ['f', 'a'].map((i) => { const r = document.getElementById(i).getBoundingClientRect(); return r.x + ' ' + r.y; }).join(' | ')));
}
await b.close();
