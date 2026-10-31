// A live page's first screen in Chromium with the engine's product UA, 1280x800.
// usage: node ua_shot.mjs <node_modules> <url> <out.png>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15 HiWave/1.0';
const b = await chromium.launch();
const c = await b.newContext({ viewport: { width: 1280, height: 800 }, userAgent: UA });
const p = await c.newPage();
await p.goto(process.argv[3], { waitUntil: 'load', timeout: 45000 });
await p.waitForTimeout(4000);
await p.screenshot({ path: process.argv[4] });
console.log(b.version());
await b.close();
