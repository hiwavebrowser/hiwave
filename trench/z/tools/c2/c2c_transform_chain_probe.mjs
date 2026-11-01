// C2(c) after #852: a transformed box that does not scroll is not a scroller of scrollIntoView.
// usage: node c2c_transform_chain_probe.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
export const html = `<!doctype html><style>body{margin:0;height:3000px}#sp0{height:1000px}#s{overflow:auto;width:200px;height:100px}#s-gap{height:300px}#tw{transform:translateY(50px);height:200px}#tw-gap{height:100px}#tw-t{height:20px}#s-end{height:100px}#tb{transform:translateX(5px)}#tb-gap{height:500px}#tb-t{height:20px}</style><body><div id=sp0></div><div id=s><div id=s-gap></div><div id=tw><div id=tw-gap></div><div id=tw-t></div></div><div id=s-end></div></div><div id=tb><div id=tb-gap></div><div id=tb-t></div></div></body>`;
const b = await chromium.launch();
console.log(b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.route('http://probe.test/**', r => r.fulfill({ contentType: 'text/html', body: html }));
const S = ['s', 'tw', 'tb'];
const state = () => p.evaluate(`${JSON.stringify(S)}.map(i=>{var e=document.getElementById(i);return e.scrollLeft||e.scrollTop?i+'='+e.scrollLeft+','+e.scrollTop:''}).filter(Boolean).join(' ')+' win='+scrollX+','+scrollY+' sh='+['s','tw','tb'].map(i=>document.getElementById(i).scrollHeight).join(',')`);
for (const [name, js] of [['tw-t', `document.getElementById('tw-t').scrollIntoView()`], ['tb-t', `document.getElementById('tb-t').scrollIntoView()`], ['tw-t nearest', `document.getElementById('tw-t').scrollIntoView({block:'nearest'})`]]) {
  await p.goto('http://probe.test/page');
  await p.evaluate(js);
  await new Promise(r => setTimeout(r, 200));
  console.log(name.padEnd(14), await state());
}
await b.close();
