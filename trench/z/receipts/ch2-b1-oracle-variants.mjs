// CH2.B1 oracle: the reduced variants of b1_probe_tests.rs in pinned Chromium.
import { readFileSync } from 'node:fs';
import { chromium } from '/Users/petecopeland/Repos/.worktrees/z-ch2-b1/tools/parity_oracle/node_modules/playwright/index.mjs';
import { getDeterministicLaunchOptions } from '/Users/petecopeland/Repos/.worktrees/z-ch2-b1/tools/parity_oracle/deterministic.mjs';

const src = readFileSync(process.argv[2], 'utf8');
const unq = (s) => JSON.parse('"' + s + '"');
const re = /\("([^"]*)", "((?:[^"\\]|\\.)*)"\)/g;
const variants = [];
for (let m; (m = re.exec(src));) variants.push([m[1], unq(m[2])]);
const js = unq(/SMALL_JS: &str = "((?:[^"\\]|\\.)*)";/.exec(src)[1]);
const b = await chromium.launch(getDeterministicLaunchOptions());
console.log('chromium', b.version());
const p = await b.newPage({ viewport: { width: 1280, height: 800 } });
for (const [name, html] of variants) {
  await p.setContent(html);
  console.log(name + ': ' + (await p.evaluate(js).catch((e) => 'ERR ' + html.slice(0, 120) + ' / ' + String(e).slice(0, 80))));
}
await b.close();
