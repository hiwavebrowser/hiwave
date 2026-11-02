// Percent opacity (#851 R1 finding 1): computed value, ink of a black box on white, and stacking context. Chromium 143.
// node opacity_pct_probe.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log(b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
const values = ['50%', '99%', '100%', '0%', '150%', '-10%', '12.5%', '5e1%', '+50%', '.5%', '50 %', '50%%', '%', '50%foo', '.5', '0', '1', '2', '-1', '+.5', '1e-1', '1.', '.', '1e', '0.5x', '1px', 'abc', 'inf', 'infinity', 'NaN', '-inf', '', 'calc(50%)', 'calc(0.5)', 'calc(25% + 25%)', 'calc(0.25 + 0.25)', 'calc(0.5 + 50%)', 'calc(50% * 2)', 'CALC(50%)', 'calc(150%)', 'calc(-1)', 'var(--p)', 'var(--n)', 'var(--nope)', 'var(--nope, 25%)', 'inherit', 'initial', 'unset', 'revert', '50% !important', '.5 !important', 'calc(1px)', 'calc(0 + 50%)', 'calc(50% + 0)', 'calc(50% / 2)', 'calc(2 * 25%)', 'calc(1 / 2)', 'calc(25%*2)', 'calc((25% + 25%) * 1)', 'calc(calc(50%))', 'calc(25%+25%)', 'calc(50%) foo', 'calc(50%', 'calc()', 'calc(50% * 2%)', 'calc(1 / 0)', 'calc(1em)', 'min(50%, 75%)', 'max(.1, .2)', 'clamp(0%, 50%, 100%)', '.5e0', '1E-1', '5E1%', '-0', '00.5', '0.5.5', '1e-1%'];
const page = (v, extra) => `<!doctype html><style>body{margin:0}${extra || ''}</style><div id=o style="--p:50%;--n:.5;opacity:.25"><div id=t style="width:100px;height:100px;background:#000;${v === '' ? '' : `opacity:${v}`}"></div></div>`;
const ink = async () => {
  const shot = await p.screenshot({ clip: { x: 50, y: 50, width: 1, height: 1 }, type: 'png' });
  const q = await b.newPage();
  const v = await q.evaluate(async (u) => {
    const i = new Image(); i.src = u; await i.decode();
    const c = document.createElement('canvas'); c.width = c.height = 1;
    const x = c.getContext('2d'); x.drawImage(i, 0, 0); return x.getImageData(0, 0, 1, 1).data[0];
  }, 'data:image/png;base64,' + shot.toString('base64'));
  await q.close();
  return v;
};
for (const v of values) {
  await p.setContent(page(v));
  const computed = await p.evaluate(() => getComputedStyle(document.getElementById('t')).opacity);
  const attr = await p.evaluate(() => document.getElementById('t').style.opacity);
  console.log('style', JSON.stringify(v), 'computed', computed, 'style.opacity', JSON.stringify(attr), 'gray', await ink());
}
// Sheet rule, later invalid value keeps the earlier one, and script writes.
for (const [name, css] of [['sheet 50%', '#t{opacity:50%}'], ['sheet .5 then 25%', '#t{opacity:.5;opacity:25%}'], ['sheet 25% then bad', '#t{opacity:25%;opacity:foo}'], ['sheet 25% then 50 %', '#t{opacity:25%;opacity:50 %}']]) {
  await p.setContent(`<!doctype html><style>body{margin:0}${css}</style><div id=t style="width:100px;height:100px;background:#000"></div>`);
  console.log('sheet', JSON.stringify(name), 'computed', await p.evaluate(() => getComputedStyle(document.getElementById('t')).opacity), 'gray', await ink());
}
for (const v of ['50%', '.5', 'foo', '50 %', '']) {
  await p.setContent(`<!doctype html><style>body{margin:0}</style><div id=t style="width:100px;height:100px;background:#000;opacity:.25"></div>`);
  await p.evaluate((x) => { document.getElementById('t').style.opacity = x; }, v);
  console.log('setter', JSON.stringify(v), 'style.opacity', JSON.stringify(await p.evaluate(() => document.getElementById('t').style.opacity)), 'computed', await p.evaluate(() => getComputedStyle(document.getElementById('t')).opacity), 'gray', await ink());
}
// Stacking: a wrapper at this opacity holding a z 10 box against a z 5 box after it, both positioned, no scroll.
const ctx = (v) => `<!doctype html><style>body{margin:0}</style><div id=w style="opacity:${v}"><div id=h style="position:relative;width:300px;height:30px;z-index:10"></div></div><div id=m style="position:absolute;left:0;top:0;width:400px;height:40px;z-index:5"></div>`;
for (const v of ['50%', '99%', '100%', '0%', '.99', '1', '150%', 'calc(50%)', 'calc(100%)', 'var(--nope, 50%)', '50 %']) {
  await p.setContent(ctx(v));
  console.log('stack', JSON.stringify(v), await p.evaluate(() => { const e = document.elementFromPoint(10, 10); return e && (e.id || e.tagName); }));
}
// Sticky over fixed, the #851 regression.
const stuck = (v) => `<!doctype html><style>body{margin:0;height:3000px}</style><div id=w style="height:2000px;opacity:${v}"><div style="height:400px"></div><div id=h style="position:sticky;top:0;width:300px;height:30px;z-index:10"></div></div><div id=m style="position:fixed;left:0;top:0;width:400px;height:40px;z-index:5"></div><div style="height:3000px"></div>`;
for (const v of ['50%', '99%', '100%', 'calc(50%)']) {
  await p.setContent(stuck(v));
  await p.evaluate('window.scrollTo(0, 500)');
  console.log('sticky', JSON.stringify(v), await p.evaluate(() => { const e = document.elementFromPoint(10, 10); return e && (e.id || e.tagName); }));
}
// Keyframes: the settled frame of a finite forward animation with a percent stop, on a paused-at-end read.
await p.setContent(`<!doctype html><style>body{margin:0}@keyframes a{to{opacity:25%}}#t{width:100px;height:100px;background:#000;animation:a 1ms forwards}</style><div id=t></div>`);
await p.waitForTimeout(100);
console.log('keyframes to 25%', await p.evaluate(() => getComputedStyle(document.getElementById('t')).opacity), 'gray', await ink());
await b.close();
