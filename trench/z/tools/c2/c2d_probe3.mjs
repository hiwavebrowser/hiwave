// C2(d), third page: hits inside a window-sized page, and a sticky box under an absolute
// box that skips a static scroller, placed with an explicit top. No site.
// usage: node c2d_probe3.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = `<!doctype html><style>body{margin:0;height:3000px}
#s{overflow:auto;width:200px;height:100px;position:absolute;left:0;top:0}
#gap{height:50px}#st{position:sticky;top:0;height:20px;width:50px}#fill{height:600px}
#w{position:sticky;top:30px;height:20px;width:40px;margin-top:400px;margin-left:300px}
#wk{height:5px;width:5px}
#ws{position:sticky;top:60px;height:20px;width:40px;margin-left:400px}
#wf{position:fixed;left:500px;top:7px;width:20px;height:20px}
#ds{position:absolute;left:600px;top:0;width:100px;height:100px}
#dst{overflow:auto;width:100px;height:100px}
#dab{position:absolute;left:0;top:500px;width:60px;height:60px}
#d{position:sticky;top:10px;height:5px;width:5px}
#dtall{height:600px}
</style><body>
<div id=s><div id=gap></div><div id=st></div><div id=fill></div></div>
<div id=ds><div id=dst><div id=dab><div id=d></div></div><div id=dtall></div></div></div>
<div id=w><div id=wk></div></div>
<div id=ws><div id=wf></div></div>
</body>`;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.route('http://probe.test/**', r => r.fulfill({ contentType: 'text/html', body: html }));
await p.goto('http://probe.test/page');
const state = () => p.evaluate(() => {
  const at = (x, y) => (document.elementFromPoint(x, y) || {}).id;
  const r = id => { const q = document.getElementById(id).getBoundingClientRect(); return q.x + ',' + q.y; };
  return { st: r('st'), w: r('w'), wk: r('wk'), ws: r('ws'), wf: r('wf'), d: r('d'),
    hits: [at(5, 5), at(5, 30), at(5, 55), at(320, 40), at(320, 405), at(420, 70), at(505, 10)].join(' ') };
});
const out = {};
out.top = await state();
await p.evaluate(() => { document.getElementById('s').scrollTop = 100; });
out.box100 = await state();
await p.evaluate(() => { document.getElementById('dst').scrollTop = 300; });
out.dst300 = await state();
await p.evaluate(() => window.scrollTo(0, 500));
out.win500 = await state();
await p.evaluate(() => window.scrollTo(0, 2000));
out.win2000 = await state();
console.log(JSON.stringify(out, null, 0).replace(/\},/g, '},\n'));
await b.close();
