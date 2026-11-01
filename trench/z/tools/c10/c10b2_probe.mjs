// C10(b2): the 3D transform functions and value forms the parser drops, in Chromium 143.
// A 100x50 block at (20,10), each transform; prints the rect, or the computed value when it was refused.
// usage: node c10b2_probe.mjs <dir holding node_modules/playwright>
import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const values = [
  'translate3d(5px,6px,0)', 'translate3d(5px,6px,100px)', 'translate3d(-50%,-50%,0)', 'translateZ(10px)', 'translateZ(0)',
  'scale3d(2,3,1)', 'scale3d(2,3,5)', 'scaleZ(2)',
  'rotateZ(90deg)', 'rotate3d(0,0,1,90deg)', 'rotate3d(0,0,2,90deg)', 'rotateX(60deg)', 'rotateY(60deg)', 'rotate3d(1,0,0,60deg)',
  'matrix3d(1,0,0,0, 0,1,0,0, 0,0,1,0, 7,9,0,1)', 'matrix3d(2,0,0,0, 0,3,0,0, 0,0,1,0, 7,9,5,1)',
  'perspective(500px)', 'perspective(500px) translateX(10px)', 'perspective(none)', 'perspective(500px) translateZ(100px)', 'perspective(500px) rotateY(60deg)',
  'translate3d(5px,6px)', 'translateZ(10%)', 'scale3d(2,3)', 'matrix3d(1,0,0,1)', 'rotate3d(0,0,0,90deg)',
  'translate3d(5px 6px 0)', 'translate(5px 6px)', 'scale(2 3)', 'rotate(90)', 'rotate(0)', 'translate(5,6)', 'translate(0,0)',
  'scale(50%)', 'scale(50%,200%)', 'scaleX(50%)', 'scale3d(50%,50%,1)',
  'translate(calc(10px + 5%),0)', 'translateX(calc(100% - 10px))', 'translate(1em,1rem)', 'translate(1vw,1vh)',
  'TRANSLATE(5px,6px)', 'translateX(5px) nonsense(1)', 'none', 'translate(5px,6px) ',
  'rotate(0.25turn)', 'rotate(-90deg)', 'skew(45deg,0)',
];
const b = await chromium.launch();
console.log('chromium', b.version());
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.setContent('<!doctype html><style>body{margin:0}#b{position:absolute;left:20px;top:10px;width:100px;height:50px;font-size:10px}html{font-size:10px}</style><div id=b></div>');
for (const v of values) {
  const out = await p.evaluate(v => {
    const e = document.getElementById('b');
    e.style.transform = '';
    e.style.transform = v;
    const r = e.getBoundingClientRect();
    return [r.x, r.y, r.width, r.height].map(n => +n.toFixed(3)).join(' ') + (e.style.transform ? '' : '   REFUSED');
  }, v);
  console.log(JSON.stringify(v).padEnd(52), out);
}
await b.close();
