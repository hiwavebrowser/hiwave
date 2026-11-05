import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const page2 = `<!doctype html><style>body{margin:0;height:3000px}#sp0{height:1000px}#s{overflow:auto;width:200px;height:100px}#s-gap{height:300px}#s-t{height:20px}#s-ab{position:absolute;left:10px;top:1800px;width:20px;height:20px}#s-fx{position:fixed;left:400px;top:500px;width:20px;height:20px}#f{position:fixed;left:400px;top:0;width:100px;height:100px;overflow:auto}#f-gap{height:300px}#f-t{height:20px}#nm{display:block;height:20px}#under{height:600px}</style><body><div id=sp0></div><div id=s><div id=s-gap></div><div id=s-t></div><div id=s-ab></div><div id=s-fx></div><div style="height:100px"></div></div><div id=f><div id=f-gap></div><div id=f-t></div></div><div id=under></div><a name=named id=nm>named</a><div id="a b" style="height:20px">spaced</div><a id=lk href="#s-t" style="position:fixed;left:600px;top:0">go</a><script>window.hc=0;onhashchange=function(){hc++}</script></body>`;
const b = await chromium.launch();
console.log(b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.route('http://probe.test/**', r => r.fulfill({ contentType: 'text/html', body: page2 }));
const st = () => p.evaluate(`'s='+document.getElementById('s').scrollTop+' win='+scrollX+','+scrollY+' hc='+hc+' url='+location.pathname+location.hash+' len='+history.length`);
const w = ms => new Promise(r => setTimeout(r, ms));
async function fresh(path='/page') { await p.goto('http://probe.test'+path); await w(200); }
// D: test-page numbers
for (const [n, js] of [['hash-encoded', `location.hash='a%20b'`], ['hash-case-id', `scrollTo(0,50);location.hash='#S-T'`], ['hash-named', `location.hash='named'`]]) { await fresh(); await p.evaluate(js); await w(200); console.log(n, await st()); }
// A: redundant hash set after a user scroll
await fresh(); await p.evaluate(`location.hash='#s-t'`); await w(300); console.log('A1 after first', await st());
await p.mouse.move(100, 300); await p.mouse.wheel(0, -500); await w(400); await p.evaluate(`document.getElementById('s').scrollTop=0`); await w(200); console.log('A2 after user scroll', await st());
await p.evaluate(`location.hash='#s-t'`); await w(300); console.log('A3 same hash again', await st());
await p.evaluate(`location.hash='s-t'`); await w(300); console.log('A4 same hash no #', await st());
// B: href to same URL
await p.mouse.wheel(0, -500); await w(400); await p.evaluate(`document.getElementById('s').scrollTop=0`); await w(200); console.log('B1 user scroll', await st());
await p.evaluate(`location.href=location.href`); await w(300); console.log('B2 href=href', await st());
// C: empty hash from no-fragment URL
await fresh(); await p.evaluate(`scrollTo(0,50)`); await w(100); await p.evaluate(`location.hash=''`); await w(300); console.log('C1 hash="" from none', await st());
await fresh(); await p.evaluate(`scrollTo(0,50)`); await w(100); await p.evaluate(`location.hash='#'`); await w(300); console.log('C2 hash="#" from none', await st());
// C3: hash='' when there is a fragment
await fresh('/page#s-t'); await p.mouse.wheel(0,-300); await w(400); console.log('C3a', await st()); await p.evaluate(`location.hash=''`); await w(300); console.log('C3b hash="" from #s-t', await st());
// F: load with fragment
await fresh('/page#s-t'); console.log('F load', await st());
// G: link click twice
await fresh(); await p.click('#lk'); await w(300); console.log('G1', await st());
await p.mouse.wheel(0,-2000); await w(400); await p.evaluate(`document.getElementById('s').scrollTop=0`); await w(100);
await p.click('#lk'); await w(300); console.log('G2 again', await st());
await b.close();
