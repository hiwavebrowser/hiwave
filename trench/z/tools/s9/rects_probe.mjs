// S9: Chromium rects for every element with an id in a page.
// node rects_probe.mjs <dir with node_modules/playwright> <page.html> [w] [h]
// Prints one "<id> x y w h" row per element (border boxes, CSS px, rounded to 0.01).
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const w = parseInt(process.argv[4] || '1280'), h = parseInt(process.argv[5] || '800');
const b = await chromium.launch();
console.log('// ' + b.version());
const p = await b.newPage({ viewport: { width: w, height: h } });
await p.setContent(readFileSync(process.argv[3], 'utf8'));
const rows = await p.evaluate(() => [...document.querySelectorAll('[id]')].map((e) => {
  const r = e.getBoundingClientRect();
  const f = (v) => Math.round(v * 100) / 100;
  return [e.id, f(r.x), f(r.y), f(r.width), f(r.height)].join(' ');
}));
for (const r of rows) console.log(r);
await b.close();
