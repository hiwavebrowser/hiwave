"""Write tools/parity_oracle/border_shorthand_no_style_cases.json (CH2.B18b)."""
import json
import sys

out = sys.argv[1]
HEAD = '<!doctype html><html><head><style>body{margin:0}div{width:10px;height:10px}%s</style></head><body>'
TAIL = '</body></html>'


def div(style, extra_css=''):
    return HEAD % extra_css + '<div id=a style="%s"></div><div id=b></div>' % style + TAIL


def raw(body, extra_css=''):
    return HEAD % extra_css + body + TAIL


cases = [
    ('border-5px', div('border:5px')),
    ('border-thick', div('border:thick')),
    ('border-5px-red', div('border:5px red')),
    ('border-red-thin', div('border:red thin')),
    ('border-top-5px', div('border-top:5px')),
    ('border-left-thick-red', div('border-left:thick red')),
    ('border-right-5px', div('border-right:5px')),
    ('border-bottom-5px', div('border-bottom:5px')),
    ('border-5px-solid', div('border:5px solid')),
    ('border-5px-dotted-blue', div('border:5px dotted blue')),
    ('style-then-border-5px', div('border-style:solid;border:5px')),
    ('border-solid-then-border-5px', div('border:5px solid;border:5px')),
    ('border-5px-then-style', div('border:5px;border-style:solid')),
    ('border-5px-then-top-style', div('border:5px;border-top-style:dashed')),
    ('side-solid-then-border-top-5px', div('border:5px solid;border-top:5px')),
    ('sheet-border-5px', raw('<div id=a class=x></div><div id=b></div>', '.x{border:5px}')),
    ('sheet-style-inline-border', raw('<div id=a class=x style="border:5px"></div><div id=b></div>', '.x{border-style:solid}')),
    ('border-style-revert', div('border:5px solid;border-style:revert')),
    ('border-style-revert-layer', div('border:5px solid;border-style:revert-layer')),
    ('border-top-style-revert', div('border:5px solid;border-top-style:revert')),
    ('border-revert', div('border:5px solid;border:revert')),
    ('input-border-5px', raw('<input id=a style="display:block;border:5px;padding:0;width:20px;height:10px"><div id=b></div>')),
    ('input-border-5px-solid', raw('<input id=a style="border:5px solid;padding:0;width:20px;height:10px"><div id=b></div>')),
    ('input-border-style-revert', raw('<input id=a style="border-style:none;border-style:revert;padding:0;width:20px;height:10px"><div id=b></div>')),
    ('hr-border-5px', raw('<hr style="border:5px;margin:0"><div id=b></div>')),
    ('pseudo-border-5px', raw('<div id=a></div><div id=c></div>',
                              '#a,#c{height:auto}#a::after{content:"";display:block;width:4px;height:4px;border:5px}'
                              '#c::after{content:"";display:block;width:4px;height:4px;border:5px solid}')),
    ('animated-width-no-style', raw('<div id=a></div><div id=b></div>',
                                    '@keyframes w{from{border-width:5px}to{border-width:5px}}#a{animation:w 100s linear}')),
    ('animated-top-width-no-style', raw('<div id=a></div><div id=b></div>',
                                        '@keyframes w{from{border-top-width:5px}to{border-top-width:5px}}#a{animation:w 100s linear}')),
    ('animated-width-solid', raw('<div id=a></div><div id=b></div>',
                                 '@keyframes w{from{border-width:5px}to{border-width:5px}}#a{border-style:solid;animation:w 100s linear}')),
    ('transition-width-no-style', raw('<div id=a style="border-width:1px;transition:border-width 100s linear"></div><script>var a=document.getElementById("a");a.offsetWidth;a.style.borderWidth="9px"</script><div id=b></div>')),
    ('script-border-5px-then-style', raw('<div id=a style="border:5px"></div><script>var a=document.getElementById("a");a.offsetWidth;a.style.borderStyle="solid"</script><div id=b></div>')),
]

data = {
    'viewport': [400, 300],
    'boxes': 'xywh',
    'note': 'CH2.B18b: a border shorthand with no style keyword resets the style to none (Chromium paints nothing); border-style revert/revert-layer.',
    'cases': [{'name': n, 'html': h} for n, h in cases],
}
with open(out, 'w') as f:
    json.dump(data, f, indent=1)
    f.write('\n')
print(len(cases), 'cases')
