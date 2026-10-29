## 2026-10-29 15:05 slot: netflix form re-check and RD1 (Z lane)

Binaries: develop `d16d0f89` parity-capture (sha256 `a7638dfd…caf7e`); #826 N1b head `0e685e6d`; and `0e685e6d` + develop `d16d0f89` (a local throwaway merge `a294895b`, clean). All `--profile parity` through z-cargo on the macOS lane seat.

### Netflix form (12:05 order, item 4)
- At develop `d16d0f89`, with a real load (`--live-ms 8000`, `--dump-diagnostics`), the hero form is **one row**: a flex form 588×96; the email field 390.76×52 at (314, 321); the button 189.24×56 at (712.76, 321). The bottom-of-page form is one row too.
- N2 (#818 + #821) holds on develop. The stacking reported at 10:15 was seen only in the R2+N1+N1b local merge, so it comes from that stack. N1's flex free-space change is the first suspect; check it when N1 is next touched.

### RD1: reddit interstitial logo paints solid black
- **Not an engine bug on develop. #826's branch predates #787** (SVG author paint, be19dc7b). Without #787, inline SVG shapes ignore author class fills (`.snoo-cls-10{fill:#ff4500}`) and inherit `.logo svg{fill:currentColor}`, which is black. N1b then paints the logo above the disc, so the black shows.
- Reduced fixture (`tools/rd1/rd1_reduce.py`): a flex item holding an SVG `<rect class=a>`, with `.a{fill:#ff4500}`.
  - `0e685e6d`: (0,0,0) in all 4 variants (no z-index, z 1, z 1 relative, z 0).
  - develop: (255,69,0) in all 4.
  - `0e685e6d` + develop: (255,69,0) in all 4.
- Served interstitial (fetched once with the product UA, rendered with `--html-file`, kept local and deleted):
  - `0e685e6d` + develop paints the full-colour Snoo over the disc (face (255,235,239), bubble #ff4500).
  - develop alone paints the disc over the logo.
- **Consequence: #826 must merge develop before it lands** (after #824, as planned), or it ships the black logo.

### Found while reducing: two develop defects (reddit's pulsing disc)
Fixture: `tools/rd1/pseudo_probe.py`, an abspos `main:before` 100×100 with background #d93900.

| case | Chrome | develop |
|---|---|---|
| plain | (217,57,0) | (217,57,0) ok |
| `display:none` in the `::before` rule | no box, white | **(217,57,0): the box still paints** |
| `opacity:.75` | (227,107,64) | (227,107,64) ok |
| `opacity:.75` + `animation` whose 100% keyframe sets `opacity:0` (0% has none) | (227,107,64) at t=0 | **(217,57,0): the underlying 0.75 is lost; the animation starts from 1** |

Also from `rd1_probe.py`: `fill: url(#missing) #ff4500` paints white. SVG 2 says to use the fallback colour.
