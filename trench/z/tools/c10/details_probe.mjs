// C10 (d): <details>/<summary> boxes. Chromium 143.
// node details_probe.mjs <dir with node_modules/playwright>; prints a Rust table of (name, body, want).
// want = "<details height> <#s top or -> <#p top or -> <#q top or ->", rounded; every line is 20px.
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log('// ' + b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
const P = `<p id=p>body</p>`;
const Q = `<div id=q>more</div>`;
const S = (t = 'sum') => `<summary id=s>${t}</summary>`;
const cases = [
  ['closed, summary first', `<details id=d>${S()}${P}</details>`],
  ['open, summary first', `<details id=d open>${S()}${P}</details>`],
  ['closed, summary last', `<details id=d>${P}${S()}</details>`],
  ['open, summary last', `<details id=d open>${P}${S()}</details>`],
  ['open, summary between', `<details id=d open>${P}${S()}${Q}</details>`],
  ['open, two summaries', `<details id=d open>${P}<summary id=s>one</summary><summary id=q>two</summary></details>`],
  ['closed, two summaries', `<details id=d><summary id=s>one</summary><summary id=q>two</summary></details>`],
  ['closed, no summary', `<details id=d>${P}</details>`],
  ['open, no summary', `<details id=d open>${P}${Q}</details>`],
  ['closed, empty', `<details id=d></details>`],
  ['open, empty', `<details id=d open></details>`],
  ['closed, summary nested in a div', `<details id=d><div id=q><summary id=s>x</summary></div>${P}</details>`],
  ['open, summary nested in a div', `<details id=d open>${P}<div id=q><summary id=s>x</summary></div></details>`],
  ['open, text before the summary', `<details id=d open>text${S()}</details>`],
  ['closed, text before the summary', `<details id=d>text${S()}</details>`],
  ['open, summary display none', `<details id=d open>${P}<summary id=s style="display:none">x</summary></details>`],
];
const out = [];
for (const [name, body] of cases) {
  await p.setContent(`<!doctype html><style>body{margin:0;font:16px/20px monospace} p{margin:0} details,summary{list-style:none}</style>${body}`);
  const got = await p.evaluate(() => {
    const top = (i) => { const e = document.getElementById(i); if (!e) return '-'; const r = e.getBoundingClientRect(); return r.height ? Math.round(r.top) : '-'; };
    const d = document.getElementById('d');
    // Closed: the content slot's boxes are laid out but hidden, so read only the height and a child summary.
    if (!d.open) { const s = document.getElementById('s'); return [Math.round(d.getBoundingClientRect().height), s && s.parentElement === d ? top('s') : '-'].join(' '); }
    return [Math.round(d.getBoundingClientRect().height), top('s'), top('p'), top('q')].join(' ');
  });
  out.push(`    (${JSON.stringify(name)}, ${JSON.stringify(body)}, ${JSON.stringify(got)}),`);
}
console.log(out.join('\n'));
await b.close();
