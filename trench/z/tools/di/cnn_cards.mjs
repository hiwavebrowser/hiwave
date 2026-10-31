// CA1-2: where two neighbouring cnn card labels sit in Chromium (a modal covers them in the screenshot).
// usage: node cnn_cards.mjs <node_modules>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15 HiWave/1.0';
const b = await chromium.launch();
const c = await b.newContext({ viewport: { width: 1280, height: 800 }, userAgent: UA });
const p = await c.newPage();
await p.goto('https://www.cnn.com/', { waitUntil: 'load', timeout: 45000 });
await p.waitForTimeout(4000);
console.log(await p.evaluate(`(() => {
  const out = [];
  for (const e of document.querySelectorAll('body *')) {
    if (e.children.length) continue;
    const t = e.textContent.trim();
    if (t !== 'CNN Headlines' && t !== 'CNN Stream') continue;
    const r = e.getBoundingClientRect();
    if (!r.width) continue;
    const chain = [];
    let n = e;
    for (let i = 0; i < 4 && n; i++, n = n.parentElement) {
      const cs = getComputedStyle(n);
      chain.push(n.tagName.toLowerCase() + ':' + cs.display + ' flex=' + cs.flexGrow + '/' + cs.flexShrink + '/' + cs.flexBasis + ' h=' + Math.round(n.getBoundingClientRect().height));
    }
    out.push(t + ' x=' + Math.round(r.x) + ' y=' + Math.round(r.y) + ' | ' + chain.join(' < '));
  }
  return out.join('\\n');
})()`));
await b.close();
