# IFC quality sketch — fragment grouping + line-level alignment

**Author:** Prometheus (grind tick) · **Date:** 2026-07-10  
**Status:** **A+B SHIPPED** (PR #31, 2026-07-11). **B2 design** banked in  
`forensics/2026-07-11-ifc-b2-midline-split-BRIEF.md`. C still open.  
**Lane:** Advise. Atlas/Athena implement; this seat does not open code PRs from this doc.

> **Name collision:** Campaign PRs already shipped **line-box phases 1–5** (#15–#20).  
> This file is **not** a re-do of PR #17 (“phase 3 share lines”). It is PATH_FORWARD  
> **Bet #2 — IFC quality**: the residual session-3 falsification that phases 1–5 left open.  
> Call it “IFC quality / mixed-run align” in digests; keep this filename for the queue pointer.

---

## 1. Why this exists

Session 3 falsification (digest-macos, day-sprint session 3):

> There is no true line-box model for **mixed** inline fragments.  
> `Some <b>bold</b> text` under `text-align: center` still tends to **self-align each leaf**  
> against the block width, so runs **overlap or mis-center as a unit**, instead of  
> one line box shifting as a group.

Phases 1–5 fixed wrap, intrinsic width, shared line *placement*, whitespace, and mid-line  
text split. They did **not** make **alignment a property of the line**. That is the  
Friday / multi-session architectural item — not a 2h night dig.

**Exit (from PATH_FORWARD Bet #2):**

- `Some <b>bold</b> text` centers (or right-aligns) as **one** line.  
- Mixed inline + img does not explode vertically.  
- Friday WPT Tier-1 (css-text / css-inline) has a **number** (menu: `WPT_TIER1_SUBSET.md`).

---

## 2. What is already banked (do not re-derive)

| Phase | PR | What it bought |
|------:|----|----------------|
| 1 | #15 | Block text → `TextShaper::wrap_text`; multi-line `TextLine`s |
| 2 | #16 | Text contributes real intrinsic width; flex-basis:auto max-content |
| 3 | #17 | **All** inline-level boxes share line boxes (not only atomic) |
| 4 | #18 | css-text §4 whitespace collapse at box-build |
| 5 | #20 | Mid-line text fill-then-wrap (`wrap_text_with_first_line` / `layout_text_in_flow`) |
| #22 | strut/border-box | Empty atomic inlines: strut descent under baseline; border-box place |

**Current owner paths (macOS master, rustkit-layout):**

- Line assembly: `LayoutBox::layout_block_children` (+ collapse twin) ~L2016–2212  
- Leaf self-align: `layout_text` single-line path ~L1176–1189 (`text_align_offset` on content.x)  
- Multi-line leaf align: `layout_text` wrap path ~L1151–1155 (per-`TextLine` `x_offset`)  
- Line shift pass: `apply_text_align_offset` ~L2216–2251  
- IFC split gate: `text_splits_inline` (Left/Justify only) ~L1204  
- Mid-line wrap: `layout_text_in_flow` ~L1224–1279  
- Strut: `inline_strut_descent` / `baseline_is_bottom_edge` (#22)  
- Shaper API: `text.rs` `wrap_text` / `wrap_text_with_first_line`

**Known structural smell (CODE_REVIEW_SLIM):**  
`layout_block_children` and `layout_block_children_with_collapse` **duplicate** the IFC loop.  
Any quality PR must touch **both** or extract one helper first (slim order item 5).

---

## 3. Root residual (session-3, restated against current code)

### Symptom fixture (canonical)

```html
<div style="width: 200px; text-align: center;">
  Some <b>bold</b> text
</div>
```

**Chrome:** one line box, total advance W; whole line shifted by `(200 − W) / 2`.  
Fragments keep **relative** x within the line; bold is just a styled span in flow.

**RustKit today (likely failure modes):**

1. **Dual alignment sources**  
   - Leaf `layout_text` centers **its own** run against full `container_width`.  
   - Parent then `apply_text_align_offset` shifts recorded line children by line width.  
   Comment at ~L2231–2235 assumes span text and box “settle about the same center” — true  
   for a **single** run in a span, **false** for sibling runs that each self-centered.

2. **Asymmetric Text join rule** (~L2056–2058)  
   A `Text` child joins the current line only if `cursor_x > 0` **and** it fits remaining.  
   First text sibling often takes the **block** path (self-align + full width CB).  
   Later text siblings may join the line. Mixed trees get **half line-model, half leaf-model**.

3. **Phase-5 split skips Center/Right** (`text_splits_inline`)  
   Correct for “can’t shift a multi-line child as one box,” but Center/Right mixed pages  
   still drop mid-line text to block rows instead of splitting. Quality epic must either  
   (a) split and align **per line fragment**, or (b) keep the gate and document the trap.

4. **#22 residual (do not re-open as epic scope)**  
   `inline_strut_descent` ≈ +1.7px vs Chrome font metrics — **QUIRKS / non-goal**  
   (PATH_FORWARD + post-#22 settings memo). Line **height** polish ≠ line **grouping**.

### What “fragment grouping” means here

Not a full CSS Fragmentainer rewrite. Minimal model:

```
LineBox {
  fragments: [ InlineFragment, ... ]  // text slice | open/close inline | atomic | image
  width: sum(advances) + gaps
  strut: max ascent/descent (or line-height box)
  y: line top in block
}
```

Today the engine approximates this with **child index ranges** `(start, end, line_width)`  
and per-box coordinates — enough for placement, not enough for **one align pass**  
when leaves also write absolute x from text-align.

---

## 4. Design — three slices (multi-session)

### Slice A — Kill leaf self-align (correctness foundation) — **SHIPPED PR #31**

**Goal:** Text leaves **never** apply `text-align` to `content.x` / `TextLine.x_offset`.  
Alignment is **only** applied at the line-box (parent) layer.

| Change | Detail |
|--------|--------|
| `layout_text` single-line | `text_align_offset = 0`; place at CB origin (flow cursor owns x) |
| `layout_text` multi-line | `TextLine.x_offset = 0` (or only phase-5 first-line remaining offset) |
| `layout_text_in_flow` | Keep first-line remaining-width offset only (flow, not align) |
| `apply_text_align_offset` | Sole owner of Center/Right for LTR; extend to pure-text lines |

**Regression tests (crate-local, no full WPT):**

1. Plain text center — same as today after parent pass.  
2. `Some <b>bold</b> text` center — **one** line width W; first glyph x ≈ `(cb − W)/2`.  
3. Nested span with background — box origin and text move together (no double-shift).  
4. Left align — bit-identical / no-op offsets.

**Risk:** Temporarily breaks any caller that relied on leaf self-align without a parent  
line record (orphan text in odd Display paths). Audit: only block-children IFC +  
inline layout. Cap: **one PR**, pure behavioral with tests; no strut/flex.

**Exit A:** session-3 fixture green under layout.json probe (not necessarily suite flip).

### Slice B — Symmetric inline join (true mixed runs) — **B-min SHIPPED PR #31; B2 SHIPPED PR #37**

**Goal:** Every inline-level sibling (Text, Inline, atomic, Image, FormControl)  
**competes for the same line box** under one rule.

| Change | Detail |
|--------|--------|
| `flows_inline` for Text | Join when remaining width ≥ min(single-line, first word) OR phase-5 split — not only `cursor_x > 0` |
| First-on-line Text | Still IFC-path: `cursor_x = 0`, width measured, no block self-align |
| Nested Inline | Prefer laying out **inline children’s fragments into parent line**, not a private vertical stack (`layout_inline` sequential cursor is OK for shrink-to-fit width, but block IFC must not re-stack mixed siblings) |
| Whitespace | Keep #18 collapse; line-start strip at assembly, not re-collapse |

**Phase-5 interaction:** Once leaves do not self-align, enable `text_splits_inline` for  
**Center/Right** by recording **per visual line** fragment ranges that include  
split `TextLine` rows (or synthetic pseudo-children). If that is too big for one PR,  
ship Left/Justify complete in B and Center/Right split as **B2**.

**Exit B-min (met):** fitting mixed runs share one line under center (`mixed-inline-center.html`).  
**Exit B2 (met, PR #37 @53ab3ca):** Center/Right mid-line split — FLOW⊕ALIGN;  
`text_flow_first_offset`; wrap hard 12/12; nested-inline residual ledgered.  
Fixtures: `mixed-inline-wrap.html` + `mixed-inline-img.html` on master.

### Slice C — Baseline / vertical-align (quality, bounded) — **OPEN 2026-07-11**

**Goal:** Mixed replaced + text on one line shares a baseline; `vertical-align: middle/sub/super/baseline` for the common set.

| In | Out |
|----|-----|
| baseline (default) | `vertical-align: top/bottom` on line boxes (defer) |
| middle for img/input | full baseline-source property matrix |
| strut from #22 as line min height | matching ±1.7px Chrome font delta |

**Owner hooks already present:** `baseline_is_bottom_edge`, `inline_strut_descent`,  
line_height / line_below_baseline accumulators in the IFC loop.

**Exit C:** `text + <img>` and form controls on one line match Chrome **structure**  
(same line, baseline-ish), not pixel-perfect strut.

**Implement brief (OPEN):** `forensics/2026-07-11-ifc-slice-c-baseline-BRIEF.md`  
**Gate receipt:** `forensics/2026-07-11-ifc-slice-c-GATE-OPEN.md` — #37 master + wrap hard green.  
Live pins @740656c: `vertical_align` parsed, still unread in layout; strut extends line  
height only; member Y still top-of-line; fixture `mixed-inline-img.html` ready.  
Atlas: C0 probe → C1/C2. Prometheus: outside-eye when PR opens.

---

## 5. Algorithm sketch (Slice A+B target)

```
layout_ifc_children(block):
  open LineState { y, x=0, height=0, below=0, members=[] }

  for child in inline_level_flow_order:
    if absolute/fixed: layout out-of-flow; continue

    if Text and needs_split(remaining):
      lines = wrap_with_first_line(remaining, full)
      place line0 at (x,y); close line; place middle full lines;
      open new line with last fragment; continue

    measure child (no text-align in measure)
    if x > 0 and x + w > available:
      close_line()  // apply text-align to members as a unit
      open LineState at y += line_box_height

    place child at (x, y) using margin-box cursor (#22 border-box lesson)
    x += w; accumulate strut/ascent/descent
    members.push(child)

  close_line()
  block.content.height = y

close_line(state):
  offset = text_align_offset(state.width, container, style.text_align)
  for m in state.members:
    m.content.x += offset
    // if Text has text_lines, also += offset to each TextLine.x_offset
  // justify later: distribute free space into gaps between members
```

**Invariant:** After `close_line`, **no** fragment has applied text-align twice.  
**Invariant:** `line.width` is sum of member margin-box widths (and collapsed spaces),  
never `container_width` unless full-justify stretch (out of scope).

---

## 6. Fixtures & WPT (measurement contract)

### Local fixtures (ship with first executable PR)

1. `parity-tests/repro/mixed-inline-center.html` — session-3 fixture + Right/Left.  
2. `mixed-inline-wrap.html` — long mixed run that wraps mid-bold.  
3. `mixed-inline-img.html` — text + 16×16 img + text (Slice C).  

Probe: layout.json / y_table — **first glyph of “Some”** and **last of “text”**  
must share one baseline band; center: midpoint of [first,last] ≈ block mid.

### WPT Tier-1 menu (already listed)

`WPT_TIER1_SUBSET.md` Tier-1A text-align + Tier-1B vertical-align / mixed inline.  
When Phase 0.5 runner exists: failures map **here**, not ad-hoc digs.  
Note: `LINE_BOX_WPT_ROADMAP.md` was referenced in the queue but **does not exist**;  
this sketch + `WPT_TIER1_SUBSET.md` are the ladder until someone cuts that file.

### Campaign metric expectation

- **Do not** promise a websuite flip from Slice A alone (session 3 already taught that).  
- Expect **css-selectors / article-typography** residual moves when B lands.  
- sticky-scroll / settings / paint cliffs stay on **other** epics (PATH_FORWARD).

---

## 7. Shared checklist (macOS ↔ Windows)

PATH_FORWARD Athena Bet #3 — same ladder, avoid a third line model:

```
wrap → real advances → mixed inlines share lines → line-level align → baseline/valign
  #15      #16/#10         #17                          **this sketch A+B**    **C**
```

Portable note on every IFC quality PR (one paragraph):

- Windows IFC (#9/#10) status vs this change  
- Whether `layout_block_children*` dual paths still exist on both seats  
- Fixture pass/fail both engines when Athena is past paint cliff

---

## 8. Explicit non-goals

- Matching #22 **+1.7px** strut / font delta  
- Full justification algorithm / hanging punctuation  
- fastrender detour (metric engine = **rustkit-***)  
- Unifying macOS/Windows crates this epic (semantics + checklist only)  
- Mid-word break “fixes” that violate css-text §5.2  
- Starting while Atlas sticky/overflow Day 1–N is the active night scope  
  (PATH_FORWARD: IFC quality **after** sticky plateaus — unless Pete reorders)

---

## 9. Sequencing vs live epic

| Now (2026-07-11) | Owner | Relation to this doc |
|------------------|-------|----------------------|
| sticky/overflow | Atlas | **CLOSED** (PR #25 era) |
| A+B IFC quality | Atlas | **SHIPPED** PR #31 |
| B2 mid-line Center/Right | Atlas | **SHIPPED** PR #37 @53ab3ca |
| advance-contract (text stack) | Atlas | **SHIPPED** #36; GradientText residual **SHIPPED** #39 |
| CI honesty (path/schema/VP/stability + KF freeze) | Atlas | **SHIPPED** #38 + #40 |
| DIG-1 input border-box | Atlas | **SHIPPED** #41; css-selectors 18.94→16.65 |
| Slice C baseline/valign | Atlas **OPEN** | Gate open: `forensics/2026-07-11-ifc-slice-c-GATE-OPEN.md` |
| DIG-2 buttons | Atlas parallel | Separate PR; not combined with C |
| paint stack | Athena | Orthogonal; portable IFC note on #31 |
| **This sketch** | Prometheus | Living design; next tip = outside-eye on C PR |

**Greenlight:** A+B+B2 shipped. Slice C gate cleared 2026-07-11 — Atlas C0 without further ceremony.

---

## 10. Suggested PR stack (when greenlit)

| Order | PR | Cap | Depends |
|------:|----|-----|---------|
| 0 | Optional: extract shared `layout_ifc_children` from dual block-children | 1h chore | — |
| 1 | **Slice A:** remove leaf text-align; parent-only align + mixed fixture tests | 1 night | 0 nice |
| 2 | **Slice B:** symmetric Text join + first-on-line IFC path | 1–2 nights | 1 |
| 2b | Center/Right + phase-5 per-line fragment ranges | 1 night | 2 |
| 3 | **Slice C:** baseline/valign subset | 1–2 nights | 2 |
| 4 | WPT Tier-1 subset run receipt (if runner ready) | half night | 1+ |

---

## 11. Decision board (for Pete / Friday)

1. Accept **line-only text-align** (Slice A) even if one night is “metric flat”? **Recommend YES** — session 3 already proved leaf align is a dead end.  
2. Start IFC quality before sticky epic finishes? **Recommend NO** unless sticky stalls early.  
3. Shared Friday IFC fixture both seats? **Recommend YES** (PATH_FORWARD decision board item 3).

---

## Receipts

- Session-3 falsification: `trench/digest-macos.md` (day-sprint session 3)  
- Phase ladder: `trench/BASELINE-macos.md` session 10 scopes; PRs #15–#20  
- Plan of record: `trench/PATH_FORWARD.md` Bet #2  
- WPT menu: `trench/WPT_TIER1_SUBSET.md`  
- Strut residual: PR #22 (`c305ef0`), `forensics/2026-07-10-post22-settings.md` § residual  
- Slim dual-path note: `trench/CODE_REVIEW_SLIM.md`  

— Prometheus
