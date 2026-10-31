// C2(c): what scrollIntoView and fragment navigation scroll, in Chromium. Hand-made page, no site.
// usage: node c2c_probe.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = `<!doctype html><style>body{margin:0;height:3000px;width:3000px}
#out{overflow:auto;width:300px;height:200px;position:absolute;left:0;top:1000px}
#gap{height:400px}
#in{overflow:auto;width:200px;height:100px;border:5px solid #000;padding:7px}
#in-gap{height:300px;width:600px}
#t{height:20px;width:30px;margin-left:400px}
#after{height:300px}
#hid{overflow:hidden;width:100px;height:100px;position:absolute;left:500px;top:0}
#hid-t{margin-top:400px;height:10px}
#clip{overflow:clip;width:100px;height:100px;position:absolute;left:650px;top:0}
#clip-t{margin-top:400px;height:10px}
#st{overflow:auto;width:100px;height:100px;position:absolute;left:800px;top:0}
#st-gap{height:300px}
#ab{position:absolute;left:10px;top:1800px;width:20px;height:20px}
#rel{overflow:auto;position:relative;width:100px;height:100px;position:absolute;left:950px;top:0}
#rel-gap{height:300px}
#ab2{position:absolute;left:0;top:250px;width:20px;height:20px}
#fx{position:fixed;left:0;top:500px;width:20px;height:20px}
#nd{display:none}
#big-s{overflow:auto;width:100px;height:100px;position:absolute;left:1100px;top:0}
#big{height:500px;margin-top:50px}
#sm{overflow:auto;width:100px;height:100px;position:absolute;left:1250px;top:0}
#sm-t{margin-top:300px;height:10px;scroll-margin-top:20px}
#sp{overflow:auto;width:100px;height:100px;position:absolute;left:1400px;top:0;scroll-padding-top:15px}
#sp-t{margin-top:300px;height:10px}
#inl{overflow:auto;width:100px;height:100px;position:absolute;left:1550px;top:0}
#inl-gap{height:300px}
</style><body>
<div id=out><div id=gap></div><div id=in><div id=in-gap></div><div id=t></div><div id=after></div></div></div>
<div id=hid><div id=hid-t></div></div>
<div id=clip><div id=clip-t></div></div>
<div id=st><div id=st-gap></div><div id=ab></div></div>
<div id=rel><div id=rel-gap></div><div id=ab2></div></div>
<div id=fx></div><div id=nd></div>
<div id=big-s><div id=big></div></div>
<div id=sm><div id=sm-t></div></div>
<div id=sp><div id=sp-t></div></div>
<div id=inl><div id=inl-gap></div><span id=inl-t>x</span></div>
<a id=link href="#t" style="position:fixed;left:700px;top:500px">go</a>
</body>`;
const S = ['in', 'out', 'hid', 'clip', 'st', 'rel', 'big-s', 'sm', 'sp', 'inl'];
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.route('http://probe.test/**', r => r.fulfill({ contentType: 'text/html', body: html }));
await p.goto('http://probe.test/page');
const state = () => p.evaluate(`${JSON.stringify(S)}.map(i=>{var e=document.getElementById(i);return e.scrollLeft||e.scrollTop?i+'='+e.scrollLeft+','+e.scrollTop:''}).filter(Boolean).join(' ')+' win='+scrollX+','+scrollY`);
const reset = () => p.evaluate(`${JSON.stringify(S)}.forEach(i=>{var e=document.getElementById(i);e.scrollTop=0;e.scrollLeft=0});scrollTo(0,0);location.hash='';scrollTo(0,0)`);
async function siv(name, id, arg, setup) {
  await reset();
  if (setup) await p.evaluate(setup);
  await new Promise(r => setTimeout(r, 60));
  await p.evaluate(`window.ev=[];${JSON.stringify(S)}.forEach(i=>document.getElementById(i).onscroll=function(e){ev.push(i+':'+e.bubbles)});document.onscroll=function(){ev.push('doc')}`);
  const out = await p.evaluate(`document.getElementById(${JSON.stringify(id)}).scrollIntoView(${arg}); var r=document.getElementById(${JSON.stringify(id)}).getBoundingClientRect(); [r.left,r.top].join(',')+' ev-sync='+ev.length`);
  await new Promise(r => setTimeout(r, 120));
  console.log(name, await state(), 'rect', out, 'events', await p.evaluate(`ev.join(' ')`));
}
console.log(b.version());
await siv('default', 't', '');
await siv('true', 't', 'true');
await siv('false', 't', 'false');
await siv('start-start', 't', '{block:"start",inline:"start"}');
await siv('center-center', 't', '{block:"center",inline:"center"}');
await siv('end-end', 't', '{block:"end",inline:"end"}');
await siv('nearest-nearest', 't', '{block:"nearest",inline:"nearest"}');
await siv('smooth-sync', 't', '{behavior:"instant"}');
await siv('from-below-nearest', 't', '{block:"nearest"}', `document.getElementById('in').scrollTop=280;document.getElementById('out').scrollTop=9999;scrollTo(0,2000)`);
await siv('visible-nearest', 'gap', '{block:"nearest"}', `scrollTo(0,1000)`);
await siv('hidden', 'hid-t', '');
await siv('clip', 'clip-t', '');
await siv('abs-escapes-static', 'ab', '');
await siv('abs-in-positioned', 'ab2', '');
await siv('fixed', 'fx', '', `scrollTo(0,200)`);
await siv('display-none', 'nd', '', `scrollTo(0,200)`);
await siv('big-start', 'big', '');
await siv('big-nearest', 'big', '{block:"nearest"}');
await siv('big-nearest-inside', 'big', '{block:"nearest"}', `document.getElementById('big-s').scrollTop=100`);
await siv('big-center', 'big', '{block:"center"}');
await siv('scroll-margin', 'sm-t', '');
await siv('scroll-padding', 'sp-t', '');
await siv('inline-box', 'inl-t', '');
await siv('root', 'out', '');
await siv('html', 'link', '', `scrollTo(0,50)`);
await p.evaluate(`document.documentElement.scrollIntoView()`);
console.log('documentElement', await state());
await siv('body', 'in', '{block:"end"}');
async function frag(name, act, setup) {
  await reset();
  if (setup) await p.evaluate(setup);
  await new Promise(r => setTimeout(r, 60));
  await p.evaluate(`window.ev=[];window.onhashchange=function(){ev.push('hash:'+scrollY+':'+document.getElementById('in').scrollTop)}`);
  await act();
  await new Promise(r => setTimeout(r, 200));
  console.log(name, await state(), 'url', p.url().replace('http://probe.test', ''), 'ev', await p.evaluate(`ev.join(' ')`));
}
await frag('click-link', () => p.click('#link'));
await frag('location-hash', () => p.evaluate(`location.hash='#t'`));
await frag('location-href', () => p.evaluate(`location.href='#in'`));
await frag('hash-hidden', () => p.evaluate(`location.hash='#hid-t'`));
await frag('hash-margin', () => p.evaluate(`location.hash='#sm-t'`));
await frag('hash-none', () => p.evaluate(`location.hash='#nope'`), `scrollTo(0,50)`);
await frag('hash-top', () => p.evaluate(`location.hash='#top'`), `scrollTo(0,50);document.getElementById('in').scrollTop=40`);
await frag('hash-empty', () => p.evaluate(`location.hash='#'`), `scrollTo(0,50);document.getElementById('in').scrollTop=40`);
await frag('same-hash-again', () => p.evaluate(`location.hash='#t';scrollTo(0,0);document.getElementById('in').scrollTop=0;location.hash='#t'`));
await frag('pushstate', () => p.evaluate(`history.pushState(null,'','#t')`));
await p.goto('http://probe.test/load#t');
await new Promise(r => setTimeout(r, 300));
console.log('load-with-fragment', await state());
await b.close();
