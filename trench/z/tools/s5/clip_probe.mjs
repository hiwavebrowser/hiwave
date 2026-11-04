// S5: screen-reader-only (visually hidden) boxes. Chromium oracle.
// node clip_probe.mjs <dir with node_modules/playwright>; prints JSON lines [name, body, ink]
// where ink = count of pixels that are not pure white in a 400x300 frame of the page
// (same page prefix as the engine test: html,body{margin:0;background:#fff}).
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
console.log('// ' + b.version());
const p = await b.newPage({ viewport: { width: 400, height: 300 }, deviceScaleFactor: 1 });
const PNG = require('playwright-core/lib/utilsBundle').PNG;
// The hidden box: 40px red block (red text too), so anything that leaks shows as ink.
const R = 'background:red;color:red;font:20px/20px Arial';
const box = (s, tag = 'span', inner = 'expand Cart') => `<${tag} style="${R};${s}">${inner}</${tag}>`;
const pos = 'position:absolute;width:1px;height:1px;overflow:hidden;white-space:nowrap;border:0;padding:0';
const cases = [
  // controls: no hiding rule
  ['control: abs 1x1 overflow hidden, no clip', box(pos + ';top:50px;left:50px')],
  ['control: abs 40x40 block', box('position:absolute;top:50px;left:50px;width:40px;height:40px', 'div', '')],
  // eBay .clipped
  ['ebay clipped: clip rect 1px x4 + clip-path inset 50%', box(pos + ';top:50px;left:50px;clip:rect(1px,1px,1px,1px);clip-path:inset(50%)')],
  // bootstrap 4/5
  ['bootstrap: clip rect(0,0,0,0) margin -1px', box(pos + ';top:50px;left:50px;margin:-1px;clip:rect(0,0,0,0)')],
  ['clip rect(0 0 0 0) space form', box(pos + ';top:50px;left:50px;clip:rect(0 0 0 0)')],
  ['clip only, no clip-path', box(pos + ';top:50px;left:50px;clip:rect(1px,1px,1px,1px)')],
  ['clip-path inset(50%) only', box(pos + ';top:50px;left:50px;clip-path:inset(50%)')],
  ['clip-path inset(100%) only', box(pos + ';top:50px;left:50px;clip-path:inset(100%)')],
  // without overflow hidden: the clip alone must hide text overflowing the 1px box
  ['clip rect no overflow', box('position:absolute;top:50px;left:50px;width:1px;height:1px;white-space:nowrap;clip:rect(0,0,0,0)')],
  ['clip-path inset 50% no overflow', box('position:absolute;top:50px;left:50px;width:1px;height:1px;white-space:nowrap;clip-path:inset(50%)')],
  // clip on a big box: a real rect
  ['clip rect on 40x40 block', box('position:absolute;top:50px;left:50px;width:40px;height:40px;clip:rect(10px,30px,30px,10px)', 'div', '')],
  ['clip rect auto sides', box('position:absolute;top:50px;left:50px;width:40px;height:40px;clip:rect(auto,20px,auto,auto)', 'div', '')],
  ['clip rect on static box: ignored', box('width:40px;height:40px;clip:rect(0,0,0,0)', 'div', '')],
  ['clip auto', box('position:absolute;top:50px;left:50px;width:40px;height:40px;clip:auto', 'div', '')],
  ['clip on fixed box', box('position:fixed;top:50px;left:50px;width:40px;height:40px;clip:rect(0,0,0,0)', 'div', '')],
  ['clip rect with child overflowing', `<div style="position:absolute;top:50px;left:50px;width:40px;height:40px;clip:rect(0,20px,20px,0)"><div style="width:80px;height:80px;background:red"></div></div>`],
  // in a header link, as on the eBay header
  ['in a link inside a header', `<header style="height:60px"><a href="#" style="display:inline-block;width:20px;height:20px"><span style="${R};${pos};clip:rect(1px,1px,1px,1px);clip-path:inset(50%)">expand Cart</span></a></header>`],
  // the box is a control or a flex/grid item, as eBay's header "expand" buttons are
  ['button clipped (ebay)', box(pos + ';top:50px;left:50px;clip:rect(1px,1px,1px,1px);clip-path:inset(50%)', 'button')],
  ['button clip-path only', box(pos + ';top:50px;left:50px;clip-path:inset(50%)', 'button')],
  ['button clip only', box(pos + ';top:50px;left:50px;clip:rect(0,0,0,0)', 'button')],
  ['input clip-path only', `<input value="expand Cart" style="${R};${pos};top:50px;left:50px;clip-path:inset(50%)">`],
  ['in a flex row', `<div style="display:flex;height:60px">${box(pos + ';clip-path:inset(50%)')}<span>&nbsp;</span></div>`],
  ['in a flex row, clip only', `<div style="display:flex;height:60px">${box(pos + ';clip:rect(0,0,0,0)')}</div>`],
  ['inline-block clip-path inset 50%', box('display:inline-block;position:absolute;top:50px;left:50px;width:1px;height:1px;white-space:nowrap;clip-path:inset(50%)')],
  ['abs child of a clipped box', `<div style="position:absolute;top:50px;left:50px;width:1px;height:1px;clip:rect(0,0,0,0)"><div style="position:absolute;width:40px;height:40px;background:red"></div></div>`],
];
for (const [name, body] of cases) {
  await p.setContent(`<!doctype html><style>html,body{margin:0;background:#fff}div{box-sizing:border-box}</style>${body}`);
  const png = PNG.sync.read(await p.screenshot());
  let ink = 0;
  for (let i = 0; i < png.data.length; i += 4) {
    if (png.data[i] !== 255 || png.data[i + 1] !== 255 || png.data[i + 2] !== 255) ink++;
  }
  console.log(JSON.stringify([name, body, ink]));
}
await b.close();
