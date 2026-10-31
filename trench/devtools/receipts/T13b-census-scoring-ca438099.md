# T13b: census scoring follow-ups from the #842 R1

Branch `atlas/dt-t13b-census-scoring` @ ca438099, base develop 546d6196. No engine change.

## Evidence
- **Red first:** c1ae6778 commits the tests over no-op stubs: 8 of 50 fail on their asserts. Fix 36d937b9: `cargo test -p css-census` 50/0.
- **Report diff, same engine, same binary (unchanged tool vs fixed tool):** effect 131→127, parse 51→65, unsupported 154→144, red 212→216. Only these rows move:
  - `background-position`, `background-size`, `background-clip`, `background-repeat`: effect → parse, red, `unproven (control-limited, N probes)` on 756/765, 915, 450, 302. `background-size: cover`, `background-clip: text` and `background-repeat: no-repeat` stay `match` on their value rows.
  - The ten mask properties: unsupported → parse (arm found through the guard). Still mismatch on effect.
  - The `Paints right, reads wrong` section drops the four background rows, and the controls line gains the cap wording.
- **Report diff against the checked-in report (engine moved 1de44430 → 546d6196):** one row, `position` computed → effect (`relative` now matches). Not caused by this tool change.
- **Campaign:** 26/26, mean 1.1095%, no engine change.

## The rule, and why not the row's two
The row offered a per-probe delta, or demoting a match whose `off` exceeds half the floor. Measured on every matching row with an off control, neither finds the four rows:
- Half the floor: `background-clip` is 450 off a 916 floor, `repeat-x` 302. It would also demote `color` (71 off a 70 floor), a sentinel, which stops the run.
- Delta (disagreeing probes among those that changed in either engine): `repeat-x` 0.10, `background-clip` 0.12, against sound `text-align: center` 0.10 and `font-weight: 700` 0.60.

Shipped: the control's credit is capped at 100 probes (`FLOOR_CREDIT`). The highest floor in the glyph-noise contexts is 88 (`multicol`). A match that needs more credit than that, but still fits under the old full-floor allowance, is `unproven`. The cap sits between the highest matching rows that stay (`no-repeat` 82, `cover` 100, text up to 90) and the lowest demoted one (302), so 100 is a judgement from this data, not a derived constant.

`spanned`, `blend`, `persp` (the row's "same read"): no value in those contexts reads `match` on an off control, so nothing is credited there and nothing moved. Their rows were already honest.

## bg context: engine finding, reduced, NOT fixed
Control rows stay red because the context stays as it is: the row's acceptance wants these four rows red with the note. Oracle Chromium 143.0.7499.4, `parity-capture` at 546d6196, painted bounding box:

| `#p` (160x100, white page) | Chrome | engine |
|---|---|---|
| `background-image: linear-gradient(135deg,#c00 50%,#00c 50%); background-size: 40px 40px` | 160x100 | **160x120** |
| + `padding: 10px` | 180x120 | **200x120** |
| + `padding: 10px; border: 10px dashed #888` | 200x140 | **200x160** |
| + `border: 10px dashed #888`, no padding | 180x120 | **200x120** |
| `padding` + dashed border + gradient, no `background-size` | 200x140 | 200x140, 100 probes differ |
| `padding` + dashed border, `background: #c00` | 200x140 | 200x140, 0 differ |

Two engine bugs, both needing only a sized gradient:
1. **A tiled gradient is not clipped to the background painting area:** whole tiles paint, so the box grows to the next tile multiple on each axis.
2. **The tile phase starts at the border box, not the padding box** (`background-origin` initial value): inside the dashed border's gaps at (25,5) Chrome has blue, the engine red. Seen on the rows sampled, and the no-`background-size` row's 100 off probes fit it, but that row was not isolated further.

## Receipt (`scripts/receipt.py`)
```json
{
 "base_sha": "origin/develop",
 "binary_sha256": "405032c0071168686ca35826e3ea32d1ff9daf135361e20cd077b28f68a09824",
 "branch": "atlas/dt-t13b-census-scoring",
 "campaign": {"cases": 26, "failed": 0, "passed": 26, "mean_diff_pct": 1.1095,
  "sha256": "d814153ff61e36561ec24e4bf5f0c70c860d629cc7e553d9bbbafaa741afb8cf"},
 "candidate_sha": "ca438099fc83faadc7bc39e8bc7e07b9d4f4ca2e",
 "dirty_state": false,
 "profile": "parity",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)",
 "repo": "https://github.com/hiwavebrowser/hiwave-macos.git"
}
```
`base_sha` records the ref as passed; origin/develop was 546d6196. The campaign ran on the parity build via a no-op `cargo` on PATH and a `target/release/parity-capture` symlink, per the 10-29 recipe; the shim was only on PATH for `parity_test.py`.
