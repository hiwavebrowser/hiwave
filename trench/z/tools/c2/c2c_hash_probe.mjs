// C2(c) R1 finding 1: location.hash = '' / '#' / same, with and without a current fragment.
// Page: PAGE from scroll_into_view_tests.rs. usage: node c2c_hash_probe.mjs <dir holding node_modules/playwright> <page.html>
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = readFileSync(process.argv[3], 'utf8');
const b = await chromium.launch();
console.log(b.version());
async function run(name, path, js) {
  const p = await b.newPage({ viewport: { width: 800, height: 600 } });
  await p.route('http://probe.test/**', r => r.fulfill({ contentType: 'text/html', body: html }));
  await p.goto('http://probe.test' + path);
  await new Promise(r => setTimeout(r, 100));
  await p.evaluate(`window.hc=0;window.sc=0;onhashchange=()=>hc++;scrollTo(0,50);document.getElementById('in').scrollTop=40;window.len0=history.length`);
  await new Promise(r => setTimeout(r, 100));
  const sync = await p.evaluate(`${js};'sync-win='+scrollY+' sync-hc='+hc`);
  await new Promise(r => setTimeout(r, 300));
  const st = await p.evaluate(`'win='+scrollX+','+scrollY+' in='+document.getElementById('in').scrollTop+' hashchange='+hc+' histDelta='+(history.length-len0)+' href='+location.href.replace('http://probe.test','')+' hash='+JSON.stringify(location.hash)`);
  console.log(name.padEnd(28), sync, '|', st);
  await p.close();
}
await run("nofrag hash=''", '/page', `location.hash=''`);
await run("nofrag hash='#'", '/page', `location.hash='#'`);
await run("frag(#nope) hash=''", '/page#nope', `location.hash=''`);
await run("frag(#nope) hash='#'", '/page#nope', `location.hash='#'`);
await run("frag(#t) hash=''", '/page#t', `scrollTo(0,50);document.getElementById('in').scrollTop=40;location.hash=''`);
await run("empty(#) hash=''", '/page#', `location.hash=''`);
await run("empty(#) hash='#'", '/page#', `location.hash='#'`);
await run("frag(#nope) hash='nope'", '/page#nope', `location.hash='nope'`);
await run("frag(#nope) hash='#nope'", '/page#nope', `location.hash='#nope'`);
await run("frag(#t) hash='t' (same)", '/page#t', `scrollTo(0,50);document.getElementById('in').scrollTop=40;location.hash='t'`);
await run("nofrag href=own+'#'", '/page', `location.href=location.href+'#'`);
await b.close();
