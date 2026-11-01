// #853 R1 items in Chromium 143. Each value in a stylesheet after translateX(7px), on a 100x50 box at (20,10), so a refusal reads x 27.
// node c10b2_r1_probe.mjs <dir with node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const values = [
  'perspective(-10px)', 'perspective(10)', 'perspective(0)', 'perspective(10px)', 'perspective(-0px)', 'perspective(calc(-10px))', 'perspective(calc(10px))', 'perspective(none)', 'perspective(NONE)',
  'perspective(+10px)', 'perspective(10%)',
  'rotate(calc(-1 * 45deg))', 'rotate(calc(45deg))', 'rotate(calc(0.25turn + 45deg))', 'rotate(calc(90deg / 2))', 'rotate(calc(2 * (10deg + 35deg)))', 'rotate(calc(1rad - 1rad))', 'rotate(calc(90))', 'rotate(calc(0))',
  'rotate(calc(45deg * 2deg))', 'rotate(calc(45deg + 1))', 'rotate(calc(90deg / 0))', 'rotate(min(90deg, 180deg))', 'rotate(max(90deg, 45deg))', 'rotate(clamp(10deg, 90deg, 180deg))', 'rotate(calc(90deg+45deg))', 'rotate(CALC(90DEG))', 'rotate(calc( 90deg ))',
  'scale(calc(1.5))', 'scale(calc(1 + 0.5))', 'scale(calc(2 * 1.5), calc(4 / 2))', 'scale(calc(1.5deg))', 'scale(calc(50%))', 'scale(min(2, 3))', 'scaleX(calc(2))', 'scale3d(calc(2),1,1)', 'matrix(calc(2),0,0,1,0,0)', 'rotate3d(0,0,calc(1),90deg)', 'skew(calc(45deg))', 'rotateX(calc(60deg))',
  'translate(-50%,-50%) rotate(calc(2 * 45deg))', 'translate(-50%, -50%) rotate(calc(-1 * 45deg)) scale(calc(1 + 1))',
  'translate(5PX,6Px)', 'translateX(5PX)', 'rotate(45DEG)', 'rotate(0.25TURN)', 'rotate(100GRAD)', 'rotate(1RAD)', 'scale(1E1)', 'translateX(1E1px)',
  'NONE', 'None', 'initial', 'INITIAL', 'unset', 'revert', 'revert-layer', 'inherit',
  'scale(inf)', 'scale(infinity)', 'scale(NaN)', 'scale(nan)', 'scale(-inf)', 'matrix(inf,0,0,1,0,0)', 'rotate(infdeg)', 'rotate(nandeg)', 'translateX(infpx)', 'scale(5.)', 'scale(.5)', 'scale(+2)', 'scale(1e400)', 'rotate3d(inf,0,1,90deg)',
  'scale(calc(infinity))', 'rotate(calc(infinity * 1deg))',
];
const b = await chromium.launch();
console.log('chromium', b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
for (const v of values) {
  await p.setContent(`<!doctype html><style>body{margin:0}#w{transform:translateY(3px)}#b{position:absolute;left:20px;top:10px;width:100px;height:50px;transform:translateX(7px);transform:${v}}</style><div id=w><div id=b></div></div>`);
  const out = await p.evaluate(() => {
    const r = document.getElementById('b').getBoundingClientRect();
    return [r.x, r.y, r.width, r.height].map((n) => +n.toFixed(3)).join(' ');
  });
  console.log(`('${v}', "${out}"),`);
}
await b.close();
