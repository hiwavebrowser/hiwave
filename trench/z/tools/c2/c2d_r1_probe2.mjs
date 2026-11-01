// #851 R1 finding 5 with an inset that acts: the fixed box sits at the top, so wfs is moved down by its own rule.
// node c2d_r1_probe2.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log(b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.setContent(`<!doctype html><style>body{margin:0;height:3000px}
  #sp{height:400px}#ws{position:sticky;top:50px;width:300px;height:200px;margin-left:100px}
  #wf{position:fixed;left:400px;top:0;width:200px;height:200px}
  #wfs{position:sticky;top:10px;width:100px;height:50px}
  </style><body><div id=sp></div><div id=ws><div id=wf><div id=wfs></div></div></div></body>`);
console.log(await p.evaluate(`var at = function (i) { var r = document.getElementById(i).getBoundingClientRect(); return r.x + ',' + r.y; };
  var hit = function (x, y) { var e = document.elementFromPoint(x, y); return e ? (e.id || e.tagName) : 'null'; };
  [0, 500, 1000].map(function (y) { window.scrollTo(0, y); return at('wfs') + ':' + hit(410, 55) + ':' + hit(410, 5); }).join(' ')`));
await b.close();
