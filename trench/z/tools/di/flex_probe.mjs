// CA1-2: the flex shorthand in Chromium. Each value is set over `flex: 7 8 9px` so a dropped declaration shows.
// usage: node flex_probe.mjs <worktree>/tools/parity_oracle/node_modules
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const values = ['none', 'auto', 'initial', 'NONE', 'Auto', 'content', '10px', '50%', '0', '1', '2 3', '1 0', '2 10px', '10px 2', '10px 2 3', '2 3 10px', '10px 1 0', '0 0 0', '1 1 0', '0 2 3', '1 2 3', '2 10px 3', '10px 20px', 'auto 2', '2 auto', 'auto 2 3', '2 3 auto', 'content 2 3', 'calc(10px + 1px) 2 3', 'none 1', '1 none', 'none auto', 'bogus', '-1', '1 -1', '10px -1', '0px 1 1', '1 1 1 1'];
const b = await chromium.launch();
const p = await b.newPage();
await p.setContent('<!doctype html><div id=x></div>');
const out = await p.evaluate((values) => values.map((v) => {
  const st = document.createElement('style');
  st.textContent = '#x{flex:7 8 9px} #x{flex:' + v + '}';
  document.head.appendChild(st);
  const c = getComputedStyle(document.getElementById('x'));
  const line = JSON.stringify(v) + ' -> ' + c.flexGrow + ' ' + c.flexShrink + ' ' + c.flexBasis;
  st.remove();
  return line;
}), values);
console.log(b.version());
console.log(out.join('\n'));
await b.close();
