// C2(c), second pass: the cases c2c_probe.mjs missed, each on the page the engine test uses.
// usage: node c2c_probe2.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = `<!doctype html><style>body{margin:0;height:3000px}
#s{overflow:auto;width:200px;height:100px;margin-top:1000px}
#s-gap{height:300px}
#s-t{height:20px}
#s-ab{position:absolute;left:10px;top:1800px;width:20px;height:20px}
#s-fx{position:fixed;left:400px;top:500px;width:20px;height:20px}
#f{position:fixed;left:400px;top:0;width:100px;height:100px;overflow:auto}
#f-gap{height:300px}
#f-t{height:20px}
#nm{height:20px}
#under{height:600px}
#after{height:20px}
#tr{transform:translateY(50px);height:20px}
</style><body>
<div id=s><div id=s-gap></div><div id=s-t></div><div id=s-ab></div><div id=s-fx></div><div style="height:100px"></div></div>
<div id=f><div id=f-gap></div><div id=f-t></div></div>
<div id=under></div>
<a name=named id=nm>named</a>
<div id=tr>t</div>
<div id="a b">spaced</div>
<a id=lk href="#s-t" style="position:fixed;left:600px;top:0">go</a>
<a id=lk2 href="#s-t"><span id=lk2s style="position:fixed;left:600px;top:40px">go</span></a>
</body>`;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.route('http://probe.test/**', r => r.fulfill({ contentType: 'text/html', body: html }));
await p.goto('http://probe.test/page');
const S = ['s', 'f'];
const state = () => p.evaluate(`${JSON.stringify(S)}.map(i=>{var e=document.getElementById(i);return e.scrollLeft||e.scrollTop?i+'='+e.scrollLeft+','+e.scrollTop:''}).filter(Boolean).join(' ')+' win='+scrollX+','+scrollY`);
const reset = () => p.evaluate(`${JSON.stringify(S)}.forEach(i=>{var e=document.getElementById(i);e.scrollTop=0;e.scrollLeft=0});history.replaceState(null,'','/page');scrollTo(0,0)`);
async function run(name, js, setup) {
  await reset();
  if (setup) await p.evaluate(setup);
  await p.evaluate(js);
  await new Promise(r => setTimeout(r, 200));
  console.log(name, await state(), p.url().replace('http://probe.test', ''));
}
console.log(b.version());
const siv = id => `document.getElementById(${JSON.stringify(id)}).scrollIntoView()`;
await run('in-static-scroller', siv('s-t'));
await run('abs-escapes-static-scroller', siv('s-ab'));
await run('fixed-in-static-scroller', siv('s-fx'), `scrollTo(0,200)`);
await run('in-fixed-scroller', siv('f-t'), `scrollTo(0,200)`);
await run('fixed-scroller-itself', siv('f'), `scrollTo(0,200)`);
await run('transformed', siv('tr'));
await run('link-click', `document.getElementById('lk').click()`);
await run('hash-name', `location.hash='named'`);
await run('hash-encoded', `location.hash='a%20b'`);
await run('hash-case', `location.hash='#TOP'`, `scrollTo(0,50)`);
await run('hash-case-id', `location.hash='#S-T'`);
await run('replace', `location.replace('#s-t')`);
await run('assign', `location.assign('#s-t')`);
await p.goto('http://probe.test/load#s-t');
await new Promise(r => setTimeout(r, 300));
console.log('load-with-fragment', await state());
await p.goto('http://probe.test/load#named');
await new Promise(r => setTimeout(r, 300));
console.log('load-with-name', await state());
await p.goto('http://probe.test/load#nope');
await new Promise(r => setTimeout(r, 300));
console.log('load-no-match', await state());
await b.close();
