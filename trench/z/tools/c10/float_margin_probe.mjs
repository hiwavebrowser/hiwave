// C10 (a): a float after a block must not collapse margins with it. Chromium 143.
// node float_margin_probe.mjs <dir with node_modules/playwright>; prints a Rust table of (name, body, want).
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log('// ' + b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
const A = (s) => `<div id=a style="height:20px;${s}"></div>`;
const F = (s) => `<div id=f style="float:left;width:50px;height:50px;${s}"></div>`;
const N = (s) => `<div id=n style="height:10px;${s}"></div>`;
const cases = [
  ['block mb, float mt', A('margin-bottom:30px') + F('margin-top:10px')],
  ['block mb smaller than float mt', A('margin-bottom:10px') + F('margin-top:30px')],
  ['block mb, float none', A('margin-bottom:30px') + F('')],
  ['block none, float mt', A('') + F('margin-top:10px')],
  ['negative block mb, float mt', A('margin-bottom:-5px') + F('margin-top:10px')],
  ['block mb, negative float mt', A('margin-bottom:30px') + F('margin-top:-10px')],
  ['then a block with mt', A('margin-bottom:30px') + F('margin-top:10px') + N('margin-top:40px')],
  ['then a block with smaller mt', A('margin-bottom:30px') + F('margin-top:10px') + N('margin-top:5px')],
  ['then a block with no mt', A('margin-bottom:30px') + F('') + N('')],
  ['float mb then block', A('') + F('margin-bottom:30px') + N('margin-top:5px')],
  ['right float', A('margin-bottom:30px') + `<div id=f style="float:right;width:50px;height:50px;margin-top:10px"></div>`],
  ['two floats', A('margin-bottom:30px') + F('margin-top:10px') + `<div id=n style="float:left;width:50px;height:50px;margin-top:20px"></div>`],
  ['clear after float', A('margin-bottom:30px') + F('margin-top:10px') + N('clear:both;margin-top:5px')],
  ['in a parent', `<div style="margin-top:7px">${A('margin-bottom:30px') + F('margin-top:10px')}</div>`],
  ['float first in a parent with mt', `<div style="margin-top:7px">${F('margin-top:10px') + N('')}</div>`],
  ['float first in body', F('margin-top:10px') + N('margin-top:15px')],
  ['empty block between', A('margin-bottom:30px') + `<div style="margin:12px 0"></div>` + F('margin-top:10px')],
];
const out = [];
for (const [name, body] of cases) {
  await p.setContent(`<!doctype html><style>body{margin:0}</style>${body}`);
  const got = await p.evaluate(() => ['f', 'n'].map((i) => { const e = document.getElementById(i); return e ? e.getBoundingClientRect().y : '-'; }).join(' '));
  out.push(`    (${JSON.stringify(name)}, ${JSON.stringify(body)}, ${JSON.stringify(got)}),`);
}
console.log(out.join('\n'));
await b.close();
