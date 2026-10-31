// DI: why google's chips are hidden in Chromium: the display chain and every display: inherit / contents rule.
// usage: node google_chain.mjs <node_modules> <user agent>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch();
const c = await b.newContext({ viewport: { width: 1280, height: 800 }, userAgent: process.argv[3] });
const p = await c.newPage();
await p.goto('https://www.google.com/', { waitUntil: 'load', timeout: 45000 });
await p.waitForTimeout(5000);
console.log(await p.evaluate(`(() => {
  const out = [];
  let e = null;
  for (const s of document.querySelectorAll('span')) if (s.children.length === 0 && s.textContent.trim() === 'Create images') { e = s; break; }
  for (let n = e; n; n = n.parentElement) {
    const cs = getComputedStyle(n);
    const r = n.getBoundingClientRect();
    out.push(n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + '.' + String(n.className.baseVal === undefined ? n.className : '').trim().split(/\\s+/).join('.') + ' display=' + cs.display + ' vis=' + cs.visibility + ' pos=' + cs.position + ' ' + Math.round(r.width) + 'x' + Math.round(r.height) + (n.hidden ? ' [hidden]' : '') + (n.getAttribute('style') ? ' style=' + n.getAttribute('style').slice(0, 80) : ''));
  }
  out.push('--- rules');
  const walk = (rules, ctx) => { for (const r of rules) {
    if (r.cssRules && r.cssRules.length) walk(r.cssRules, (r.conditionText || r.media && r.media.mediaText || '') + ' ' + ctx);
    if (r.style && /inherit|contents/.test(r.style.getPropertyValue('display'))) out.push((ctx ? '@' + ctx + ' ' : '') + r.selectorText.slice(0, 160) + ' { display: ' + r.style.getPropertyValue('display') + ' }');
  } };
  for (const s of document.styleSheets) { try { walk(s.cssRules, ''); } catch (err) { out.push('sheet blocked ' + s.href); } }
  return out.join('\\n');
})()`));
await b.close();
