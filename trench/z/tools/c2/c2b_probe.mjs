// C2(b): which box a wheel moves, in Chromium. Hand-made page, no site.
// usage: node c2b_probe.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = `<!doctype html><style>body{margin:0;height:3000px}
#out{overflow:auto;width:200px;height:200px;position:absolute;left:0;top:0}
#out-in{height:600px}
#in{overflow:auto;width:150px;height:100px}
#in-in{height:300px;background:#ddd}
#hid{overflow:hidden;width:100px;height:100px;position:absolute;left:300px;top:0}
#hid-in{height:400px}
#con{overflow:auto;overscroll-behavior:contain;width:100px;height:100px;position:absolute;left:450px;top:0}
#con-in{height:150px}
#x{overflow-x:auto;overflow-y:hidden;width:100px;height:100px;position:absolute;left:600px;top:0}
#x-in{width:400px;height:100px}
#ab{overflow:auto;width:100px;height:100px;position:absolute;left:0;top:300px}
#ab-in{height:150px}
#ab-abs{position:absolute;left:300px;top:300px;width:50px;height:50px}
#short{overflow:auto;width:100px;height:100px;position:absolute;left:150px;top:300px}
</style><body><div id=out><div id=out-in><div id=in><div id=in-in></div></div></div></div>
<div id=hid><div id=hid-in></div></div>
<div id=con><div id=con-in></div></div>
<div id=x><div id=x-in></div></div>
<div id=ab><div id=ab-in></div></div><div id=ab-abs></div>
<div id=short>s</div></body>`;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.setContent(html);
const state = () => p.evaluate(`['in','out','hid','con','x','ab'].map(i=>i+'='+document.getElementById(i).scrollLeft+','+document.getElementById(i).scrollTop).join(' ')+' win='+scrollX+','+scrollY`);
const reset = () => p.evaluate(`['in','out','hid','con','x','ab'].forEach(i=>{var e=document.getElementById(i);e.scrollTop=0;e.scrollLeft=0});scrollTo(0,0)`);
async function wheel(name, x, y, dx, dy, setup) {
  await reset();
  if (setup) await p.evaluate(setup);
  await new Promise(r => setTimeout(r, 300));
  await p.mouse.move(x, y);
  await p.mouse.wheel(dx, dy);
  await new Promise(r => setTimeout(r, 400));
  console.log(name, await state());
}
console.log(b.version());
await p.evaluate(`window.ev=[];document.getElementById('in').addEventListener('scroll',e=>ev.push('in:'+e.bubbles));document.getElementById('out').addEventListener('scroll',e=>ev.push('out'));document.addEventListener('scroll',e=>ev.push('doc'))`);
await wheel('inner', 20, 20, 0, 50);
console.log('events', await p.evaluate(`ev.splice(0).join(' ')`));
await wheel('inner-past-end', 20, 20, 0, 500);
await wheel('inner-at-end', 20, 20, 0, 50, `document.getElementById('in').scrollTop=9999`);
await wheel('both-at-end', 20, 20, 0, 50, `document.getElementById('in').scrollTop=9999;document.getElementById('out').scrollTop=9999`);
await wheel('inner-up-at-top', 20, 20, 0, -50, `document.getElementById('out').scrollTop=30;window.scrollTo(0,0)`);
await wheel('outer-only', 170, 150, 0, 50);
await wheel('hidden', 320, 20, 0, 50);
await wheel('contain-at-end', 470, 20, 0, 50, `document.getElementById('con').scrollTop=9999`);
await wheel('x-only-dy', 620, 20, 0, 50);
await wheel('x-only-dx', 620, 20, 50, 0);
await wheel('diagonal-x-box', 620, 20, 50, 50);
await wheel('no-overflow', 170, 320, 0, 50);
await wheel('plain-page', 700, 500, 0, 50);
await b.close();
