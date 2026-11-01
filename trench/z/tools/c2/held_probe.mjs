// What else holds a fixed box to the page, Chromium 143: each wrapper in the flow with a fixed child, at window scroll 500. Plus a fixed box in an element scroller.
// node held_probe.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log(b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
const styles = ['', 'filter:blur(1px)', 'filter:none', 'backdrop-filter:blur(1px)', 'will-change:transform', 'will-change:opacity', 'will-change:filter', 'will-change:top', 'contain:paint', 'contain:layout', 'contain:strict', 'contain:content', 'contain:size', 'perspective:100px', 'transform-style:preserve-3d', 'opacity:0.5', 'isolation:isolate', 'translate:1px', 'scale:1', 'rotate:0deg', 'container-type:inline-size', 'content-visibility:auto', 'mix-blend-mode:multiply', 'clip-path:inset(0)'];
for (const s of styles) {
  await p.setContent(`<!doctype html><style>body{margin:0;height:3000px}</style><div style="height:100px"></div><div id=w style="width:200px;height:50px;${s}"><div id=f style="position:fixed;left:3px;top:4px;width:10px;height:10px"></div></div>`);
  await p.evaluate('window.scrollTo(0, 500)');
  console.log(JSON.stringify(s), await p.evaluate(() => { const r = document.getElementById('f').getBoundingClientRect(); return r.x + ' ' + r.y; }));
}
await p.setContent(`<!doctype html><style>body{margin:0;height:3000px}</style><div id=s style="width:200px;height:100px;overflow:auto"><div id=f style="position:fixed;left:3px;top:4px;width:10px;height:10px"><div id=k style="height:5px"></div></div><div style="height:800px"></div></div>`);
await p.evaluate(`window.scrollTo(0, 500); document.getElementById('s').scrollTop = 40`);
console.log('in scroller', await p.evaluate(() => ['f', 'k'].map((i) => { const r = document.getElementById(i).getBoundingClientRect(); return r.x + ' ' + r.y; }).join(' | ')));
await b.close();
