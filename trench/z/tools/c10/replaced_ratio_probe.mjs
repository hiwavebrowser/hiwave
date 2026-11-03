// C10 (e) second slice: replaced boxes (img, canvas) with a natural ratio inside flex and grid. Chromium.
// node replaced_ratio_probe.mjs <dir with node_modules/playwright>; prints JSON lines [name, body, want].
// want = "<width>x<height> @x,y" of #t's border box (getBoundingClientRect, rounded to 0.01).
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log('// ' + b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
// A 40x20 red PNG (natural ratio 2:1), no fonts anywhere.
const IMG = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAUCAIAAABwJOjsAAAAI0lEQVR42u3NsQ0AAAjAoP7/tJ7hIAk7TZ1ILBaLxWKx+E+8ffodDqIehz0AAAAASUVORK5CYII=';
const flex = (inner, s = '') => `<div id=c style="display:flex;width:400px;${s}">${inner}</div>`;
const grid = (inner, s = '') => `<div id=c style="display:grid;width:400px;${s}">${inner}</div>`;
const I = (s, extra = '') => `<img id=t src="${IMG}" ${extra}style="display:block;${s}">`;
const C = (s, w = 300, h = 150) => `<canvas id=t width=${w} height=${h} style="display:block;${s}"></canvas>`;
const two = 'grid-template-columns:1fr 1fr';
const cases = [
  // block-flow controls
  ['img block: none', I('')],
  ['img block: width 50%', I('width:50%')],
  ['img block: width 100%, height auto attrs', `<div style="width:400px">${I('width:100%;height:auto', 'width=40 height=20 ')}</div>`],
  ['canvas block: none', C('')],
  // grid, img
  ['img grid: one column', grid(I(''))],
  ['img grid: one column, width', grid(I('width:100px'))],
  ['img grid: one column, height', grid(I('height:60px'))],
  ['img grid: two columns', grid(I('') + '<div></div>', two)],
  ['img grid: two columns width 100%', grid(I('width:100%') + '<div></div>', two)],
  ['img grid: two columns width 50%', grid(I('width:50%') + '<div></div>', two)],
  ['img grid: two columns max-width 100%', grid(I('max-width:100%') + '<div></div>', two)],
  ['img grid: fixed column 300px', grid(I(''), 'grid-template-columns:300px')],
  ['img grid: justify start', grid(I(''), 'justify-items:start')],
  ['img grid: align start', grid(I(''), 'align-items:start')],
  ['img grid: justify start, width', grid(I('width:100px'), 'justify-items:start')],
  ['img grid: ratio 1, width 100%', grid(I('width:100%;aspect-ratio:1') + '<div></div>', two)],
  ['img grid: width 100%, height auto attrs', grid(I('width:100%;height:auto', 'width=40 height=20 ') + '<div></div>', two)],
  ['img grid: fixed row 100px', grid(I(''), 'grid-template-rows:100px;grid-template-columns:300px')],
  ['img grid: three columns gap', grid(I('width:100%') + '<div></div><div></div>', 'grid-template-columns:repeat(3,1fr);gap:20px')],
  // grid, canvas
  ['canvas grid: one column', grid(C(''))],
  ['canvas grid: width 100%', grid(C('width:100%') + '<div></div>', two)],
  ['canvas grid: justify start', grid(C(''), 'justify-items:start')],
  // flex, img
  ['img flex row: none', flex(I(''))],
  ['img flex row: align start', flex(I(''), 'align-items:flex-start')],
  ['img flex row: flex 1, align start', flex(I('flex:1;min-width:0'), 'align-items:flex-start')],
  ['img flex row: height, align start', flex(I('height:60px'), 'align-items:flex-start')],
  ['img flex column: width', flex(I('width:100px'), 'flex-direction:column')],
  ['img flex column: stretch', flex(I(''), 'flex-direction:column')],
  ['img flex column: align start', flex(I(''), 'flex-direction:column;align-items:flex-start')],
  ['img flex column: width 100%', flex(I('width:100%'), 'flex-direction:column')],
  // flex, canvas
  ['canvas flex row: width', flex(C('width:100px'), 'align-items:flex-start')],
  ['canvas flex column: width', flex(C('width:100px'), 'flex-direction:column')],
  ['canvas flex column: stretch', flex(C(''), 'flex-direction:column')],
  // card patterns
  ['card: grid column, img 100%', grid(`<div>${I('width:100%')}</div><div></div>`, two)],
  ['card: grid column, img 100% ratio 16/9 cover', grid(`<div>${I('width:100%;aspect-ratio:16/9;object-fit:cover')}</div><div></div>`, two)],
  ['card: flex 1, img 100%', flex(`<div style="flex:1">${I('width:100%')}</div><div style="flex:1"></div>`)],
  ['card: flex 1, img 100% ratio 16/9', flex(`<div style="flex:1">${I('width:100%;aspect-ratio:16/9')}</div><div style="flex:1"></div>`)],
  // #871 R1 (6612792527) finding 1: attribute-sized image with max-width:100% in a card column
  ['card: grid column, img attrs 800x400 max-width 100%', grid(`<div>${I('max-width:100%', 'width=800 height=400 ')}</div><div></div>`, two)],
  ['card: grid column, img attrs 800x400 max-width 100% height auto', grid(`<div>${I('max-width:100%;height:auto', 'width=800 height=400 ')}</div><div></div>`, two)],
  ['card: three columns, img attrs 800x400 max-width 100%', grid(`<div>${I('max-width:100%', 'width=800 height=400 ')}</div><div></div><div></div>`, 'grid-template-columns:repeat(3,1fr)')],
  ['card: three columns gap, img attrs 800x400 max-width 100% height auto', grid(`<div>${I('max-width:100%;height:auto', 'width=800 height=400 ')}</div><div></div><div></div>`, 'grid-template-columns:repeat(3,1fr);gap:20px')],
  ['img grid: two columns, attrs 800x400 max-width 100%',grid(I('max-width:100%', 'width=800 height=400 ') + '<div></div>', two)],
  ['img grid: two columns, attrs 800x400 width 100%', grid(I('width:100%', 'width=800 height=400 ') + '<div></div>', two)],
  // finding 2: explicit stretch on the item
  ['img grid: self stretch both, row 100px', grid(I('justify-self:stretch;align-self:stretch'), 'grid-template-rows:100px')],
  ['img grid: justify-self stretch', grid(I('justify-self:stretch'))],
  ['img grid: align-self stretch, row 100px', grid(I('align-self:stretch'), 'grid-template-rows:100px')],
  // finding 3: percentage image in an auto / max-content column
  ['img grid: auto column, width 100%', grid(I('width:100%') + '<div></div>', 'grid-template-columns:auto 1fr')],
  ['img grid: max-content column, width 100%', grid(I('width:100%') + '<div></div>', 'grid-template-columns:max-content 1fr')],
  ['img grid: auto column, max-width 100%', grid(I('max-width:100%') + '<div></div>', 'grid-template-columns:auto 1fr')],
  ['img grid: min-content column, width 100%', grid(I('width:100%') + '<div></div>', 'grid-template-columns:min-content 1fr')],
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
