"""gen_d.py <outdir>: S9 (b) bisect. Shrink-to-fit grid item `height:100%; max-height:230px`
in a 240px grid; a `calc(100% - 400px)` spacer, then one of several siblings."""
import base64, io, pathlib, sys
from PIL import Image

out = pathlib.Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
buf = io.BytesIO()
Image.new('RGB', (1000, 400), (220, 40, 40)).save(buf, 'PNG')
SRC = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
IMG = '<img id="img" width="1000" height="400" style="max-height:100%;max-width:100%;width:auto;vertical-align:bottom" src="' + SRC + '">'
HEAD = ('<!doctype html><html><head><style>html,body{margin:0}'
        '.slot{height:240px;display:grid;grid-template-rows:minmax(0,1fr);justify-items:center;align-items:center}'
        '.item{grid-area:1/1;height:100%%;max-height:230px}</style></head><body>'
        '<div class="slot" id="slot"><div class="item" id="item">%s</div></div></body></html>')
SP = '<div id="spacer" style="height:calc(100% - 400px)"></div>'
SP50 = '<div id="half" style="height:50%"></div>'
V = {
    'd_text': SP + '<span id="t">text</span>',
    'd_wide': SP + '<div id="w" style="width:500px;height:10px"></div>',
    'd_img': SP + IMG,
    'd_a_img': SP + '<a id="link" href="#">' + IMG + '</a>',
    'd_half_text': SP50 + '<span id="t">text</span>',
    'd_px_spacer_text': '<div id="spacer" style="height:calc(50% + 10px)"></div><span id="t">text</span>',
}
for name, body in V.items():
    (out / (name + '.html')).write_text(HEAD % body)
    print(out / (name + '.html'))
