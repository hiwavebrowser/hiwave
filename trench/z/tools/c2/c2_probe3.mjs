// C2(a), third page: a bordered scroller's extent, a fractional write, a border around the clip, opacity under a scroll.
// usage: node c2_probe3.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = `<!doctype html><style>body{margin:0}
#b{overflow:auto;width:100px;height:100px;border:5px solid #000;padding:7px}
#b-in{height:100px;background:#00f}
#f{overflow:auto;width:100px;height:100px}
#f-in{height:300px;background:#0f0}
#o{overflow:auto;width:100px;height:100px;position:absolute;left:300px;top:0}
#o-in{height:300px;background:#f00;opacity:.5}
</style><body><div id=b><div id=b-in></div></div><div id=f><div id=f-in></div></div><div id=o><div id=o-in></div></div></body>`;
const expr = `(() => {
  const $ = (i) => document.getElementById(i);
  const at = (i) => { const r = $(i).getBoundingClientRect(); return r.x + ',' + r.y; };
  const out = [];
  const b = $('b');
  out.push('bordered ' + [b.scrollHeight, b.clientHeight, b.scrollWidth, b.clientWidth].join(' '));
  b.scrollTop = 500;
  out.push('bordered-max ' + b.scrollTop);
  const f = $('f');
  f.scrollTop = 30.5;
  out.push('fraction ' + f.scrollTop + ' ' + at('f-in'));
  f.scrollTop = 30.4;
  out.push('fraction2 ' + f.scrollTop + ' ' + at('f-in'));
  $('o').scrollTop = 50;
  return out.join('\\n');
})()`;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.setContent(html);
console.log(b.version());
console.log(await p.evaluate(expr));
await b.close();
