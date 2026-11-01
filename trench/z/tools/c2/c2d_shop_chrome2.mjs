// #851's shopify mover: the ancestor chain of a dropdown link in Chromium 143, and which rules set its hiding. Box shape and CSS only.
// node c2d_shop_chrome2.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1280, height: 800 } });
await p.goto('https://www.shopify.com/', { waitUntil: 'load', timeout: 45000 }).catch((e) => console.log('goto', String(e).slice(0, 200)));
await p.waitForTimeout(4000);
const rows = await p.evaluate(() => {
  const props = ['display', 'position', 'top', 'left', 'visibility', 'opacity', 'overflow', 'backgroundColor', 'transform', 'translate', 'zIndex', 'maxHeight', 'height', 'width', 'pointerEvents', 'clipPath'];
  const link = document.querySelector('header .level3-link');
  const out = [];
  for (let e = link, n = 0; e && e.tagName !== 'HEADER' && n < 14; e = e.parentElement, n++) {
    const r = e.getBoundingClientRect(), c = getComputedStyle(e), o = { tag: e.tagName, cls: String(e.className).slice(0, 420), rect: [r.x, r.y, r.width, r.height].map(Math.round) };
    for (const k of props) o[k] = c[k];
    for (const a of ['aria-hidden', 'aria-expanded', 'data-state', 'inert', 'hidden', 'style']) if (e.hasAttribute(a)) o[a] = e.getAttribute(a).slice(0, 200);
    out.push(o);
  }
  return out;
});
for (const r of rows) console.log(JSON.stringify(r));
await b.close();
