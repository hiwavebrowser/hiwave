import sys
D = '/Users/petecopeland/Repos/.worktrees/z-ch2-b18c/scratch/x-b18c/'


def ppm(p):
    b = open(p, 'rb').read()
    parts, i = [], 0
    while len(parts) < 4:
        while b[i:i + 1].isspace():
            i += 1
        j = i
        while not b[j:j + 1].isspace():
            j += 1
        parts.append(b[i:j]); i = j
    w, h = int(parts[1]), int(parts[2])
    return w, h, b[i + 1:]


for site in sys.argv[1:]:
    wa, ha, a = ppm(D + site + '-0.ppm')
    wb, hb, bb = ppm(D + site + '-1.ppm')
    if (wa, ha) != (wb, hb):
        print(site, 'size differs', wa, ha, wb, hb); continue
    xs, ys, n = [], [], 0
    for k in range(0, min(len(a), len(bb)), 3):
        if a[k:k + 3] != bb[k:k + 3]:
            p = k // 3; xs.append(p % wa); ys.append(p // wa); n += 1
    if n:
        print(site, 'px', n, 'bbox x', min(xs), max(xs), 'y', min(ys), max(ys))
    else:
        print(site, 'identical')
