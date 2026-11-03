// C10 (c): offsetParent and offsets through tables. Chromium 143.
// node offset_parent_probe.mjs <dir with node_modules/playwright>; prints a Rust table of (name, body, want).
// want = "<offsetParent id or tag or null> <offsetLeft> <offsetTop>" of #t.
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log('// ' + b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
const T = `<div id=t style="width:10px;height:10px"></div>`;
const S = (s) => `<div id=t style="width:10px;height:10px;${s}"></div>`;
const tbl = (inner, ts = '', cs = '') => `<table id=tb style="border-spacing:0;${ts}"><tr id=tr><td id=c style="padding:3px;width:40px;height:40px;${cs}">${inner}</td></tr></table>`;
const cases = [
  ['in a td', tbl(T)],
  ['in a th', `<table id=tb style="border-spacing:0"><tr><th id=c style="padding:3px;width:40px;height:40px">${T}</th></tr></table>`],
  ['deep in a td', tbl(`<div id=w style="padding:2px"><div id=w2 style="padding:1px">${T}</div></div>`)],
  ['td with a border', tbl(T, '', 'border:4px solid red')],
  ['table with margin and border', tbl(T, 'margin:7px;border:2px solid red')],
  ['table with spacing', tbl(T, 'border-spacing:5px')],
  ['td is the target', `<table id=tb style="border-spacing:0;margin:5px"><tr><td id=t style="width:40px;height:40px"></td></tr></table>`],
  ['second td is the target', `<table id=tb style="border-spacing:0;margin:5px"><tr><td style="width:40px;height:40px"></td><td id=t style="width:40px;height:40px"></td></tr></table>`],
  ['th is the target', `<table id=tb style="border-spacing:0"><tr><th id=t style="width:40px;height:40px"></th></tr></table>`],
  ['tr is the target', `<table id=tb style="border-spacing:0;margin:5px"><tr id=t><td style="width:40px;height:40px"></td></tr></table>`],
  ['tbody is the target', `<table id=tb style="border-spacing:0;margin:5px"><tbody id=t><tr><td style="width:40px;height:40px"></td></tr></tbody></table>`],
  ['table is the target', `<table id=t style="margin:5px"><tr><td>x</td></tr></table>`],
  ['caption is the target', `<table id=tb style="border-spacing:0;margin:5px"><caption id=t>x</caption><tr><td style="width:40px;height:40px"></td></tr></table>`],
  ['in a caption', `<table id=tb style="border-spacing:0;margin:5px"><caption id=cap>${T}</caption><tr><td style="width:40px;height:40px"></td></tr></table>`],
  ['relative target in a td', tbl(S('position:relative'))],
  ['relative target with offset in a td', tbl(S('position:relative;left:5px;top:6px'))],
  ['absolute target in a td', tbl(S('position:absolute;left:5px;top:6px'))],
  ['fixed target in a td', tbl(S('position:fixed;left:5px;top:6px'))],
  ['sticky target in a td', tbl(S('position:sticky;top:0'))],
  ['absolute target in a relative td', tbl(S('position:absolute;left:5px;top:6px'), '', 'position:relative')],
  ['static target in a relative td', tbl(T, '', 'position:relative')],
  ['relative wrapper inside the td', tbl(`<div id=w style="position:relative;padding:2px">${T}</div>`)],
  ['td inside a relative wrapper', `<div id=w style="position:relative;padding:9px">${tbl(T)}</div>`],
  ['absolute target, td, relative wrapper', `<div id=w style="position:relative;padding:9px">${tbl(S('position:absolute;left:5px;top:6px'))}</div>`],
  ['nested table', tbl(`<table id=tb2 style="border-spacing:0"><tr><td id=c2 style="padding:2px">${T}</td></tr></table>`)],
  ['inner table is the target', tbl(`<table id=t style="border-spacing:0"><tr><td>x</td></tr></table>`)],
  ['a span in a td', tbl(`<span id=t>x</span>`)],
  ['td with display block', `<table id=tb style="border-spacing:0"><tr><td id=c style="display:block;padding:3px">${T}</td></tr></table>`],
  ['td with display contents', `<table id=tb style="border-spacing:0"><tr><td id=c style="display:contents">${T}</td></tr></table>`],
  ['table with display block', `<table id=tb style="display:block;margin:5px"><tr><td id=c>${T}</td></tr></table>`],
  ['td with no table', `<td id=c>${T}</td>`],
  ['td made by script outside a table', `<div id=h></div><script>var d=document.createElement('td');d.id='c';d.style.padding='3px';d.innerHTML='${T}';document.getElementById('h').appendChild(d)</script>`],
  ['display table on a div', `<div id=w style="display:table;margin:5px"><div id=w2 style="display:table-cell;padding:3px">${T}</div></div>`],
  ['tr with position', `<table id=tb style="border-spacing:0"><tr id=tr style="position:relative"><td id=c style="padding:3px">${T}</td></tr></table>`],
  ['in a tr, no td', `<table id=tb style="border-spacing:0"><tr id=tr>${T}</tr></table>`],
  ['td display none', `<table id=tb style="border-spacing:0"><tr><td id=c style="display:none">${T}</td></tr></table>`],
  ['control, no table', `<div id=w style="margin:6px;padding:4px">${T}</div>`],
  ['control, relative', `<div id=w style="position:relative;margin:6px;padding:4px">${T}</div>`],
  ['transform ancestor', `<div id=w style="transform:translateX(0);margin:6px;padding:4px">${T}</div>`],
  ['filter ancestor', `<div id=w style="filter:blur(0);margin:6px;padding:4px">${T}</div>`],
  ['contain paint ancestor', `<div id=w style="contain:paint;margin:6px;padding:4px">${T}</div>`],
  ['will-change transform ancestor', `<div id=w style="will-change:transform;margin:6px;padding:4px">${T}</div>`],
  ['fixed in a transform', `<div id=w style="transform:translateX(0);margin:6px;padding:4px">${S('position:fixed;left:2px;top:3px')}</div>`],
  ['positioned body', `<script>document.body.style.position='relative';document.body.style.margin='9px'</script>${T}`],
];
const out = [];
for (const [name, body] of cases) {
  await p.setContent(`<!doctype html><style>body{margin:0}</style><body>${body}`);
  const got = await p.evaluate(() => {
    const e = document.getElementById('t');
    if (!e) return 'no target';
    const o = e.offsetParent;
    return [o ? (o.id || o.tagName.toLowerCase()) : 'null', e.offsetLeft, e.offsetTop].join(' ');
  });
  out.push(`    (${JSON.stringify(name)}, ${JSON.stringify(body)}, ${JSON.stringify(got)}),`);
}
console.log(out.join('\n'));
await b.close();
