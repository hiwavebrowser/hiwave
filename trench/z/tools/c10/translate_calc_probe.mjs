// The individual transform properties with spaces inside a function, Chromium 143. A 100x50 box at (20,10) under translate:7px first, so a refusal reads x 27.
// node translate_calc_probe.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log(b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
const values = [
  ['translate', '0px calc(-100% - 1px)'], ['translate', 'calc(10px + 5%) 0'], ['translate', 'calc(10px + 5%)'], ['translate', 'calc(1px + 1px) calc(2px * 2) 0'],
  ['translate', 'calc( 1px + 1px ) 3px 0px'], ['translate', '1px 2px 3px'], ['translate', '1px 2px calc(1px + 1px)'], ['translate', '1px 2px 3px 4px'], ['translate', 'min(1px, 2px) max(3px, 4px)'],
  ['translate', 'calc(1px + 1px) calc(2px * 2) 0 0'], ['translate', 'none'],
  ['scale', 'min(2, 3)'], ['scale', 'calc(1 + 1)'], ['scale', 'calc(1 + 1) calc(2 + 1)'], ['scale', '2 3'],
  ['rotate', 'calc(45deg + 45deg)'], ['rotate', 'z calc(45deg + 45deg)'], ['rotate', '90deg'],
];
for (const [prop, v] of values) {
  await p.setContent(`<!doctype html><style>body{margin:0}#b{position:absolute;left:20px;top:10px;width:100px;height:50px;${prop}:7px;translate:7px;scale:none;rotate:none;${prop}:${v}}</style><div id=b></div>`);
  console.log(JSON.stringify([prop, v]), await p.evaluate(() => { const r = document.getElementById('b').getBoundingClientRect(); return [r.x, r.y, r.width, r.height].map((n) => +n.toFixed(3)).join(' '); }));
}
// The shape on the page: a clipping wrapper under a sticky header, an opaque panel slid out of it.
await p.setContent(`<!doctype html><style>body{margin:0;height:2000px}
  #h{position:sticky;top:0;height:72px;width:800px;display:flex}
  ul{display:flex;margin:0;padding:0;list-style:none}li{display:flex;z-index:30;margin-left:100px;width:90px}
  #w{position:absolute;top:72px;left:0;width:100%;overflow:hidden auto;max-height:500px}
  #p{position:relative;background:rgb(2,9,10);height:200px;translate:0px calc(-100% - 1px)}
  </style><body><div id=h><ul><li><div id=w><div id=p></div></div></li></ul></div></body>`);
console.log('panel', await p.evaluate(() => { const f = (i) => { const r = document.getElementById(i).getBoundingClientRect(); return [r.x, r.y, r.width, r.height].join(' '); }; return f('w') + ' | ' + f('p'); }));
await b.close();
