// C2(b): an absolute box inside a static scroller, whose containing block is a positioned scroller. Hand-made page.
// usage: node c2b_escape_probe.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const html = `<!doctype html><style>body{margin:0;height:3000px}
#st{overflow:auto;width:100px;height:100px;position:absolute;left:0;top:300px}
#st2{overflow:auto;width:80px;height:50px}#st2-in{height:200px}
#esc{position:absolute;left:10px;top:10px;width:30px;height:30px;background:#00f}
#rest{height:300px}
</style><body><div id=st><div id=st2><div id=st2-in><div id=esc></div></div></div><div id=rest></div></div></body>`;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.setContent(html);
console.log(b.version());
await p.mouse.move(20, 320);
console.log(await p.evaluate(`document.elementFromPoint(20, 320).id`));
await p.mouse.wheel(0, 50);
await new Promise(r => setTimeout(r, 400));
console.log(await p.evaluate(`'st=' + document.getElementById('st').scrollTop + ' st2=' + document.getElementById('st2').scrollTop + ' win=' + scrollY`));
await b.close();
