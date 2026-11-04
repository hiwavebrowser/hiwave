// S7: `:checked` (and other compounds) left of a sibling combinator that sits
// left of a descendant/child step. Chromium oracle for checked_sibling.html.
// node checked_sibling_probe.mjs <dir with node_modules/playwright> <page.html>
// Prints "<phase> <id>:<display>" rows: load, then after script sets
// c1.checked = true, r2.checked = true, x2.checked = true, y2.checked = false,
// and c2.checked = false.
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log('// ' + b.version());
const p = await b.newPage({ viewport: { width: 400, height: 600 } });
await p.setContent(readFileSync(process.argv[3], 'utf8'));
const ids = ['off1', 'on1', 'off2', 'on2', 'mark1', 'mark2', 'deep1', 'deep2', 'n1', 'n2', 'v1', 'v2', 'g1', 'g2', 'z1', 'z2'];
const read = () => p.evaluate((ids) => ids.map((id) => id + ':' + getComputedStyle(document.getElementById(id)).display).join(' '), ids);
console.log('load ' + (await read()));
await p.evaluate(() => {
  for (const id of ['c1', 'r2', 'x2']) document.getElementById(id).checked = true;
  for (const id of ['c2', 'y2']) document.getElementById(id).checked = false;
});
console.log('toggled ' + (await read()));
await b.close();
