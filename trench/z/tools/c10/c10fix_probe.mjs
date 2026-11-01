// Chromium 143: rects of a fixed box with a transform under a window scroll.
// node c10fix_probe.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log(b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
const READ = `var $ = function (i) { return document.getElementById(i); };
  var nums = function (a) { return a.map(function (v) { return +v.toFixed(3); }).join(' '); };
  var box = function (i) { var r = $(i).getBoundingClientRect(); return nums([r.x, r.y, r.width, r.height]); };`;
const page = `<!doctype html><style>body{margin:0;height:3000px}</style>
  <div id=m style="position:fixed;left:50%;top:10px;width:200px;height:50px;transform:translateX(-50%)"></div>
  <div id=plain style="position:fixed;left:7px;top:9px;width:20px;height:20px"></div>
  <div id=wrap style="position:fixed;left:100px;top:100px;width:200px;height:100px;transform:scale(2);transform-origin:0 0">
    <div id=kid style="position:absolute;left:5px;top:6px;width:10px;height:10px"></div>
    <div id=fkid style="width:20px;height:10px"></div>
  </div>
  <div id=undertr style="position:fixed;left:300px;top:300px;width:100px;height:100px;overflow:auto;transform:translate(1px,2px)">
    <div id=skid style="height:30px;width:30px"></div><div style="height:400px"></div>
  </div>
  <div id=fs style="position:fixed;left:500px;top:100px;width:100px;height:100px;overflow:auto">
    <div id=fsk style="height:20px;width:40px;transform:translate(3px,4px)"></div><div style="height:400px"></div>
  </div>
  <div id=flow style="width:50px;height:50px;transform:translate(1px,2px)"></div>
  <div style="height:200px"></div>
  <div id=inner style="width:100px;height:100px;transform:translate(10px,20px)">
    <div id=abs style="position:absolute;left:1px;top:2px;width:10px;height:10px"></div>
  </div>`;
await p.setContent(page);
const read = (js) => p.evaluate(READ + js);
const ids = ['m', 'plain', 'wrap', 'kid', 'fkid', 'undertr', 'skid', 'fs', 'fsk', 'flow', 'inner', 'abs'];
const all = `[${ids.map((i) => `'${i} ' + box('${i}')`).join(',')}].join(' | ')`;
console.log('scroll 0:', await read(all));
await p.evaluate('window.scrollTo(0, 500)');
console.log('scroll 500:', await read(all));
await p.evaluate(`document.getElementById('undertr').scrollTop = 7; document.getElementById('fs').scrollTop = 7`);
console.log('scroll 500, boxes 7:', await read(all));
await p.evaluate(`document.documentElement.scrollLeft = 0`);
await p.setContent(`<!doctype html><style>body{margin:0;height:3000px;width:3000px}</style>
  <div id=m style="position:fixed;left:50%;top:10px;width:200px;height:50px;transform:translateX(-50%)"></div>`);
await p.evaluate('window.scrollTo(30, 500)');
console.log('xy scroll:', await read(`box('m') + ' sx ' + window.scrollX`));
await b.close();
