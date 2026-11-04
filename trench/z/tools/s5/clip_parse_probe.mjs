// S5: which `clip` values Chromium takes (CSS.supports + computed value on an abs box).
// node clip_parse_probe.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log('// ' + b.version());
const p = await b.newPage();
const values = [
  'auto', 'rect(0,0,0,0)', 'rect(0 0 0 0)', 'rect(1px, 1px, 1px, 1px)', 'rect(1px 1px 1px 1px)',
  'rect(auto, 20px, auto, auto)', 'rect(auto auto auto auto)', 'rect(10%, 0, 0, 0)', 'rect(0, 0, 0)',
  'rect(0,0 0,0)', 'rect(1em, 2em, 3em, 4em)', 'rect(-5px, 10px, 10px, -5px)', 'RECT(0,0,0,0)',
  'rect(0,0,0,0,0)', 'rect()', 'inset(0)', 'rect(0,,0,0)', 'rect( 0 , 0 , 0 , 0 )', 'rect(1, 2, 3, 4)',
  'rect(calc(1px + 1px), 0, 0, 0)',
];
for (const v of values) {
  const ok = await p.evaluate((v) => CSS.supports('clip', v), v);
  console.log(JSON.stringify([v, ok]));
}
await b.close();
