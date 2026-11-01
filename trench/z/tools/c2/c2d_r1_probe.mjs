// #851 R1 cases in Chromium 143: sticky under transforms, a sticky box over a fixed bar, sticky in a fixed box in a sticky box.
// node c2d_r1_probe.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log(b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
const AT = `var $ = function (i) { return document.getElementById(i); };
  var at = function (i) { var r = $(i).getBoundingClientRect(); return r.x + ',' + r.y; };
  var size = function (i) { var r = $(i).getBoundingClientRect(); return r.width + 'x' + r.height; };
  var hit = function (x, y) { var e = document.elementFromPoint(x, y); return e ? (e.id || e.tagName) : 'null'; };`;
const run = async (name, page, js) => {
  const q = await b.newPage({ viewport: { width: 800, height: 600 } });
  await q.setContent(page);
  console.log(name, JSON.stringify(await q.evaluate(AT + js)));
  await q.close();
};
const T = `<!doctype html><style>body{margin:0;height:3000px}.tall{height:600px}.gap{height:50px}
  .st{position:sticky;top:0;height:20px;width:50px}
  #a-s{position:absolute;left:0;top:0;width:200px;height:100px;overflow:auto;transform:translateX(10px)}
  #b-s{position:absolute;left:300px;top:0;width:200px;height:100px;overflow:auto}#b{transform:scale(2)}
  #sp{height:400px}#c-tr{transform:translateY(50px);margin-left:600px;height:1000px}
  #d-s{position:absolute;left:0;top:200px;width:200px;height:100px;overflow:auto;transform:scale(2);transform-origin:0 0}
  </style><body>
  <div id=a-s><div class=gap></div><div class=st id=a></div><div class=tall></div></div>
  <div id=b-s><div class=gap></div><div class=st id=b></div><div class=tall></div></div>
  <div id=d-s><div class=gap></div><div class=st id=d></div><div class=tall></div></div>
  <div id=sp></div><div id=c-tr><div class=st id=c></div></div></body>`;
await run('in-transformed-scroller', T, `$('a-s').scrollTop = 100; at('a')`);
await run('own-scale', T, `$('b-s').scrollTop = 100; at('b') + ' ' + size('b')`);
await run('scaled-scroller', T, `$('d-s').scrollTop = 100; at('d') + ' ' + size('d')`);
await run('window-under-translate', T, `window.scrollTo(0, 600); at('c')`);
await run('window-under-translate-steps', T,
  `[0, 300, 450, 700, 1200].map(function (y) { window.scrollTo(0, y); return at('c'); }).join(' ')`);
const F = `<!doctype html><style>body{margin:0;height:3000px}
  #bar{position:fixed;left:0;top:0;width:400px;height:40px}
  #sp{height:400px}#st{position:sticky;top:0;width:300px;height:30px}
  #after{position:relative;width:100px;height:20px}
  </style><body><div id=bar></div><div id=sp></div><div id=st></div></body>`;
await run('sticky-over-fixed', F, `window.scrollTo(0, 500); hit(10, 10) + ' ' + hit(350, 10) + ' ' + at('st')`);
const FZ = F.replace('#bar{', '#bar{z-index:5;');
await run('fixed-z5-over-sticky', FZ, `window.scrollTo(0, 500); hit(10, 10)`);
const SZ = F.replace('#st{', '#st{z-index:5;').replace('<div id=bar></div><div id=sp></div><div id=st></div>', '<div id=sp></div><div id=st></div><div id=bar></div>');
await run('sticky-z5-before-fixed', SZ, `window.scrollTo(0, 500); hit(10, 10)`);
const FL = F.replace('<div id=bar></div><div id=sp></div><div id=st></div>', '<div id=sp></div><div id=st></div><div id=bar></div>');
await run('fixed-later-than-sticky', FL, `window.scrollTo(0, 500); hit(10, 10)`);
const FK = F.replace('<div id=st></div>', '<div id=st><div id=kid style="width:50px;height:10px"></div></div>');
await run('sticky-child-over-fixed', FK, `window.scrollTo(0, 500); hit(10, 5) + ' ' + hit(10, 20)`);
await run('sticky-before-scroll-under-fixed', F, `hit(10, 10)`);
const N = `<!doctype html><style>body{margin:0;height:3000px}
  #sp{height:400px}#ws{position:sticky;top:50px;width:300px;height:200px;margin-left:100px}
  #wf{position:fixed;left:400px;top:100px;width:200px;height:200px}
  #wfs{position:sticky;top:10px;width:100px;height:50px}
  </style><body><div id=sp></div><div id=ws><div id=wf><div id=wfs></div></div></div></body>`;
await run('sticky-in-fixed-in-sticky', N,
  `[0, 500, 1000].map(function (y) { window.scrollTo(0, y); return y + ':' + at('wfs') + ':' + hit(410, 110); }).join(' ')`);
await b.close();
