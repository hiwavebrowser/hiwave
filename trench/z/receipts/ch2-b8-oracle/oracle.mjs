// CH2.B8 oracle. Usage: node oracle.mjs
import { chromium } from '../parity_oracle/node_modules/playwright/index.mjs';
import { getDeterministicLaunchOptions } from '../parity_oracle/deterministic.mjs';
import { variants, JS } from './variants.mjs';

const b = await chromium.launch(getDeterministicLaunchOptions());
console.log('chromium', b.version());
const p = await b.newPage({ viewport: { width: 300, height: 200 } });
for (const [name, html] of variants) {
  await p.setContent(html);
  console.log(name + ': ' + (await p.evaluate(JS)));
}
await b.close();
