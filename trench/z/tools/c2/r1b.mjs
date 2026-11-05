import { createRequire } from 'node:module';
const require = createRequire(process.argv[2] + '/');
const { chromium } = require('playwright');
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.setContent(`<!doctype html><style>body{margin:0;height:3000px}#s{overflow:auto;width:200px;height:100px}#a{position:absolute;left:10px;top:1800px;width:20px;height:20px}</style><body><div id=s><div style=height:300px></div><div id=a></div></div></body>`);
console.log('static-scroller-with-escaping-abs sh=', await p.evaluate(`document.getElementById('s').scrollHeight`));
await p.setContent(`<!doctype html><style>body{margin:0;height:3000px;width:3000px}#a{position:absolute;left:10px;top:5px;width:20px;height:20px}</style><body><div style='margin-left:200px;padding-top:40px'><div id=a></div></div></body>`);
console.log('absx', await p.evaluate(`var r=document.getElementById('a').getBoundingClientRect(); r.left+','+r.top`));
await b.close();
