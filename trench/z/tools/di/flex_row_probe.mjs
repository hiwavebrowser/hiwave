// CA1-2: row geometry of the flex keywords and three more invalid values, in Chromium.
// usage: node flex_row_probe.mjs <worktree>/tools/parity_oracle/node_modules
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = '<!doctype html><style>body{margin:0} .r{display:flex;width:400px} .r div{height:10px} #a{width:100px;flex:none} #b{flex:auto} #d,#e{width:500px;flex:none} #f,#g{flex:10px}</style><body><div class=r><div id=a>a</div><div id=b>b</div></div><div class=r><div id=d>d</div><div id=e>e</div></div><div class=r><div id=f>f</div><div id=g>g</div></div></body>';
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.setContent(html);
console.log(b.version());
console.log(await p.evaluate(`[].map.call(document.querySelectorAll('[id]'), function (e) { var r = e.getBoundingClientRect(); return e.id + ':' + r.x + ',' + r.width; }).join(' ')`));
await p.setContent('<!doctype html><div id=x></div>');
console.log((await p.evaluate(() => ['1 -5px', 'nan', 'inf', '1e1', '+1', '.5 10px', '1 1 10em', 'min-content', 'unset', 'inherit'].map((v) => {
  const st = document.createElement('style');
  st.textContent = '#x{flex:7 8 9px} #x{flex:' + v + '}';
  document.head.appendChild(st);
  const c = getComputedStyle(document.getElementById('x'));
  const line = JSON.stringify(v) + ' -> ' + c.flexGrow + ' ' + c.flexShrink + ' ' + c.flexBasis;
  st.remove();
  return line;
}))).join('\n'));
await b.close();
