"""gen.py <outdir>: S9 reduced pages (google election-day doodle, 2026-11-03), shape only.

Shape from the served page: a grid (one minmax(0,1fr) row, fixed height) whose item is
`height:100%; max-height:230px`; inside it a spacer `height:calc(100% - 400px)` and an
<img width=1000 height=400> with `max-height:100%; max-width:100%; width:auto`.
Chrome: the item is 230 tall, the spacer 0, the image 575x230 at the item's top.
Each variant drops or isolates one property so the first divergence can be named.
"""
import base64, io, pathlib, sys
from PIL import Image

out = pathlib.Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
buf = io.BytesIO()
Image.new('RGB', (1000, 400), (220, 40, 40)).save(buf, 'PNG')
SRC = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

HEAD = '<!doctype html><html><head><style>html,body{margin:0;height:100%%}%s</style></head><body>%s</body></html>'

FULL_CSS = (
    '.col{display:flex;flex-direction:column;height:100%}'
    '.top{height:60px;flex-shrink:0}'
    '.slot{flex-shrink:0;box-sizing:border-box;min-height:150px;height:calc(100% - 560px);max-height:290px;'
    'display:grid;justify-items:center;align-items:center;position:relative;grid-template-rows:minmax(0,1fr);padding:0 96px}'
    '.item{grid-area:1/1;height:100%;margin-top:auto;max-height:230px;position:relative;text-align:center;margin-left:48px;margin-right:48px}'
    '.img{max-height:100%;max-width:100%;object-fit:contain;object-position:center bottom;width:auto;vertical-align:bottom}'
)
FULL_BODY = ('<div class="col"><div class="top" id="top"></div><div class="slot" id="slot">'
             '<div class="item" id="item"><div id="spacer" style="height:calc(100% - 400px)"></div>'
             '<a href="#" id="link"><picture id="pic"><img class="img" id="img" width="1000" height="400" src="' + SRC + '"></picture></a>'
             '</div></div><div id="after" style="height:20px"></div></div>')

# Simplest: a definite-height block, img max-height:100% inside an inline <a>.
BLOCK_CSS = '.box{height:230px;width:992px;text-align:center}.img{max-height:100%;max-width:100%;width:auto;vertical-align:bottom}'
BLOCK_BODY = ('<div class="box" id="item"><div id="spacer" style="height:calc(100% - 400px)"></div>'
              '<a href="#" id="link"><img class="img" id="img" width="1000" height="400" src="' + SRC + '"></a></div>')

# Grid item with height:100% (definite from the row), percent child.
GRID_CSS = ('.slot{height:240px;display:grid;grid-template-rows:minmax(0,1fr);justify-items:center;align-items:center}'
            '.item{grid-area:1/1;height:100%;max-height:230px;margin-top:auto}'
            '.img{max-height:100%;max-width:100%;width:auto;vertical-align:bottom}')
GRID_BODY = ('<div class="slot" id="slot"><div class="item" id="item"><div id="spacer" style="height:calc(100% - 400px)"></div>'
             '<img class="img" id="img" width="1000" height="400" src="' + SRC + '"></div></div>')

PAGES = {
    'full': (FULL_CSS, FULL_BODY),
    'block': (BLOCK_CSS, BLOCK_BODY),
    'grid': (GRID_CSS, GRID_BODY),
}
for name, (css, body) in PAGES.items():
    (out / (name + '.html')).write_text(HEAD % (css, body))
    print(out / (name + '.html'))
