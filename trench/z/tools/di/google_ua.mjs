// DI: google in Chromium with the engine's product UA, so it is served the same variant.
// Screenshot plus the shape of the button/chip rows: tag, display, visible size. No page text is printed
// except the short labels of visible buttons.
// usage: node google_ua.mjs <node_modules> <out.png> <user agent>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
const c = await b.newContext({ viewport: { width: 1280, height: 800 }, userAgent: process.argv[4] });
const p = await c.newPage();
await p.goto('https://www.google.com/', { waitUntil: 'load', timeout: 45000 });
await p.waitForTimeout(5000);
await p.screenshot({ path: process.argv[3] });
console.log(b.version());
console.log(await p.evaluate(`(() => {
  const out = [];
  const labels = /^(Create images|Ask about files|Brainstorm|Google Search|I'm Feeling Lucky|AI Mode)$/;
  for (const e of document.querySelectorAll('body *')) {
    if (e.children.length > 2) continue;
    const t = (e.textContent || e.value || '').trim();
    const v = e.value || '';
    if (!labels.test(t) && !labels.test(v)) continue;
    const r = e.getBoundingClientRect();
    if (e.children.length && r.width === 0) continue;
    const chain = [];
    let n = e;
    for (let i = 0; i < 6 && n; i++, n = n.parentElement) {
      const cs = getComputedStyle(n);
      chain.push(n.tagName.toLowerCase() + ':' + cs.display + (cs.visibility !== 'visible' ? '/' + cs.visibility : ''));
    }
    out.push((t || v) + ' [' + Math.round(r.x) + ',' + Math.round(r.y) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height) + '] ' + chain.join(' < '));
  }
  return out.join('\\n');
})()`));
await b.close();
