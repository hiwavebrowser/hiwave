"""Close the 09:05 session: fill the suite line into pr-body.md, set CH2.B18c blocked (cap), append the digest."""
import sys
H = '/Users/petecopeland/Repos/.worktrees/z-hub/trench/z/'
suite = open(sys.argv[1]).read().strip()  # one-paragraph suite result
when = sys.argv[2]  # HH:MM

pb = H + 'receipts/ch2-b18c/pr-body.md'
s = open(pb).read()
assert '@@SUITE@@' in s
open(pb, 'w').write(s.replace('@@SUITE@@', suite))

p = H + 'PLAN-z.md'
L = open(p).read().split('\n')
for i, l in enumerate(L):
    if l.startswith('| CH2.B18c |'):
        c = l.split('|')
        assert c[6].strip() == 'in-progress', c[6]
        c[6] = ' blocked (PR cap) '
        c[7] = c[7].rstrip() + (
            ' %s (11-07) Z lane: **head cfb8e2b5** (second red 01f3ffde): the frame follows the author only when all four sides agree, '
            'snapped as Chromium (0<w<1 → 1, else floor); mixed sides keep develop\'s frame (468544a4 painted none for `border-top:0`). '
            'Chromium probes: wikipedia hide buttons `0px none`, netflix select/input `0px solid` → all four A/B movers (bing .12, x .07, netflix .08, wikipedia .02) toward Chrome. '
            'Campaign 26/26 (css-selectors 12767 → 12561); layout 907/0; form filter 220/0; e22 fixture headless red px 1196 → 41600 = Chromium 41600 (window half needs a seat with grants). '
            'Suite: see digest. **BLOCKED (stop rule, 2nd session; cap 9/8). Decision packet: open the PR from `receipts/ch2-b18c/pr-body.md` when a slot frees, after E20 and B17b.** '
            'Follow-up row wanted: per-side control frames (TextInput carries one width). |' % when)
        L[i] = '|'.join(c[:7]) + '|' + c[7]
        break
else:
    raise SystemExit('row not found')
open(p, 'w').write('\n'.join(L))

d = H + 'digest-z.md'
open(d, 'a').write('''
## 2026-11-07 %s Z-lane CH2.B18c (owed gates → second fix → blocked: cap)
- **Order:** there is still no 'PETE'S HAND TEST' CONSEQUENCE line under Rules. No receipt step was due (that is Prometheus's). I0's Z items are all on develop, and the 11-04 order puts the lane on CH2 rows, so this session resumed B18c, the row the 07:50 session left in progress.
- **Chromium look at the movers found a regression in 468544a4**, now fixed at **cfb8e2b5** (second red pin 01f3ffde; branch `atlas/z-ch2-b18c-input-border-width`, base develop 3b4561e3).
  - 468544a4 painted the top side's width on all four sides, so an input with `border: 1px solid; border-top: 0` lost its whole frame. Chromium keeps three sides; develop painted all four.
  - Now the frame follows the author only when the four sides agree, and widths snap as in Chromium (0.05em → 1, 2.5px → 2).
  - Mixed sides keep develop's frame. Real per-side frames need a TextInput command change: **a new row is wanted** (Atlas to place).
- **Before → after, by Chromium:**
  - The reduced page of 15 border forms matches Chromium on every uniform form: `border:0`, `width:0 solid`, `thin`, `medium` → 3, `3px`, rem/calc/var.
  - develop wrongly framed `border:0`: our `border` shorthand leaves the side styles set, so the old `style == none` test never fired.
  - The e22 fixture at rest: red border pixels 1196 → 41600, and Chromium has 41600.
- **The four A/B movers are confirmed toward Chrome.**
  - wikipedia hide/move buttons are `0px none` in Chromium; netflix's select and email input are `0px solid`.
  - bing and x lose an inner rectangle drawn inside a rounded search/login box.
  - At cfb8e2b5 they have the same values as at 468544a4.
- **Gates at cfb8e2b5:** campaign 26/26 (css-selectors 12767 → 12561, identical to 468544a4); layout 907/0; headless form filter 220/0. Suite: %s
- **Not run:** the window half of `e22_focus_ring`. It needs Accessibility and Screen Recording, which this seat does not have.
- **BLOCKED (stop rule, second session; PR cap 9/8).** Decision packet: open the PR from `receipts/ch2-b18c/pr-body.md` (complete) when a slot frees, after E20 and B17b. Worktree z-ch2-b18c is KEPT (bins in scratch) until the PR is open.
- Aleph not used (no Aleph tools in this seat).
''' % (when, suite))
print('ok')
