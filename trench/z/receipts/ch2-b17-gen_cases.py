import json, sys
B = '<!doctype html><body style="margin:0">'
S = 'display:block;width:40px;height:20px'
cases = [
    ("an-input-with-author-size", B + '<input id=a style="%s">' % S),
    ("a-textarea-with-author-size", B + '<textarea id=a style="%s"></textarea>' % S),
    ("an-input-with-author-padding-and-border", B + '<input id=a style="%s;padding:5px;border:1px solid #000">' % S),
    ("a-textarea-with-author-padding-and-border", B + '<textarea id=a style="%s;padding:5px;border:1px solid #000"></textarea>' % S),
    ("an-input-with-zero-padding-and-border", B + '<input id=a style="%s;padding:0px;border:0px solid">' % S),
    ("an-input-with-border-none", B + '<input id=a style="%s;border:none">' % S),
    ("a-border-box-input", B + '<input id=a style="%s;box-sizing:border-box">' % S),
    ("a-border-box-textarea", B + '<textarea id=a style="%s;box-sizing:border-box"></textarea>' % S),
    ("typed-inputs-with-author-size", B + ''.join('<input id=%s type=%s style="%s">' % (t, t, S) for t in ['text', 'password', 'email', 'url', 'tel', 'number', 'search'])),
    ("a-flex-row-input-and-its-neighbour", B + '<div style="display:flex;align-items:flex-start"><input id=a style="width:40px;height:20px"><textarea id=t style="width:40px;height:20px"></textarea><span id=b style="width:8px;height:10px"></span></div>'),
]
data = {"viewport": [400, 600], "boxes": "xywh", "cases": [{"name": n, "html": h} for n, h in cases]}
open(sys.argv[1], 'w').write(json.dumps(data, indent=1) + '\n')
