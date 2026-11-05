import json, sys

H = '<!doctype html><html><head><style>body{margin:0;font:16px/20px Arial}%s</style></head><body>%s</body></html>'
cases = [
    ("margin-p", "p{margin:Z}", "<div id=a><p id=p>x</p><p id=q>y</p></div>"),
    ("margin-top-p", "p{margin-top:Z;margin-bottom:Z}", "<div id=a><p id=p>x</p><p id=q>y</p></div>"),
    ("margin-body", "body{margin:Z!important}", "<div id=a style='height:10px'></div>"),
    ("padding-ul", "ul{padding:Z;margin:0}", "<ul id=u><li id=l>x</li></ul>"),
    ("padding-left-ul", "ul{padding-left:Z;margin:0}", "<ul id=u><li id=l>x</li></ul>"),
    ("border-width-solid", "#b{border:Z solid red;width:50px;height:10px}", "<div id=b></div><div id=c>y</div>"),
    ("border-top-width", "#b{border-style:solid;border-top-width:Z;width:50px;height:10px}", "<div id=b></div><div id=c>y</div>"),
    ("border-width-input", "input{border:Z;padding:0;width:100px;height:20px;box-sizing:border-box}", "<input id=i><div id=c>y</div>"),
    ("inset-top-left-abs", "#r{position:relative;width:200px;height:100px;margin:10px}#t{position:absolute;top:Z;left:Z;width:10px;height:10px}", "<div id=r><span>abc</span><div id=t></div></div>"),
    ("inset-right-bottom-abs", "#r{position:relative;width:200px;height:100px;margin:10px}#t{position:absolute;right:Z;bottom:Z;width:10px;height:10px}", "<div id=r><div id=t></div></div>"),
    ("inset-all-abs", "#r{position:relative;width:200px;height:100px;margin:10px}#t{position:absolute;top:Z;right:Z;bottom:Z;left:Z}", "<div id=r><div id=t></div></div>"),
    ("inset-shorthand-fixed", "#t{position:fixed;inset:Z}", "<div style='height:30px'></div><div id=t></div>"),
    ("inset-rel-top", "#t{position:relative;top:Z;left:Z;height:10px}", "<div style='height:30px'></div><div id=t></div>"),
    ("sticky-top", "#s{position:sticky;top:Z;height:10px}", "<div style='height:30px'></div><div id=s></div><div style='height:900px'></div>"),
    ("gap-flex", "#f{display:flex;gap:Z;width:200px}#f>div{width:20px;height:10px}", "<div id=f><div id=a></div><div id=b></div></div>"),
    ("column-gap-flex", "#f{display:flex;column-gap:Z;width:200px}#f>div{width:20px;height:10px}", "<div id=f><div id=a></div><div id=b></div></div>"),
    ("gap-grid", "#g{display:grid;grid-template-columns:20px 20px;gap:Z;width:200px}#g>div{height:10px}", "<div id=g><div id=a></div><div id=b></div><div id=c></div></div>"),
    ("row-gap-grid", "#g{display:grid;grid-template-columns:20px;row-gap:Z;width:200px}#g>div{height:10px}", "<div id=g><div id=a></div><div id=b></div></div>"),
    ("column-gap-multicol", "#m{column-count:2;column-gap:Z;width:200px;font:10px/10px Arial}#m>div{height:10px}", "<div id=m><div id=a></div><div id=b></div></div>"),
    ("flex-basis", "#f{display:flex;width:200px}#a{flex-basis:Z;flex-grow:1;height:10px}#b{width:50px;height:10px}", "<div id=f><div id=a>xxxxxxxx</div><div id=b></div></div>"),
    ("flex-shorthand-1-1-0", "#f{display:flex;width:200px}#f>div{flex:1 1 Z;height:10px}", "<div id=f><div id=a>xxxxxxxxxxxx</div><div id=b>y</div></div>"),
    ("line-height", "#l{line-height:Z;font-size:16px}", "<div id=l><span>x</span></div><div id=n>y</div>"),
    ("text-indent", "#t{text-indent:Z}#t span{display:inline-block;width:10px;height:10px}", "<div id=t><span id=s></span></div>"),
    ("letter-spacing", "#t{letter-spacing:Z;display:inline-block}", "<div><span id=t>abcdef</span></div>"),
    ("word-spacing", "#t{word-spacing:Z;display:inline-block}", "<div><span id=t>a b c d</span></div>"),
    ("border-spacing-table", "table{border-spacing:Z}td{padding:0;width:10px;height:10px}", "<table id=t><tr><td id=c1></td><td id=c2></td></tr></table>"),
    ("outline-offset", "#o{outline:2px solid red;outline-offset:Z;width:10px;height:10px}", "<div id=o></div>"),
    ("grid-template-zero-track", "#g{display:grid;grid-template-columns:Z 1fr;width:200px}#g>div{height:10px}", "<div id=g><div id=a></div><div id=b></div></div>"),
    ("margin-auto-center", "#c{width:100px;height:10px;margin:Z auto}", "<div id=c></div>"),
    ("min-width-flex-item", "#f{display:flex;width:100px}#a{min-width:Z;flex:1 1 auto;overflow:hidden;height:10px}#a span{display:inline-block;width:300px}", "<div id=f><div id=a><span></span></div><div id=b style='width:50px;height:10px'></div></div>"),
    ("vertical-align-length", "#v{vertical-align:Z;display:inline-block;width:10px;height:10px}", "<div id=d><span>x</span><span id=v></span></div>"),
    ("translate-transform", "#t{transform:translate(Z,Z);width:10px;height:10px}", "<div id=t></div>"),
    ("table-padding-cell", "table{border-collapse:collapse}td{padding:Z;width:10px;height:10px}", "<table><tr><td id=c1>x</td><td id=c2>y</td></tr></table>"),
    ("fieldset-padding", "fieldset{padding:Z;margin:0;border:0}", "<fieldset id=f><div id=d style='height:10px'></div></fieldset>"),
    ("h1-margin", "h1{margin:Z}", "<h1 id=h>x</h1><div id=n>y</div>"),
    ("button-padding", "button{padding:Z;border:0;font:16px/20px Arial}", "<button id=b>x</button>"),
]
out = {"viewport": [400, 300], "boxes": "xywh", "cases": []}
for n, css, body in cases:
    for z, suf in (("0", ""), ("0px", "-px")):
        out["cases"].append({"name": n + suf, "html": H % (css.replace("Z", z), body)})
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(len(out["cases"]))
