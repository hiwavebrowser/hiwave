// C2(c) found-not-fixed: where an absolute box with no positioned ancestor goes, in Chromium,
// and the static scroller at y=0 the engine test uses to avoid that.
// usage: node c2c_abs_probe.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
console.log(b.version());
for (const [name, parent] of [['plain', ''], ['auto', 'overflow:auto;height:100px'], ['hidden', 'overflow:hidden;height:100px'], ['auto-tall', 'overflow:auto']]) {
  await p.setContent(`<!doctype html><style>body{margin:0;height:5000px}#a{position:absolute;left:10px;top:1800px;width:20px;height:20px}</style><body><div style=height:1000px></div><div id=p style='${parent}'><div style=height:300px></div><div id=a></div></div></body>`);
  console.log(name, await p.evaluate(`document.getElementById('a').getBoundingClientRect().top+' '+document.getElementById('p').getBoundingClientRect().top`));
}
await p.setContent(`<!doctype html><style>body{margin:0;height:3000px}#s{overflow:auto;width:200px;height:100px}#a{position:absolute;left:10px;top:1800px;width:20px;height:20px}</style><body><div id=s><div style=height:300px></div><div id=a></div></div></body>`);
await p.evaluate(`document.getElementById('a').scrollIntoView()`);
console.log('escape-at-top', await p.evaluate(`document.getElementById('s').scrollTop+' win='+scrollX+','+scrollY`));
await b.close();
