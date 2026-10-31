// DI: display: inherit under a display: contents parent, in Chromium. Hand-made pages, no site.
// usage: node di_probe.mjs <worktree>/tools/parity_oracle/node_modules
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const expr = `[].map.call(document.querySelectorAll('[id]'), function (e) {
  var r = e.getBoundingClientRect();
  return e.id + ':' + getComputedStyle(e).display + ',' + r.x + ',' + r.y; }).join(' ')`;
const items = '#a,#b,#c{width:50px;height:20px}';
const pages = {
  apple_shape: `<!doctype html><style>body{margin:0} #l{display:flex;width:300px;justify-content:space-between} #m{display:contents} .i{display:inherit} ${items}</style><body><div id=l><div id=m><div id=f class=i><div id=g class=i><div id=a>a</div><div id=b>b</div><div id=c>c</div></div></div></div></div></body>`,
  block_grandparent: `<!doctype html><style>body{margin:0} #l{display:block;width:300px} #m{display:contents} .i{display:inherit} ${items}</style><body><div id=l><div id=m><div id=f class=i><div id=a>a</div><div id=b>b</div></div></div></div></body>`,
  child_redeclares: `<!doctype html><style>body{margin:0} #l{display:flex;width:300px} #m{display:contents} #f{display:inherit} #g{display:block} ${items}</style><body><div id=l><div id=m><div id=f><div id=g><div id=a>a</div><div id=b>b</div></div></div></div></div></body>`,
  plain_child_control: `<!doctype html><style>body{margin:0} #l{display:flex;width:300px} #m{display:contents} ${items}</style><body><div id=l><div id=m><div id=a>a</div><div id=b>b</div></div></div></body>`,
  webkit_box_after_contents: `<!doctype html><style>body{margin:0} #l{display:flex;width:300px} #m{display:contents;display:-webkit-box} #f{display:inherit} ${items}</style><body><div id=l><div id=m><div id=f><div id=a>a</div><div id=b>b</div></div></div></div></body>`,
};
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
console.log(b.version());
for (const [name, html] of Object.entries(pages)) {
  await p.setContent(html);
  console.log(name + ' => ' + await p.evaluate(expr));
}
await b.close();
