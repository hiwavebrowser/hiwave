// C2(d): where position: sticky puts a box, in Chromium. Hand-made page, no site.
// usage: node c2d_probe.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = `<!doctype html><style>body{margin:0;height:3000px}
.sc{overflow:auto;width:200px;height:100px;position:absolute;top:0}
.tall{height:600px}
.gap{height:50px}
.st{position:sticky;height:20px;width:50px}
#a-s{left:0}#a{top:0}
#b-s{left:210px}#b{top:10px;margin-bottom:5px}
#c-s{left:420px}#c{bottom:0}
#d-s{left:630px}#d{top:10%}
#e-s{left:840px}#e-cb{height:100px;margin-top:50px}#e{top:0;margin-bottom:6px}
#f-s{left:1050px}#f{top:5px;bottom:5px;height:200px}
#g-s{left:1260px;height:100px;width:100px}#g-wide{width:800px;height:20px}#g{left:7px;top:auto}
#h-s{left:1470px}#h{top:0}#h-abs{position:absolute;left:3px;top:4px;width:5px;height:5px}#h-kid{height:5px}
#i-out{left:1680px}#i-in{height:50px;overflow:hidden;margin-top:40px}#i{top:0}
#j-s{left:1890px;overflow:clip}#j{top:0}
#k{position:sticky;top:30px;height:20px;width:40px;margin-top:400px;margin-left:2100px}
#k-kid{height:5px;width:5px}
#l-cb{margin-left:2200px;height:300px;margin-top:100px}
#l{position:sticky;top:15px;height:10px;width:10px}
#m-s{left:2400px}#m{top:0;right:0;width:10px}
#o-s{left:2600px}#o1{top:0;height:60px;width:60px}#o2{top:5px;height:5px;width:5px}#o-gap{height:30px}
#p-s{left:2800px}#p{top:0;display:inline-block}
</style><body>
<div class=sc id=a-s><div class=gap></div><div class=st id=a></div><div class=tall></div></div>
<div class=sc id=b-s><div class=gap></div><div class=st id=b></div><div class=tall></div></div>
<div class=sc id=c-s><div class=tall></div><div class=st id=c></div><div class=gap></div></div>
<div class=sc id=d-s><div class=gap></div><div class=st id=d></div><div class=tall></div></div>
<div class=sc id=e-s><div id=e-cb><div class=st id=e></div></div><div class=tall></div></div>
<div class=sc id=f-s><div class=gap></div><div class=st id=f></div><div class=tall></div></div>
<div class=sc id=g-s><div id=g-wide><div class=st id=g></div></div></div>
<div class=sc id=h-s><div class=gap></div><div class=st id=h><div id=h-kid></div><div id=h-abs></div></div><div class=tall></div></div>
<div class=sc id=i-out><div id=i-in><div class=st id=i></div><div class=tall></div></div><div class=tall></div></div>
<div class=sc id=j-s><div class=gap></div><div class=st id=j></div><div class=tall></div></div>
<div class=sc id=m-s><div class=gap></div><div class=st id=m></div><div class=tall></div></div>
<div class=sc id=o-s><div class=gap></div><div class=st id=o1><div id=o-gap></div><div class=st id=o2></div></div><div class=tall></div></div>
<div class=sc id=p-s><div class=gap></div><span class=st id=p>x</span><div class=tall></div></div>
<div id=k><div id=k-kid></div></div>
<div id=l-cb><div id=l></div></div>
</body>`;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.route('http://probe.test/**', r => r.fulfill({ contentType: 'text/html', body: html }));
await p.goto('http://probe.test/page');
const read = (ids) => p.evaluate((ids) => ids.map(id => {
  const e = document.getElementById(id), r = e.getBoundingClientRect();
  return `${id} ${r.x},${r.y} ${r.width}x${r.height} offsetTop=${e.offsetTop}`;
}), ids);
const out = {};
for (const [sc, target, offs, axis] of [
  ['a-s', ['a'], [0, 30, 50, 70, 200], 'Top'],
  ['b-s', ['b'], [0, 30, 45, 70], 'Top'],
  ['c-s', ['c'], [0, 400, 545, 570], 'Top'],
  ['d-s', ['d'], [0, 45, 100], 'Top'],
  ['e-s', ['e'], [0, 50, 100, 124, 130, 160, 200], 'Top'],
  ['f-s', ['f'], [0, 50, 200, 400], 'Top'],
  ['g-s', ['g'], [0, 30, 100, 700], 'Left'],
  ['h-s', ['h', 'h-kid', 'h-abs'], [0, 100], 'Top'],
  ['i-out', ['i', 'i-in'], [0, 40, 60, 80], 'Top'],
  ['j-s', ['j'], [0, 100], 'Top'],
  ['m-s', ['m'], [0, 100], 'Top'],
  ['o-s', ['o1', 'o2'], [0, 50, 100], 'Top'],
  ['p-s', ['p'], [0, 100], 'Top'],
]) {
  out[sc] = {};
  for (const o of offs) {
    await p.evaluate(([sc, o, a]) => { document.getElementById(sc)['scroll' + a] = o; }, [sc, o, axis]);
    out[sc][o] = await read(target);
  }
}
// inner box of i: scroll the inner one too
await p.evaluate(() => { document.getElementById('i-out').scrollTop = 0; document.getElementById('i-in').scrollTop = 30; });
out.iInner30 = await read(['i']);
// The window: a free sticky, its child, and one limited by its parent. Then hit tests.
out.window = {};
for (const y of [0, 100, 380, 500, 1000]) {
  await p.evaluate(y => window.scrollTo(0, y), y);
  out.window[y] = await read(['k', 'k-kid', 'l']);
}
await p.evaluate(() => { window.scrollTo(0, 500); document.getElementById('a-s').scrollTop = 100; });
out.hits = await p.evaluate(() => {
  const k = document.getElementById('k').getBoundingClientRect();
  const a = document.getElementById('a').getBoundingClientRect();
  const at = (x, y) => (document.elementFromPoint(x, y) || {}).id;
  return { k: [k.x, k.y], a: [a.x, a.y], hitK: at(k.x + 20, k.y + 15), hitA: at(a.x + 5, a.y + 5) };
});
await p.evaluate(() => window.scrollTo(0, 0));
out.hitA0 = await p.evaluate(() => { const a = document.getElementById('a').getBoundingClientRect(); return [a.x, a.y, (document.elementFromPoint(a.x + 5, a.y + 5) || {}).id]; });
console.log(JSON.stringify(out, null, 0).replace(/\],/g, '],\n'));
await b.close();
