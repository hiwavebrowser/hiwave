T9 found two things `diagnose` could not say on yahoo: content painted over other content, and an own-site `console.error` of a string. This adds both to `report.rs`. No engine change. Gap 3 (naming React errors) stays out until Pete rules.

## What changed

| gap | report now says | carrier |
|---|---|---|
| 6 overlap, overflow | `[R12] y 800..1600: 7 boxes overlap other content, 3 run past the right edge`, ranked after R11, above own-site R5 | `Band.overlapping`, `Band.past_right`, both also printed in every band's Facts line; R12 fires at 3 or more of either in a band |
| 7 string errors | `[R5] the page's own script: logged string in <script>:line:col; at t=...; N fetch/XHR to <host> before, M after` | console records with a `<string len=N>` argument and no `error_stack`; shape only |

**Also fixed:** `console.error("text", err)` read `logged string thrown in`, because the name came from the first argument. It now reads the error's name and groups with the same error logged alone. A yahoo run showed this.

## Two departures from the plan row, both from what yahoo showed

1. **Overlap compares content leaves anywhere in the tree, not siblings.** I built the row's sibling rule first. It read **0 on yahoo**, the page it exists for, and fired R12 on wikipedia, so it was wrong both ways. On yahoo no two siblings overlap: the boxes lying over each other are 3 to 10 levels below their common ancestor. A leaf is an image or a box with text and no element children. Still layout rects only.
2. **A string is named by its first own-site frame, not only the record's place.** Yahoo wraps `console.error` from s.yimg.com, so every call's `location` is the wrapper. A location-only rule would miss the very string T9 reported.

## What each count leaves out

`overlapping` and `past_right` skip: out-of-flow boxes and anything inside them, sticky and inline boxes (a wrapped link's rect is the union of its lines), boxes clipped by an ancestor, boxes in a transform layer, boxes at zero opacity. `past_right` counts the outermost box only, and a body wider than the viewport does not hide what is in it. In a leaf overlap, a box and its own descendant are one thing, and the later leaf in document order is counted.

## Red first

Each fix commit follows a commit holding its failing tests.

| commit | tests | seen red |
|---|---|---|
| f0ecd85c | first 8 | 8/8 failed, 20 passed |
| f3b40f7d | cross-subtree overlap; empty and tinted box | 2 failed, 28 passed |
| 2a82bdbb | wrapper | 1 failed, 30 passed |
| c5b01118 | error name | 1 failed, 31 passed |

Three tests were not red at a commit, so I saw them red by mutation:
- `overlap_and_overflow_below_the_fold_are_named_from_a_real_layout`: removed the counting call.
- `a_string_console_error_from_the_page_reaches_r5_as_a_shape`: changed the shape literal.
- `a_box_and_its_own_descendant_do_not_overlap`: removed the descendant guard.

After: `cargo test -p parity-capture` 64/0. `cargo test -p rustkit-engine --features headless --lib diagnos` 33/0 (run at 2dc9a3b2; the later commits touch only parity-capture). The full engine suite was not run, since no engine file changed. Two of the new tests go through a real engine: the real-layout one, and the string one, which also pins that the text never reaches the report.

## Yahoo scoring run (1a6c8095, shape-only; script paths and class names trimmed)

```
document 2390px tall  1171 elements
Most likely:
  1. [R11] y 1600..2400: 16 painted boxes with no text and no image (skeleton?)
  2. [R12] y 800..1600: 7 boxes overlap other content, 3 run past the right edge
  3. [R12] y 1600..2400: 9 boxes overlap other content, 0 run past the right edge
  4. [R5] the page's own script: logged Error thrown in <own-site chunk>; at t=25.6 s; 8 fetch/XHR to www.yahoo.com before, 2 after
  5. [R4] no page script ran until t=6.1 s: 16 script body(ies) had arrived 3.0 s or more before (first at t=1.7 s); first layout at t=5.2 s; last answer before it: image at t=6.0 s
  6-8. [R4] three inserted scripts waited 3.6 to 3.7 s for a turn
Facts:
  still changing at capture end: last relayout 10 ms before; 0 requests open
  y 0..800: text 26, images 25, empty painted 0, overlapping 1, past right edge 1
  y 800..1600: text 52, images 37, empty painted 0, overlapping 7, past right edge 3
  y 1600..2400: text 11, images 7, empty painted 16, overlapping 9, past right edge 0
Not checked:
  R6 shield: not installed, nothing could be blocked
```

**Exit metric, read from this output alone: still not met (Atlas scores).** It now says the lower feed is placeholders and that the content around them overlaps and overflows. It still does not say why the rows never fill: the logged Error has no link to them and no name (gap 3), and no record links a fetch to the rows (gap 8). The overlap is a second symptom, not a cause. What is left for this metric is gaps 3 and 8.

**R12 across runs:** the three `diagnose` runs on the leaf rule (13a8c064, 2dc9a3b2, 1a6c8095) gave 6 to 7 in 800..1600 and 9 in 1600..2400, and 3 past the right edge in all three.

## What was and was not seen on yahoo

- **The string rule has not produced a line on yahoo.** All four yahoo runs this session held one plain string record, from the consent script (consent.cmp.oath.com) under the wrapper. That is another site, so it is correctly left out. Only the last two runs had the frame rule. T9's own-site string did not recur, so this path is pinned by the unit tests and the live local test, not by a yahoo line.
- The error-name bug showed on one yahoo run (2dc9a3b2) and the fix is pinned by a unit test; that TypeError did not recur at 1a6c8095, so the fixed line has not been seen live.
- The R12 counts are layout rects. I did not check them against a frame this session; T9's frames are what showed the overlap.

## False-positive check (`--live-ms` 8000, 1a6c8095)

| page | most overlapping in a band | most past the right edge | R12 |
|---|---|---|---|
| yahoo (25000) | 9 | 3 | fires |
| github | 1 | 0 | no |
| wikipedia | 0 | 0 | no |
| bbc | 1 | 0 | no |
| apple | 0 | 0 | no |
| nytimes | 0 | 0 | no |
| hacker news | 0 | 0 | no |

Seven pages, and the threshold of 3 came from these runs. It is not a broad sample.

**Known limits:**
- Bands stop at three viewports; overlap deeper in a page is not counted (a dump showed a few on github and bbc further down).
- Only leaves count, so text in an inline box is missed, and so is a coloured box lying over a card.
- A page that overlaps on purpose (a caption on an image, as a leaf in flow) counts.
- nytimes dumps stop at the 5000-element cap (6135 elements); the report says so.
- Strings logged by a page's own scripts only: a string from another site is dropped, and so is a string whose stack holds no own-site frame.
- A run with `--event-log-console-text` has no shape to read, so its strings are left out.

## Campaign and receipt

Campaign 26/26 at 1a6c8095, mean 1.1095%, the same mean as T10's receipt. T11 changes no render code.

```json
{
 "base_sha": "8f0488c6",
 "binary_sha256": "d697c187457a674e287f7675c9276e2f057bdb0f1010c7fdbb95b3a94e517a84",
 "branch": "atlas/dt-t11-overlap-strings",
 "campaign": {"cases": 26, "failed": 0, "mean_diff_pct": 1.1095, "passed": 26,
  "sha256": "4eeada9779b83c2fa46768bc5b92f4de471c4c9fe8e67b626987eb9c59430a49"},
 "candidate_sha": "1a6c8095594f3950711003032a8f7adc4523e732",
 "cargo": "cargo 1.91.0 (ea2d97820 2025-10-10)",
 "dirty_state": false,
 "profile": "parity",
 "toolchain": "rustc 1.91.0 (f8297e351 2025-10-28)"
}
```

R1: Prometheus or Atlas.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
