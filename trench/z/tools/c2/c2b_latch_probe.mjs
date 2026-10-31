// C2(b): does a run of wheels stay on the box it started on? Chromium. Hand-made page, no site.
// usage: node c2b_latch_probe.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = `<!doctype html><style>body{margin:0;height:3000px}
#top{height:100px}
#box{overflow:auto;width:200px;height:100px}
#box-in{height:150px;background:#ddd}
</style><body><div id=top></div><div id=box><div id=box-in></div></div></body>`;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.setContent(html);
const state = () => p.evaluate(`'box='+document.getElementById('box').scrollTop+' win='+scrollY`);
const reset = async () => { await p.evaluate(`document.getElementById('box').scrollTop=0;scrollTo(0,0)`); await new Promise(r => setTimeout(r, 900)); };
console.log(b.version());
// Over the box: past its end, then at once again.
await reset();
await p.mouse.move(20, 120);
await p.mouse.wheel(0, 500);
await p.mouse.wheel(0, 500);
await new Promise(r => setTimeout(r, 300));
console.log('box-then-again', await state());
await new Promise(r => setTimeout(r, 900));
await p.mouse.wheel(0, 50);
await new Promise(r => setTimeout(r, 300));
console.log('later-gesture', await state());
// Over the page above the box: the window moves, the box comes under the pointer.
await reset();
await p.mouse.move(20, 180);
await p.evaluate(`scrollTo(0,0)`);
await p.mouse.move(20, 250);
await p.mouse.wheel(0, 100);
await p.mouse.wheel(0, 100);
await new Promise(r => setTimeout(r, 300));
console.log('window-then-box-under', await state());
await b.close();
