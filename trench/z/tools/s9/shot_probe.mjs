// S9: Chromium screenshot + #hplogo rect of a local page.
// node shot_probe.mjs <dir with node_modules/playwright> <page.html> <out.png>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log('// ' + b.version());
const p = await b.newPage({ viewport: { width: 1280, height: 800 } });
await p.goto('file://' + process.argv[3], { waitUntil: 'load' });
await p.waitForTimeout(1500);
const r = await p.evaluate(() => {
  const e = document.getElementById('hplogo');
  if (!e) return 'no #hplogo';
  const b = e.getBoundingClientRect();
  return ['hplogo', b.x, b.y, b.width, b.height].join(' ');
});
console.log(r);
await p.screenshot({ path: process.argv[4] });
await b.close();
