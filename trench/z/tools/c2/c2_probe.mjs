// C2(a): an overflow box's scrollTop/scrollLeft against child geometry, in Chromium. Hand-made page, no site.
// usage: node c2_probe.mjs <worktree>/tools/parity_oracle/node_modules
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = `<!doctype html><style>body{margin:0}
#s{overflow:auto;width:200px;height:100px;position:absolute;left:10px;top:20px}
#w{width:500px;height:400px}
#a{height:50px;background:red}#b{height:50px;background:lime}#c{height:300px;background:blue}
#h{overflow:hidden;width:100px;height:50px;position:absolute;left:300px;top:20px}
#hc{height:200px;background:orange}
#v{overflow:visible;width:100px;height:50px;position:absolute;left:450px;top:20px}
#vc{height:200px;background:teal}
</style><body><div id=s><div id=w><div id=a>a</div><div id=b>b</div><div id=c>c</div></div></div>
<div id=h><div id=hc>h</div></div><div id=v><div id=vc>v</div></div></body>`;
const expr = `(() => {
  const $ = (i) => document.getElementById(i);
  const y = (i) => { const r = $(i).getBoundingClientRect(); return r.x + ',' + r.y; };
  const out = [];
  const s = $('s');
  out.push('initial ' + [s.scrollTop, s.scrollLeft, s.scrollHeight, s.scrollWidth, s.clientHeight, s.clientWidth].join(' ') + ' b=' + y('b'));
  s.scrollTop = 30;
  out.push('top30 ' + s.scrollTop + ' s=' + y('s') + ' a=' + y('a') + ' b=' + y('b'));
  s.scrollLeft = 40;
  out.push('left40 ' + s.scrollLeft + ' b=' + y('b'));
  s.scrollTop = 9999; s.scrollLeft = 9999;
  out.push('clamped ' + s.scrollTop + ' ' + s.scrollLeft + ' c=' + y('c'));
  s.scrollTop = -5; s.scrollLeft = -5;
  out.push('negative ' + s.scrollTop + ' ' + s.scrollLeft);
  s.scrollTo(0, 60);
  out.push('scrollTo ' + s.scrollTop + ' b=' + y('b'));
  s.scrollBy(0, 10);
  out.push('scrollBy ' + s.scrollTop + ' b=' + y('b'));
  const hit = document.elementFromPoint(20, 30);
  out.push('hit ' + hit.id);
  const h = $('h');
  h.scrollTop = 25;
  out.push('hidden ' + h.scrollTop + ' hc=' + y('hc'));
  const v = $('v');
  v.scrollTop = 25;
  out.push('visible ' + v.scrollTop + ' vc=' + y('vc'));
  return out.join('\\n');
})()`;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.setContent(html);
console.log(b.version());
console.log(await p.evaluate(expr));
await b.close();
