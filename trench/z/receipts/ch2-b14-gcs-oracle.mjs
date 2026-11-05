// Chromium's getComputedStyle for unitless 0 vs 0px vs unset (CH2.B14 audit).
import { chromium } from '../tools/parity_oracle/node_modules/playwright/index.mjs';
const b = await chromium.launch();
const p = await b.newPage();
const props = ['column-gap', 'row-gap', 'letter-spacing', 'word-spacing', 'line-height', 'text-indent',
  'outline-offset', 'top', 'flex-basis', 'margin-top', 'padding-top', 'border-top-width'];
for (const z of ['0', '0px', null]) {
  const decl = z === null ? 'border-top-style:solid' : props.map(q => q + ':' + z).join(';') + ';border-top-style:solid;position:relative';
  const mcol = z === null ? '' : 'column-gap:' + z;
  await p.setContent('<div id=t style="display:flex;' + decl + '">x</div><div id=m style="column-count:2;' + mcol + '">y</div>');
  const out = await p.evaluate((props) => {
    const s = getComputedStyle(document.getElementById('t'));
    return props.map(q => q + '=' + s.getPropertyValue(q)).join(' ') + ' | mcol column-gap=' + getComputedStyle(document.getElementById('m')).columnGap;
  }, props);
  console.log(z, out);
}
await b.close();
