// #851 R1 finding 1: what a click over a stuck header hits under a fixed box, by the stacking contexts on each path. Chromium 143, window scroll 500.
// node sticky_ctx_probe.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log(b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
const hdr = (z) => `<div id=app_inner style="height:400px"></div><div id=h style="position:sticky;top:0;width:300px;height:30px;z-index:${z}"></div>`;
const wrap = (s, inner) => `<div id=w style="height:2000px;${s}">${inner}</div>`;
const m = (z) => `<div id=m style="position:fixed;left:0;top:0;width:400px;height:40px;z-index:${z}"></div>`;
const cases = [
  ['no wrapper, header over modal', wrap('', hdr(10)) + m(5)],
  ['relative z0, modal after', wrap('position:relative;z-index:0', hdr(10)) + m(5)],
  ['relative z0, modal before', m(5) + wrap('position:relative;z-index:0', hdr(10))],
  ['relative z1, header 100, bar 50', wrap('position:relative;z-index:1', hdr(100)) + m(50)],
  ['relative z60, header 1, bar 50', wrap('position:relative;z-index:60', hdr(1)) + m(50)],
  ['relative z5, modal z5 after', wrap('position:relative;z-index:5', hdr(10)) + m(5)],
  ['relative z5, modal z5 before', m(5) + wrap('position:relative;z-index:5', hdr(10))],
  ['relative z auto', wrap('position:relative', hdr(10)) + m(5)],
  ['static with z-index', wrap('z-index:0', hdr(10)) + m(5)],
  ['absolute z0', wrap('position:absolute;left:0;top:0;width:100%;z-index:0', hdr(10)) + m(5)],
  ['transform', wrap('transform:translateX(0)', hdr(10)) + m(5)],
  ['opacity', wrap('opacity:.9', hdr(10)) + m(5)],
  ['filter', wrap('filter:blur(0px)', hdr(10)) + m(5)],
  ['isolation', wrap('isolation:isolate', hdr(10)) + m(5)],
  ['will-change transform', wrap('will-change:transform', hdr(10)) + m(5)],
  ['will-change opacity', wrap('will-change:opacity', hdr(10)) + m(5)],
  ['contain paint', wrap('contain:paint', hdr(10)) + m(5)],
  ['mix-blend', wrap('mix-blend-mode:multiply', hdr(10)) + m(5)],
  ['flex item z0', `<div style="display:flex">${wrap('flex:1;z-index:0', hdr(10))}</div>` + m(5)],
  ['flex item z auto', `<div style="display:flex">${wrap('flex:1', hdr(10))}</div>` + m(5)],
  ['nested outer 20 inner 1', wrap('position:relative;z-index:20', wrap('position:relative;z-index:1', hdr(1))) + m(5)],
  ['nested outer 1 inner 20', wrap('position:relative;z-index:1', wrap('position:relative;z-index:20', hdr(10))) + m(5)],
  ['shared wrapper, header 10 modal 5', wrap('position:relative;z-index:0', hdr(10) + m(5))],
  ['shared wrapper, header 1 modal 5', wrap('position:relative;z-index:0', hdr(1) + m(5))],
  ['modal wrapper 20, app 10', wrap('position:relative;z-index:10', hdr(1)) + `<div style="position:relative;z-index:20">${m(1)}</div>`],
  ['modal wrapper 1, app 10', wrap('position:relative;z-index:10', hdr(1)) + `<div style="position:relative;z-index:1">${m(50)}</div>`],
  ['app negative, modal 0', wrap('position:relative;z-index:-1', hdr(10)) + m(0)],
  ...['will-change:clip-path', 'will-change:mask', 'will-change:isolation', 'will-change:mix-blend-mode', 'will-change:z-index', 'will-change:position', 'will-change:top', 'clip-path:inset(0)', 'mask-image:linear-gradient(#000,#000)', 'backdrop-filter:blur(0px)', 'perspective:100px', 'transform-style:preserve-3d', 'translate:0px', 'scale:1', 'rotate:0deg', 'container-type:size', 'opacity:1', 'transform:none', 'isolation:auto', 'mix-blend-mode:normal', 'contain:layout', 'contain:style', 'contain:size'].map((s) => [s, wrap(s, hdr(10)) + m(5)]),
];
for (const [name, body] of cases) {
  await p.setContent(`<!doctype html><style>body{margin:0;height:3000px}</style>${body}<div style="height:3000px"></div>`);
  await p.evaluate('window.scrollTo(0, 500)');
  console.log(JSON.stringify(name), await p.evaluate(() => { const e = document.elementFromPoint(10, 10); return (e && (e.id || e.tagName)) + ' ' + document.getElementById('h').getBoundingClientRect().y; }));
}
await b.close();
