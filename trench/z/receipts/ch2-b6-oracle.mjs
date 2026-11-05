// CH2.B6 oracle: span widths of the chrome system-font probe in the pinned Chromium.
import { readFileSync, writeFileSync } from 'node:fs';
import { chromium } from '/Users/petecopeland/Repos/.worktrees/z-ch2-b6/tools/parity_oracle/node_modules/playwright/index.mjs';
import { getDeterministicLaunchOptions } from '/Users/petecopeland/Repos/.worktrees/z-ch2-b6/tools/parity_oracle/deterministic.mjs';

const dir = '/Users/petecopeland/Repos/.worktrees/z-ch2-b6/target/b6/';
const b = await chromium.launch(getDeterministicLaunchOptions());
const p = await b.newPage({ viewport: { width: 600, height: 800 } });
await p.goto('file://' + dir + (process.argv[2]||'probe.html'));
const out = await p.evaluate(() => [...document.querySelectorAll('[id]')].map(s => {
  const r = s.getBoundingClientRect();
  return [s.id, s.getAttribute('style'), r.x, r.y, r.width, r.height];
}));
writeFileSync(dir + (process.argv[3]||'chrome-widths.json'), JSON.stringify({ chromium: b.version(), rows: out }, null, 1));
console.log('chromium', b.version(), out.length);
await b.close();
