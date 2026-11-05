"""gen_b.py <outdir>: S9 (b) variants. A grid item whose children see a percentage height.
Each page: grid 240px tall, one minmax(0,1fr) row; item style varies; inside it a
`height:50%` child (#half) and a `height:calc(100% - 400px)` child (#spacer)."""
import pathlib, sys

out = pathlib.Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
HEAD = '<!doctype html><html><head><style>html,body{margin:0}%s</style></head><body>%s</body></html>'
GRID = '.slot{height:240px;display:grid;grid-template-rows:%s;justify-items:center;align-items:%s}'
BODY = ('<div class="slot" id="slot"><div class="item" id="item" style="%s;width:300px">'
        '<div id="half" style="height:50%%;background:red"></div>'
        '<div id="spacer" style="height:calc(100%% - 400px)"></div></div></div>')
V = {
    'b_px': ('minmax(0,1fr)', 'center', 'height:230px'),
    'b_pct': ('minmax(0,1fr)', 'center', 'height:100%'),
    'b_pct_max': ('minmax(0,1fr)', 'center', 'height:100%;max-height:230px'),
    'b_pct_max_mt': ('minmax(0,1fr)', 'center', 'height:100%;max-height:230px;margin-top:auto'),
    'b_pct_fixedrow': ('240px', 'center', 'height:100%'),
    'b_pct_start': ('minmax(0,1fr)', 'start', 'height:100%'),
    'b_auto_stretch': ('minmax(0,1fr)', 'stretch', 'height:auto'),
}
for name, (rows, align, item) in V.items():
    (out / (name + '.html')).write_text(HEAD % (GRID % (rows, align), BODY % item))
    print(out / (name + '.html'))

# Shrink-to-fit item (no width): a fixed-width child, then the percent children.
BODY_AUTO = ('<div class="slot" id="slot"><div class="item" id="item" style="%s">'
             '<div id="w" style="width:300px;height:10px"></div>'
             '<div id="half" style="height:50%%;background:red"></div>'
             '<div id="spacer" style="height:calc(100%% - 400px)"></div>%s</div></div>')
IMG = '<img id="img" width="1000" height="400" style="max-height:100%;max-width:100%;width:auto;vertical-align:bottom">'
VA = {
    'c_auto_pct': ('height:100%', ''),
    'c_auto_px': ('height:230px', ''),
    'c_auto_pct_img': ('height:100%', IMG),
    'c_auto_px_img': ('height:230px', IMG),
}
for name, (item, extra) in VA.items():
    (out / (name + '.html')).write_text(HEAD % (GRID % ('minmax(0,1fr)', 'center'), BODY_AUTO % (item, extra)))
    print(out / (name + '.html'))
