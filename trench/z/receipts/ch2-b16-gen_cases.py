import json, sys

H = '<!doctype html><html><head><style>body{margin:0}%s</style></head><body>%s</body></html>'
cases = [
    ("float-only-children-pct-height", "#p{height:200px;width:300px}#f{float:left;width:50px;height:50%}", "<div id=p><div id=f></div></div>"),
    ("two-floats-pct-height", "#p{height:200px;width:300px}.f{float:left;width:50px;height:50%}", "<div id=p><div id=a class=f></div><div id=b class=f></div></div>"),
    ("float-with-inflow-sibling", "#p{height:200px;width:300px}#f{float:left;width:50px;height:50%}", "<div id=p><div id=f></div><div id=s style='height:10px'></div></div>"),
    ("float-right-pct-height", "#p{height:200px;width:300px}#f{float:right;width:50px;height:50%}", "<div id=p><div id=f></div></div>"),
    ("float-pct-of-auto-parent", "#p{width:300px}#f{float:left;width:50px;height:50%}", "<div id=p><div id=f></div><div id=s style='height:40px'></div></div>"),
    ("float-nested-pct-chain", "#p{height:200px;width:300px}#q{height:50%}#f{float:left;width:50px;height:50%}", "<div id=p><div id=q><div id=f></div></div></div>"),
    ("float-in-max-height-parent", "#p{height:200px;max-height:150px;width:300px}#f{float:left;width:50px;height:100%}", "<div id=p><div id=f></div></div>"),
    ("float-min-height-pct", "#p{height:200px;width:300px}#f{float:left;width:50px;min-height:25%}", "<div id=p><div id=f></div></div>"),
]
out = {"viewport": [400, 600], "boxes": "xywh", "cases": []}
for n, css, body in cases:
    out["cases"].append({"name": n, "html": H % (css, body)})
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(len(out["cases"]))
