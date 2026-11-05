// CH2.B3 oracle: computed background-color of the button_background_tests shapes in the pinned Chromium.
import { chromium } from '/Users/petecopeland/Repos/.worktrees/z-ch2-b3/tools/parity_oracle/node_modules/playwright/index.mjs';
import { getDeterministicLaunchOptions } from '/Users/petecopeland/Repos/.worktrees/z-ch2-b3/tools/parity_oracle/deterministic.mjs';

const html = `<body style="background:#1e293b">
<button id=v style="border:none;background:transparent;padding:4px">v</button>
<button id=L style="border:none;background:transparent;display:flex;width:28px;height:28px">L</button>
<input id=I type="button" value="I" style="border:none;background-color:transparent">
<button id=plain>plain</button><input id=Go type="submit" value="Go"><input id=R type="reset" value="R">
<button id=c style="background:rgb(1,2,3)">c</button></body>`;
const b = await chromium.launch(getDeterministicLaunchOptions());
console.log('chromium', b.version());
const p = await b.newPage({ viewport: { width: 600, height: 400 } });
await p.setContent(html);
console.log(await p.evaluate(() => JSON.stringify(['v', 'L', 'I', 'plain', 'Go', 'R', 'c'].map(id => [id, getComputedStyle(document.getElementById(id)).backgroundColor]))));
await p.setContent('<body style="font:12px Arial"><button id=w1 style="border:none;padding:4px">\n                    v\n            </button><button id=w2 style="border:none;padding:4px">v</button></body>');
console.log(await p.evaluate(() => JSON.stringify(['w1','w2'].map(id => [id, document.getElementById(id).getBoundingClientRect().width]))));
await b.close();
