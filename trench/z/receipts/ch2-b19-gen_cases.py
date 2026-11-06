import json, sys
B = '<!doctype html><body style="margin:0">'
def row(jc, items, direction='row'):
    if direction == 'row':
        box = 'display:flex;justify-content:%s;width:100px;height:40px;margin-left:200px' % jc
        kids = ''.join('<div id=i%d style="flex:none;width:%dpx;height:20px"></div>' % (n, w) for n, w in enumerate(items))
    else:
        box = 'display:flex;flex-direction:column;justify-content:%s;width:40px;height:100px;margin-top:200px' % jc
        kids = ''.join('<div id=i%d style="flex:none;height:%dpx;width:20px"></div>' % (n, w) for n, w in enumerate(items))
    return B + '<div id=c style="%s">%s</div>' % (box, kids)
cases = []
for jc in ['center', 'flex-end', 'space-between', 'space-around', 'space-evenly', 'end', 'flex-start']:
    cases.append(('row-%s-one-overflowing-item' % jc, row(jc, [300])))
for jc in ['center', 'flex-end', 'space-around']:
    cases.append(('row-%s-two-overflowing-items' % jc, row(jc, [100, 100])))
for jc in ['center', 'flex-end']:
    cases.append(('column-%s-one-overflowing-item' % jc, row(jc, [300], 'column')))
cases.append(('row-reverse-center-overflowing', B + '<div id=c style="display:flex;flex-direction:row-reverse;justify-content:center;width:100px;height:40px;margin-left:200px"><div id=i0 style="flex:none;width:100px;height:20px"></div><div id=i1 style="flex:none;width:100px;height:20px"></div></div>'))
cases.append(('row-center-fits-control', row('center', [60])))
data = {"viewport": [600, 600], "boxes": "xywh", "cases": [{"name": n, "html": h} for n, h in cases]}
open(sys.argv[1], 'w').write(json.dumps(data, indent=1) + '\n')
