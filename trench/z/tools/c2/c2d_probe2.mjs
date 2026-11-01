// C2(d), second page: padding on the scroller and the containing block, sticky under
// a fixed box, in an absolute box that skips a static scroller, in a transform. No site.
// usage: node c2d_probe2.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = `<!doctype html><style>body{margin:0;height:3000px}
.sc{overflow:auto;width:200px;height:100px;position:absolute;top:0}
.tall{height:600px}.gap{height:50px}
.st{position:sticky;top:0;height:20px;width:50px}
#a-s{left:0;padding:11px;border:3px solid #000}
#b-s{left:300px}#b-cb{padding:9px 0 13px;height:100px;margin-top:50px}
#fx{position:fixed;left:600px;top:40px;width:100px;height:100px}#c{top:60px}
#d-s{left:800px;position:absolute}#d-st{overflow:auto;width:200px;height:100px}
#d-abs{position:absolute;left:0;top:500px;width:60px;height:60px}#d{top:10px;height:5px;width:5px}
#e-tr{transform:translateY(100px);margin-left:1100px;margin-top:400px;height:400px}
#e{top:10px}
#g-cb{margin-left:1300px;height:500px}
#g{top:10px}#g-fx{position:fixed;left:1400px;top:7px;width:5px;height:5px}
</style><body>
<div class=sc id=a-s><div class=gap></div><div class=st id=a></div><div class=tall></div></div>
<div class=sc id=b-s><div id=b-cb><div class=st id=b></div></div><div class=tall></div></div>
<div id=fx><div class=st id=c></div></div>
<div id=d-s><div id=d-st><div id=d-abs><div class=st id=d></div></div><div class=tall></div></div></div>
<div id=e-tr><div class=st id=e></div></div>
<div id=g-cb><div class=st id=g><div id=g-fx></div></div></div>
</body>`;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.route('http://probe.test/**', r => r.fulfill({ contentType: 'text/html', body: html }));
await p.goto('http://probe.test/page');
const read = (ids) => p.evaluate((ids) => ids.map(id => {
  const r = document.getElementById(id).getBoundingClientRect();
  return `${id} ${r.x},${r.y}`;
}), ids);
const out = {};
for (const [sc, target, offs] of [
  ['a-s', ['a'], [0, 30, 45, 100]],
  ['b-s', ['b'], [0, 50, 59, 100, 200]],
  ['d-st', ['d'], [0, 400]],
]) {
  out[sc] = {};
  for (const o of offs) {
    await p.evaluate(([s, o]) => { document.getElementById(s).scrollTop = o; }, [sc, o]);
    out[sc][o] = await read(target);
  }
}
out.window = {};
for (const y of [0, 300, 450, 700, 1200]) {
  await p.evaluate(y => window.scrollTo(0, y), y);
  out.window[y] = await read(['c', 'd', 'e', 'g', 'g-fx']);
}
console.log(JSON.stringify(out, null, 0).replace(/\],/g, '],\n'));
await b.close();
