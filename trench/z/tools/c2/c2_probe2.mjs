// C2(a), second page: out-of-flow children, nesting, offsets, events, pixels. Hand-made page, no site.
// usage: node c2_probe2.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = `<!doctype html><style>body{margin:0}
#st{overflow:auto;width:100px;height:100px;margin-left:0;margin-top:0}
#st-in{height:300px;background:#00f}
#st-abs{position:absolute;left:300px;top:0;width:20px;height:20px;background:#0f0}
#st-fix{position:fixed;left:330px;top:0;width:20px;height:20px;background:#ff0}
#rel{position:relative;overflow:auto;width:100px;height:100px;margin-top:10px}
#rel-in{height:300px;background:#0ff}
#rel-abs{position:absolute;left:10px;top:40px;width:20px;height:20px;background:#f00}
#rel-fix{position:fixed;left:360px;top:0;width:20px;height:20px;background:#f0f}
#out{overflow:auto;width:100px;height:100px;position:absolute;left:400px;top:0}
#inner{overflow:auto;width:80px;height:200px}
#deep{height:500px;background:#888}
#clip{overflow:clip;width:50px;height:50px;position:absolute;left:520px;top:0}
#clip-in{height:200px;background:#333}
#gone{overflow:auto;width:50px;height:50px;position:absolute;left:580px;top:0}
#gone-in{height:200px;background:#666}
#ev{overflow:auto;width:50px;height:50px;position:absolute;left:640px;top:0}
#ev-in{height:200px}
</style><body><div id=st><div id=st-in><div id=st-abs></div><div id=st-fix></div></div></div>
<div id=rel><div id=rel-in></div><div id=rel-abs></div><div id=rel-fix></div></div>
<div id=out><div id=inner><div id=deep></div></div></div>
<div id=clip><div id=clip-in></div></div>
<div id=gone><div id=gone-in></div></div>
<div id=ev><div id=ev-in></div></div></body>`;
const expr = `(async () => {
  const $ = (i) => document.getElementById(i);
  const at = (i) => { const r = $(i).getBoundingClientRect(); return r.x + ',' + r.y; };
  const out = [];
  $('st').scrollTop = 50;
  out.push('static-scroller st-in=' + at('st-in') + ' st-abs=' + at('st-abs') + ' st-fix=' + at('st-fix'));
  $('rel').scrollTop = 50;
  out.push('rel-scroller rel-in=' + at('rel-in') + ' rel-abs=' + at('rel-abs') + ' rel-fix=' + at('rel-fix'));
  out.push('offsets rel-abs ' + $('rel-abs').offsetTop + ' ' + ($('rel-abs').offsetParent||{}).id + ' rel-in ' + $('rel-in').offsetTop + ' st-in ' + $('st-in').offsetTop + ' ' + ($('st-in').offsetParent||{}).tagName);
  $('out').scrollTop = 30; $('inner').scrollTop = 70;
  out.push('nested inner=' + at('inner') + ' deep=' + at('deep') + ' hit=' + document.elementFromPoint(410, 10).id);
  $('clip').scrollTop = 25;
  out.push('clip ' + $('clip').scrollTop + ' clip-in=' + at('clip-in'));
  document.body.style.overflow = 'hidden'; document.body.scrollTop = 20;
  out.push('body ' + document.body.scrollTop + ' ' + at('st') + ' scrollY=' + window.scrollY);
  document.body.style.overflow = '';
  $('gone').scrollTop = 40;
  $('gone').style.display = 'none';
  const hiddenRead = $('gone').scrollTop;
  $('gone').style.display = '';
  out.push('gone ' + hiddenRead + ' back=' + $('gone').scrollTop + ' gone-in=' + at('gone-in'));
  $('gone-in').style.height = '60px';
  out.push('shrunk ' + $('gone').scrollTop + ' gone-in=' + at('gone-in'));
  const seen = [];
  $('ev').addEventListener('scroll', (e) => seen.push('el:' + e.bubbles + ':' + e.target.id));
  document.addEventListener('scroll', (e) => seen.push('doc:' + (e.target.id || e.target.nodeName)));
  $('ev').scrollTop = 10; $('ev').scrollTop = 20; $('ev').scrollTop = 20;
  const sync = seen.length;
  await new Promise((r) => setTimeout(r, 200));
  out.push('events sync=' + sync + ' ' + seen.join(' '));
  return out.join('\\n');
})()`;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.setContent(html);
console.log(b.version());
console.log(await p.evaluate(expr));
await p.screenshot({ path: process.argv[3] });
await b.close();
