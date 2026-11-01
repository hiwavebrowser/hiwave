// #851's shopify mover: in Chromium 143, what the header's dropdown panels are. Prints box shape and CSS only, no page text.
// node c2d_shop_chrome.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log(b.version());
const p = await b.newPage({ viewport: { width: 1280, height: 800 } });
await p.goto('https://www.shopify.com/', { waitUntil: 'load', timeout: 45000 }).catch((e) => console.log('goto', String(e).slice(0, 200)));
await p.waitForTimeout(4000);
console.log(JSON.stringify(await p.evaluate(() => {
  const props = ['display', 'position', 'visibility', 'opacity', 'overflow', 'backgroundColor', 'transform', 'zIndex', 'maxHeight', 'height', 'pointerEvents', 'clipPath', 'contentVisibility'];
  const shape = (e) => {
    const r = e.getBoundingClientRect(), c = getComputedStyle(e), o = { tag: e.tagName, cls: String(e.className).slice(0, 180), hidden: e.hidden, rect: [r.x, r.y, r.width, r.height].map(Math.round) };
    for (const k of props) o[k] = c[k];
    for (const a of ['aria-hidden', 'aria-expanded', 'data-state', 'inert']) if (e.hasAttribute(a)) o[a] = e.getAttribute(a);
    return o;
  };
  const header = document.querySelector('header');
  if (!header) return { noHeader: true };
  const out = { header: shape(header), rows: [] };
  const buttons = [...header.querySelectorAll('button, a')].filter((e) => { const r = e.getBoundingClientRect(); return r.y < 70 && r.height > 0 && r.x > 250 && r.x < 480; });
  for (const btn of buttons.slice(0, 2)) {
    let li = btn; for (let i = 0; i < 5 && li.parentElement && li.tagName !== 'LI'; i++) li = li.parentElement;
    const row = { button: shape(btn), holder: shape(li), kids: [] };
    const walk = (e, d) => { for (const k of e.children) { if (d < 4 && row.kids.length < 22 && !k.contains(btn)) { row.kids.push({ d, ...shape(k) }); walk(k, d + 1); } } };
    walk(li, 0);
    out.rows.push(row);
  }
  return out;
}), null, 0));
await b.close();
