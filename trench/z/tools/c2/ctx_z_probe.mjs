// #851 R1 delta findings 1-3: a z-index that does not apply, -webkit-backdrop-filter, and the arms still missing. Chromium 143, window scroll 500.
// node ctx_z_probe.mjs <dir with node_modules/playwright>
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
  ...['opacity:.9;z-index:50', 'isolation:isolate;z-index:50', 'transform:translateX(0);z-index:50', 'filter:blur(0px);z-index:50', 'contain:paint;z-index:50', 'will-change:opacity;z-index:50', 'mix-blend-mode:multiply;z-index:50', 'position:relative;opacity:.9;z-index:50', 'position:relative;isolation:isolate;z-index:50', 'position:relative;opacity:.9;z-index:1', 'opacity:.9;z-index:-1', 'position:relative;opacity:.9;z-index:-1', 'opacity:.9;z-index:0'].map((s) => [s, wrap(s, hdr(10)) + m(5)]),
  ['flex item opacity z50', `<div style="display:flex">${wrap('flex:1;opacity:.9;z-index:50', hdr(10))}</div>` + m(5)],
  ['grid item isolate z50', `<div style="display:grid">${wrap('isolation:isolate;z-index:50', hdr(10))}</div>` + m(5)],
  ['flex item opacity z1', `<div style="display:flex">${wrap('opacity:.9;z-index:1', hdr(10))}</div>` + m(5)],
  ['modal in static opacity z50 wrapper, app z10', wrap('position:relative;z-index:10', hdr(1)) + `<div style="opacity:.9;z-index:50">${m(1)}</div>`],
  ['modal in relative opacity z50 wrapper, app z10', wrap('position:relative;z-index:10', hdr(1)) + `<div style="position:relative;opacity:.9;z-index:50">${m(1)}</div>`],
  ...['-webkit-backdrop-filter:blur(2px)', 'backdrop-filter:blur(2px)', 'backdrop-filter:none', 'backdrop-filter:blur(2px);-webkit-backdrop-filter:none', '-webkit-backdrop-filter:blur(2px);backdrop-filter:none'].map((s) => [s, wrap(s, hdr(10)) + m(5)]),
  ...['content-visibility:auto', 'content-visibility:hidden', 'content-visibility:visible', 'content-visibility:foo', 'content-visibility:auto;content-visibility:visible', 'content-visibility:auto;content-visibility:foo', 'CONTENT-VISIBILITY:AUTO', 'view-transition-name:vt', 'view-transition-name:none', 'view-transition-name:auto', 'view-transition-name:match-element', 'view-transition-name:a b', 'view-transition-name:1a', 'view-transition-name:vt;view-transition-name:none', 'view-transition-name:vt;view-transition-name:1a', 'view-transition-name:VT', 'will-change:mask-image', 'will-change:-webkit-mask-image', 'will-change:mask-size', 'will-change:mask', 'will-change:content-visibility', 'will-change:view-transition-name', 'will-change:contain-intrinsic-size', 'will-change:top,mask-image', 'will-change:MASK-IMAGE', 'opacity:99%', 'opacity:100%', 'opacity:50%'].map((s) => [s, wrap(s, hdr(10)) + m(5)]),
  ['tailwind isolate root, cookie bar outside', wrap('isolation:isolate', hdr(50)) + m(40)],
  ['tailwind isolate root, cookie bar z-auto', wrap('isolation:isolate', hdr(50)) + `<div id=m style="position:fixed;left:0;top:0;width:400px;height:40px"></div>`],
];
for (const [name, body] of cases) {
  await p.setContent(`<!doctype html><style>body{margin:0;height:3000px}</style>${body}<div style="height:3000px"></div>`);
  await p.evaluate('window.scrollTo(0, 500)');
  console.log(JSON.stringify(name), await p.evaluate(() => { const e = document.elementFromPoint(10, 10); return (e && (e.id || e.tagName)) + ' ' + document.getElementById('h').getBoundingClientRect().y; }));
}
await b.close();
