// C10(b): rects of transformed boxes in Chromium 143, the numbers the red tests pin.
// usage: node c10b_probe.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const box = 'width:100px;height:50px;background:#08f';
const pages = {
  // Each kind of transform on a plain block at (20,10).
  kinds: `<div style="margin:0"><style>body{margin:0}.b{position:absolute;left:20px;top:10px;${box}}</style>
    <div class=b id=translate style="transform:translate(30px,40px)"></div>
    <div class=b id=percent style="transform:translate(-50%,-50%)"></div>
    <div class=b id=scale style="transform:scale(2)"></div>
    <div class=b id=scale0 style="transform:scale(2);transform-origin:0 0"></div>
    <div class=b id=originpx style="transform:scale(2);transform-origin:10px 20px"></div>
    <div class=b id=rotate style="transform:rotate(90deg)"></div>
    <div class=b id=rotate45 style="transform:rotate(45deg)"></div>
    <div class=b id=matrix style="transform:matrix(1,0,0,1,7,9)"></div>
    <div class=b id=skew style="transform:skewX(45deg)"></div>
    <div class=b id=t3d style="transform:translate3d(5px,6px,0)"></div>
    <div class=b id=indiv style="translate:30px 40px"></div>
    <div class=b id=indivscale style="scale:2"></div>
    <div class=b id=indivrot style="rotate:90deg"></div>
    <div class=b id=both style="translate:10px 0;transform:scale(2)"></div>
    <div class=b id=border style="border:5px solid red;transform:translate(1px,2px)"></div>
    <div class=b id=none style="transform:none"></div></div>`,
  // Offsets, sizes and the box under it do not move.
  metrics: `<style>body{margin:0}</style>
    <div id=wrap style="position:relative;left:50px;top:60px;${box};transform:translate(10px,20px) scale(2)">
      <div id=kid style="position:absolute;left:5px;top:6px;width:10px;height:10px"></div>
      <div id=flow style="width:20px;height:10px"></div>
    </div>
    <div id=next style="height:10px;margin-top:80px"></div>`,
  // Transforms multiply down the tree, order kept.
  nested: `<style>body{margin:0}</style>
    <div id=o style="position:absolute;left:0;top:0;width:200px;height:200px;transform:translate(100px,0) rotate(90deg);transform-origin:0 0">
      <div id=i style="width:50px;height:20px;margin-left:10px;transform:translate(5px,0)">
        <div id=leaf style="width:10px;height:10px"></div>
      </div>
    </div>`,
  // A scroller inside a transform and a transform inside a scroller.
  scroll: `<style>body{margin:0}</style>
    <div id=tin style="position:absolute;left:0;top:0;width:100px;height:100px;overflow:auto;transform:scale(2);transform-origin:0 0">
      <div id=tinkid style="height:400px;width:50px"></div></div>
    <div id=sout style="position:absolute;left:300px;top:0;width:100px;height:100px;overflow:auto">
      <div style="height:30px"></div><div id=soutkid style="height:20px;width:40px;transform:scale(2);transform-origin:0 0"></div>
      <div style="height:400px"></div></div>`,
  // Who the transform holds: absolute and fixed with no positioned ancestor.
  holds: `<style>body{margin:0;height:3000px}</style>
    <div style="height:100px"></div>
    <div id=t style="width:200px;height:50px;transform:translate(10px,20px)">
      <div id=abs style="position:absolute;left:1px;top:2px;width:10px;height:10px"></div>
      <div id=fix style="position:fixed;left:3px;top:4px;width:10px;height:10px"></div>
    </div>
    <div id=sc style="margin-top:100px;width:100px;height:100px;overflow:auto;transform:translate(1px,1px)">
      <div id=sabs style="position:absolute;left:1px;top:2px;width:10px;height:10px"></div>
      <div style="height:400px"></div></div>`,
  // A transform does not apply to a non-replaced inline; it does to the others.
  inline: `<style>body{margin:0}</style>
    <div style="width:300px"><span id=sp style="transform:translate(30px,40px)">text</span>
    <span id=ib style="display:inline-block;width:20px;height:20px;transform:translate(30px,40px)"></span>
    <img id=im width=20 height=20 style="transform:translate(30px,40px)" src="data:image/gif;base64,R0lGODlhAQABAAAAACw="></div>
    <div id=fl style="display:flex;transform:translate(1px,2px)"><span id=fi style="transform:translate(3px,4px)">x</span></div>`,
};
const b = await chromium.launch();
console.log('chromium', b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
for (const [name, html] of Object.entries(pages)) {
  await p.route('http://probe.test/' + name, r => r.fulfill({ contentType: 'text/html', body: '<!doctype html>' + html }));
  await p.goto('http://probe.test/' + name);
  const read = () => p.evaluate(() => {
    const out = {};
    for (const e of document.querySelectorAll('[id]')) {
      const r = e.getBoundingClientRect(), c = e.getClientRects();
      out[e.id] = [r.x, r.y, r.width, r.height].map(v => +v.toFixed(3)).join(' ')
        + ' | off ' + [e.offsetLeft, e.offsetTop, e.offsetWidth, e.offsetHeight].join(' ')
        + ' | n' + c.length + (c.length ? ' ' + [c[0].x, c[0].y].map(v => +v.toFixed(3)).join(' ') : '');
    }
    return out;
  });
  console.log('--- ' + name, JSON.stringify(await read(), null, 0).replaceAll('","', '",\n "'));
  if (name === 'scroll') {
    await p.evaluate(() => { tin.scrollTop = 10; sout.scrollTop = 7; });
    console.log('--- scroll after', JSON.stringify(await read()).replaceAll('","', '",\n "'));
  }
  if (name === 'holds') {
    await p.evaluate(() => window.scrollTo(0, 40));
    console.log('--- holds after window 40', JSON.stringify(await read()).replaceAll('","', '",\n "'));
  }
}
await b.close();
