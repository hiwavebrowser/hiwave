// C10 (e): aspect-ratio on replaced and non-replaced boxes inside flex and grid. Chromium.
// node aspect_ratio_probe.mjs <dir with node_modules/playwright>; prints JSON lines [name, body, want].
// want = "<width>x<height>" of #t's border box (getBoundingClientRect, rounded to 0.01), plus " @x,y" of its origin.
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log('// ' + b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
// A 40x20 red PNG (intrinsic ratio 2:1), no fonts anywhere.
const IMG = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAUCAIAAABwJOjsAAAAI0lEQVR42u3NsQ0AAAjAoP7/tJ7hIAk7TZ1ILBaLxWKx+E+8ffodDqIehz0AAAAASUVORK5CYII=';
const flex = (inner, s = '') => `<div id=c style="display:flex;width:400px;${s}">${inner}</div>`;
const grid = (inner, s = '') => `<div id=c style="display:grid;width:400px;${s}">${inner}</div>`;
const D = (s) => `<div id=t style="${s}"></div>`;
const I = (s) => `<img id=t src="${IMG}" style="display:block;${s}">`;
const C = (s) => `<canvas id=t width=300 height=150 style="display:block;${s}"></canvas>`;
const cases = [
  // control: block flow
  ['block: width, ratio 2/1', D('width:200px;aspect-ratio:2/1')],
  ['block: auto width, ratio 4/1', D('aspect-ratio:4/1')],
  ['block: height, ratio 2/1, auto width', `<div style="width:400px">${D('height:50px;aspect-ratio:2/1;float:left')}</div>`],
  // flex row
  ['flex row: width, ratio 2/1', flex(D('width:200px;aspect-ratio:2/1'))],
  ['flex row: width, ratio 2/1, align start', flex(D('width:200px;aspect-ratio:2/1'), 'align-items:flex-start')],
  ['flex row: width, ratio 2/1, definite container height', flex(D('width:200px;aspect-ratio:2/1'), 'height:300px')],
  ['flex row: width, ratio 2/1, container height, align start', flex(D('width:200px;aspect-ratio:2/1'), 'height:300px;align-items:flex-start')],
  ['flex row: flex-basis, ratio 2/1', flex(D('flex:0 0 120px;aspect-ratio:2/1'), 'align-items:flex-start')],
  ['flex row: flex 1, ratio 4/1', flex(D('flex:1;aspect-ratio:4/1'), 'align-items:flex-start')],
  ['flex row: two flex 1, ratio 1', flex(D('flex:1;aspect-ratio:1') + '<div style="flex:1;height:10px"></div>', 'align-items:flex-start')],
  ['flex row: height, ratio 2/1, auto width', flex(D('height:50px;aspect-ratio:2/1'))],
  ['flex row: height, ratio 2/1, align start', flex(D('height:50px;aspect-ratio:2/1'), 'align-items:flex-start')],
  ['flex row: width %, ratio 16/9', flex(D('width:50%;aspect-ratio:16/9'), 'align-items:flex-start')],
  ['flex row: ratio with sibling', flex(D('width:100px;aspect-ratio:1') + '<div style="width:50px;height:20px"></div>')],
  ['flex row: ratio 1, align center', flex(D('width:80px;aspect-ratio:1'), 'height:200px;align-items:center')],
  ['flex row: auto ratio 3/1 no size, align start', flex(D('aspect-ratio:3/1;min-width:0'), 'align-items:flex-start')],
  // flex column
  ['flex column: width, ratio 2/1', flex(D('width:200px;aspect-ratio:2/1'), 'flex-direction:column')],
  ['flex column: stretch, ratio 4/1', flex(D('aspect-ratio:4/1'), 'flex-direction:column')],
  ['flex column: align start, width, ratio 4/1', flex(D('width:100px;aspect-ratio:4/1'), 'flex-direction:column;align-items:flex-start')],
  ['flex column: height, ratio 2/1, align start', flex(D('height:50px;aspect-ratio:2/1'), 'flex-direction:column;align-items:flex-start')],
  ['flex column: ratio 1, sibling', flex(D('aspect-ratio:2/1') + '<div style="height:20px"></div>', 'flex-direction:column')],
  // grid
  ['grid: ratio 2/1, one column', grid(D('aspect-ratio:2/1'))],
  ['grid: ratio 2/1, two columns', grid(D('aspect-ratio:2/1') + '<div></div>', 'grid-template-columns:1fr 1fr')],
  ['grid: ratio 1, three columns, gap', grid(D('aspect-ratio:1') + '<div></div><div></div>', 'grid-template-columns:repeat(3,1fr);gap:10px')],
  ['grid: ratio 2/1, justify start, width', grid(D('width:100px;aspect-ratio:2/1'), 'justify-items:start')],
  ['grid: ratio 2/1, align start', grid(D('aspect-ratio:2/1'), 'align-items:start')],
  ['grid: ratio 1, fixed rows', grid(D('aspect-ratio:1'), 'grid-template-rows:100px;grid-template-columns:300px')],
  ['grid: ratio 1, fixed rows, align start', grid(D('aspect-ratio:1'), 'grid-template-rows:100px;grid-template-columns:300px;align-items:start')],
  ['grid: ratio 16/9, auto-fill minmax', grid(D('aspect-ratio:16/9') + '<div></div><div></div>', 'grid-template-columns:repeat(auto-fill,minmax(120px,1fr))')],
  // replaced: img with intrinsic 40x20
  ['img block: width only', I('width:100px')],
  ['img block: aspect-ratio 1 overrides', I('width:100px;aspect-ratio:1')],
  ['img block: aspect-ratio auto 1', I('width:100px;aspect-ratio:auto 1')],
  ['img flex row: width', flex(I('width:100px'))],
  ['img flex row: width, align start', flex(I('width:100px'), 'align-items:flex-start')],
  ['img flex row: ratio 1, align start', flex(I('width:100px;aspect-ratio:1'), 'align-items:flex-start')],
  ['img flex row: flex 1, align start', flex(I('flex:1;min-width:0'), 'align-items:flex-start')],
  ['img flex row: height, align start', flex(I('height:60px'), 'align-items:flex-start')],
  ['img flex column: width', flex(I('width:100px'), 'flex-direction:column')],
  ['img flex column: stretch', flex(I(''), 'flex-direction:column')],
  ['img flex column: align start', flex(I(''), 'flex-direction:column;align-items:flex-start')],
  ['img grid: one column', grid(I(''))],
  ['img grid: two columns width 100%', grid(I('width:100%') + '<div></div>', 'grid-template-columns:1fr 1fr')],
  ['img grid: justify start', grid(I(''), 'justify-items:start')],
  ['img grid: ratio 1, width 100%', grid(I('width:100%;aspect-ratio:1') + '<div></div>', 'grid-template-columns:1fr 1fr')],
  // replaced: canvas 300x150
  ['canvas flex row: width', flex(C('width:100px'), 'align-items:flex-start')],
  ['canvas flex row: ratio 1', flex(C('width:100px;aspect-ratio:1'), 'align-items:flex-start')],
  ['canvas grid: width 100%', grid(C('width:100%') + '<div></div>', 'grid-template-columns:1fr 1fr')],
  // object-fit wrapper pattern (cards)
  ['card: grid column, img 100% ratio 16/9 cover', grid(`<div>${I('width:100%;aspect-ratio:16/9;object-fit:cover')}</div><div></div>`, 'grid-template-columns:1fr 1fr')],
  ['card: flex item, img 100% ratio 16/9', flex(`<div style="flex:1">${I('width:100%;aspect-ratio:16/9')}</div><div style="flex:1"></div>`)],
  ['card: div ratio wrapper in flex 1', flex(`<div style="flex:1"><div id=t style="aspect-ratio:16/9"></div></div><div style="flex:1"></div>`)],
];
const out = [];
for (const [name, body] of cases) {
  await p.setContent(`<!doctype html><style>body{margin:0}</style><body>${body}`);
  await p.waitForFunction(() => [...document.images].every((i) => i.complete));
  const got = await p.evaluate(() => {
    const e = document.getElementById('t');
    const r = e.getBoundingClientRect();
    const f = (v) => String(Math.round(v * 100) / 100);
    return `${f(r.width)}x${f(r.height)} @${f(r.left)},${f(r.top)}`;
  });
  out.push(JSON.stringify([name, body, got]));
}
console.log(out.join('\n'));
await b.close();
