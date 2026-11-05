// CH2.B8 reduced pages (viewport 300x200): a percentage height chain from
// the ICB through html/body to a flex container. Reads html, body, .row.
const SIDE =
  "<aside class=side><section><div style='padding:8px;color:#000'>Workspaces</div>" +
  "<button style='background:rgb(255,0,0);width:120px;height:30px;border:0'>Open</button>" +
  "<div style='background:rgb(0,0,255);width:50px;height:20px'></div></section></aside>" +
  '<main class=main>main</main>';
const SIDE_CSS =
  '.side{width:0;min-width:0;overflow:hidden;display:flex;flex-direction:column;flex-shrink:0;background:#eee}' +
  '.main{flex:1;background:#fff}';
const doc = (css, body) =>
  `<!doctype html><html><head><style>${css}</style></head><body>${body}</body></html>`;
export const variants = [
  ['b2_page', doc('html,body{margin:0;height:100%;background:#fff}.row{display:flex;height:100%}' + SIDE_CSS, `<div class=row>${SIDE}</div>`)],
  ['flex_row_text', doc('html,body{margin:0;height:100%}.row{display:flex;height:100%}', '<div class=row><div>a</div></div>')],
  ['flex_col_text', doc('html,body{margin:0;height:100%}.row{display:flex;flex-direction:column;height:100%}', '<div class=row><div>a</div></div>')],
  ['block_text', doc('html,body{margin:0;height:100%}.row{height:100%}', '<div class=row><div>a</div></div>')],
  ['grid_text', doc('html,body{margin:0;height:100%}.row{display:grid;height:100%}', '<div class=row><div>a</div></div>')],
  ['body_margin', doc('html,body{height:100%}.row{display:flex;height:100%}', '<div class=row><div>a</div></div>')],
  ['html50_body_tall', doc('html{height:50px}body{margin:8px}.row{height:120px}', '<div class=row>a</div>')],
  ['html300_body_short', doc('html{height:300px}body{margin:0}.row{height:20px}', '<div class=row>a</div>')],
  ['html_auto_body_margin', doc('body{margin:8px}.row{height:20px}', '<div class=row>a</div>')],
  ['no_doctype_flex', `<style>html,body{margin:0;height:100%}.row{display:flex;height:100%}</style><div class=row><div>a</div></div>`],
];
export const JS = `(function(){function h(e){return Math.round(e.getBoundingClientRect().height)}
return 'html='+h(document.documentElement)+' body='+h(document.body)+' row='+h(document.querySelector('.row'));})()`;
