// C10 (a) follow-on: an empty block's margins collapse through it, with what comes before and after. Chromium 143.
// node empty_through_probe.mjs <dir with node_modules/playwright>; prints a Rust table of (name, body, want).
// want is the y of #e (the empty box), #n (the next box), then the height of #p (the parent, if any).
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log('// ' + b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
const A = (s = 'margin-bottom:30px') => `<div style="height:20px;${s}"></div>`;
const E = (s = 'margin:12px 0') => `<div id=e style="${s}"></div>`;
const N = (s = '') => `<div id=n style="height:10px;${s}"></div>`;
const cases = [
  ['then a block', A() + E() + N()],
  ['then a block with a larger mt', A() + E() + N('margin-top:40px')],
  ['larger bottom than the block before', A() + E('margin:12px 0 45px') + N()],
  ['larger top than the block before', A() + E('margin:45px 0 12px') + N()],
  ['two empties', A() + E() + `<div style="margin:35px 0"></div>` + N()],
  ['negative bottom', A() + E('margin:0 0 -5px') + N()],
  ['nothing before', E() + N()],
  ['height 0', A() + E('margin:12px 0;height:0') + N()],
  ['min-height', A() + E('margin:12px 0;min-height:1px') + N()],
  ['border stops it', A() + E('margin:12px 0;border-top:1px solid') + N()],
  ['padding stops it', A() + E('margin:12px 0;padding-bottom:1px') + N()],
  ['overflow hidden stops it', A() + E('margin:12px 0;overflow:hidden') + N()],
  ['display flex stops it', A() + E('margin:12px 0;display:flex') + N()],
  ['height 1 stops it', A() + E('margin:12px 0;height:1px') + N()],
  ['clear none after no float', A() + E('margin:12px 0;clear:both') + N()],
  ['holds an abspos box', A() + `<div id=e style="margin:12px 0"><div style="position:absolute;width:5px;height:5px"></div></div>` + N()],
  ['holds an empty block', A() + `<div id=e style="margin:12px 0"><div style="margin:50px 0"></div></div>` + N()],
  ['last in a parent', `<div id=p>${A() + E()}</div>` + N()],
  ['last in a parent with a border', `<div id=p style="border-bottom:1px solid">${A() + E()}</div>` + N()],
  ['last in a fixed-height parent', `<div id=p style="height:60px">${A() + E()}</div>` + N()],
  ['first in a parent', `<div id=p style="margin-top:7px">${E() + N()}</div>`],
  ['first in a parent with a border', `<div id=p style="border-top:1px solid;margin-top:7px">${E() + N()}</div>`],
  ['only child of a parent', A() + `<div id=p style="margin:5px 0">${E()}</div>` + N()],
  ['then a float', A() + E() + `<div id=n style="float:left;width:50px;height:50px;margin-top:10px"></div>`],
  ['then text', A() + E() + `<div id=n>x</div>`],
  ['first in a parent, next has a larger mt', `<div id=p style="margin-top:7px">${E() + N('margin-top:40px')}</div>`],
  ['first in a parent, then text then a block', `<div id=p style="margin-top:7px">${E()}x${N('margin-top:40px')}</div>`],
  ['first in a parent, then a float then a block', `<div id=p style="margin-top:7px">${E()}<div style="float:left;width:5px;height:5px"></div>${N('margin-top:40px')}</div>`],
  ['clearance past a float', `<div style="float:left;width:50px;height:100px"></div>` + A('margin-bottom:0') + E('margin:12px 0;clear:both') + N()],
  ['clearance past a float, block before, next has mt', `<div style="float:left;width:50px;height:100px"></div>` + A('margin-bottom:0') + E('margin:12px 0;clear:left') + N('margin-top:30px')],
  ['clear none beside a float', `<div style="float:left;width:50px;height:100px"></div>` + E() + N()],
  ['holds a float', A() + `<div id=e style="margin:12px 0"><div style="float:left;width:5px;height:5px"></div></div>` + N()],
  ['percent margin', A() + E('margin:1% 0') + N()],
  ['relative with an offset', A() + E('margin:12px 0;position:relative;top:5px') + N()],
  ['in an inline-block parent', `<div id=p style="display:inline-block;width:100px"><div style="height:20px;margin-bottom:30px"></div>${E()}</div>` + N()],
  ['in a flex item', `<div style="display:flex"><div id=p style="width:100px">${A() + E() + N()}</div></div>`],
  ['a flex container child', `<div id=p style="display:flex;flex-direction:column">${A() + E() + N()}</div>`],
  ['in a table cell', `<table style="border-spacing:0"><tr><td id=p style="padding:0">${A() + E() + N()}</td></tr></table>`],
  ['a list item', `<ul style="margin:0;padding:0;list-style:none"><li id=e style="margin:12px 0"></li>${N()}</ul>`],
  ['an empty paragraph', A() + `<p id=e></p>` + N()],
];
const out = [];
for (const [name, body] of cases) {
  await p.setContent(`<!doctype html><style>body{margin:0}</style>${body}`);
  const got = await p.evaluate(() => {
    const y = (i) => { const e = document.getElementById(i); return e ? e.getBoundingClientRect().y : '-'; };
    const parent = document.getElementById('p');
    return [y('e'), y('n'), parent ? parent.getBoundingClientRect().height : '-'].join(' ');
  });
  out.push(`    (${JSON.stringify(name)}, ${JSON.stringify(body)}, ${JSON.stringify(got)}),`);
}
console.log(out.join('\n'));
await b.close();
