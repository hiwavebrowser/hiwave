# IFC Slice C — baseline / vertical-align (implement brief)

**Author:** Prometheus · **Date:** 2026-07-11 (grind tick)  
**Status:** **OPEN for implement** — gate cleared 2026-07-11 (see `2026-07-11-ifc-slice-c-GATE-OPEN.md`)  
**Extends:** `trench/IFC_PHASE3_SKETCH.md` § Slice C · B2 brief / PR37 review  
**Pinned tree:** `hiwave/hiwave-macos` @ **`740656c`** (master tip after #37–#41)  
**B2 content:** `53ab3ca` (PR #37) · advance contract + GradientText + CI honesty already on master  
**Lane:** IFC quality tip — **not** DIG-2 buttons, not campaign thresholds, not Windows

---

## 0. Gate (hard) — **CLEARED 2026-07-11**

Was blocked until all of:

1. **#37 B2** on `master` → **PASS** (merged; tip includes #38–#41 on top).  
2. **Wrap hard rows green** on B2 fixtures → **PASS** (`probe_b2_wrap.py` **12/12 hard**; four midline unit tests on master; B2 PR gate `29162498221` green incl. aggregate).  
3. Nested-inline fragmentation **ledgered**, not expanded into C → **PASS** (probe `hard=False` rows 1–3).

**Open doc:** `forensics/2026-07-11-ifc-slice-c-GATE-OPEN.md` (re-pins + Atlas order).

**Why the gate existed:** C placement math sits on the same dual IFC loops B2 taught. That flight is over; start with **C0 probe**, not another design pass.

---

## 1. Goal (from sketch, tightened)

**Exit C:** `text + <img>` (and a small form-control sample) on one line match Chrome **structure**:

- Same line box (already A+B / B2 territory when width allows).  
- **Baseline-ish** vertical placement: image bottom margin edge sits on the line’s alphabetic baseline under `vertical-align: baseline` (default).  
- `vertical-align: middle` on the image moves it to a middle-of-line band (fixture `.mid` row).  
- **Not** pixel-perfect strut / ±1.7px Chrome font delta (explicit non-goal from IFC sketch §8 and PR #22 residual).

| In scope | Out of scope |
|----------|----------------|
| `baseline` (default) for replaced + empty atomic | `top` / `bottom` / `text-top` / `text-bottom` on line boxes |
| `middle` for `img` (and optional checkbox/radio) | full `baseline-source` property matrix |
| strut hooks already present as line min-height | matching campaign `settings` 11b class by font delta |
| dual-path mirror (`layout_block_children` + `_with_collapse`) | full justification / hanging punctuation |
| unit + fixture probe | WPT runner (menu only: Tier-1B) |

---

## 2. Live truth (falsifiable pins — re-verified master@740656c)

### 2.1 CSS already parses `vertical-align` — layout never reads it

`rustkit-css` `VerticalAlign` enum (`Baseline`, `Sub`, `Super`, `Top`, `TextTop`, `Middle`, `Bottom`, `TextBottom`, `Length(f32)`) lives on `ComputedStyle.vertical_align`.

**`git grep vertical_align crates/rustkit-layout` → empty** (still empty @740656c). Every value is a silent no-op at layout time.

### 2.2 Strut / baseline hooks exist — they only extend **line height**, not **member Y**

| Hook | Location (approx) | What it does today |
|------|-------------------|--------------------|
| `baseline_is_bottom_edge()` | `lib.rs` ~1445 | `true` for `BoxType::Image` and empty atomic inlines (`inline-block/flex/grid` with no children) |
| `inline_strut_descent()` | ~1452 | container font descent + half-leading (CSS2 §10.8 approximation) |
| `line_below_baseline` | IFC loops ~2031 / ~2307 | max extent **below** baseline for bottom-edge boxes → used only when **closing** the line (`cursor_y += line_height.max(line_below_baseline)`) |

**Placement is still top-of-line for every member:**

```text
child.content.y = line_top + margin.top + border.top + padding.top
# same cursor_y for Text, Image, FormControl, atomic inlines
```

Text paint later applies **half-leading** on emission (`content_y + half_leading`, ~4189–4210), so glyphs sit mid–line-height. Images do **not** get a corresponding “bottom sits on baseline” shift. Net visual: text and 16×16 img share an X line (good) but the img hangs from the **top** of the line box (Chrome puts its bottom on the alphabetic baseline for `vertical-align: baseline`).

### 2.3 Form controls

`FormControl` flows inline (`flows_inline` match includes `BoxType::FormControl`) but is **not** in `baseline_is_bottom_edge` unless it is also an empty atomic-inline display (typical form controls are `inline` / replaced-ish, not `inline-block` empty). Slice C should treat **img first**, then optionally checkbox/radio as “bottom-edge baseline” if a one-line probe shows they need it — do not boil the ocean on `<select>` / multi-line `<textarea>`.

### 2.4 Dual IFC loops (must stay twins)

Same B2 discipline:

- `layout_block_children` ~2037  
- `layout_block_children_with_collapse` ~2402  

Any Y adjustment for valign **must** ship in both, or re-extract a shared line-place helper (optional 1h chore; not required if the mirror is line-identical).

### 2.5 Fixture already drafted

`parity-tests/repro/mixed-inline-img.html` (B2 brief §8 / this epic’s C fixture):

| Row | Expectation |
|-----|-------------|
| left / center / right `before <img> after` | one line when width allows; center/right shift as a **unit** (A+B / B2) |
| `.mid` `aa <img> bb` with `img { vertical-align: middle }` | img vertically centered on the line’s middle band (C) |

Local `mixed-inline-img.layout.json` may exist from earlier probes — **re-capture after B2 merge** before trusting Y tables.

---

## 3. Contract (portable)

### Line baseline (CSS2 §10.8.1, minimal)

For each open line box after members are measured (or on place, with running maxes):

1. **`line_top`** = current `cursor_y` (content-box of container).  
2. **`max_text_ascent` / `max_text_descent`** from text members’ font metrics (reuse `measure_text_advanced` / layout shaper — same stack as advance contract).  
3. **Strut** from container: ascent/descent/half-leading already approximated by `inline_strut_descent` + existing line-height path.  
4. **`baseline_y`** (absolute content Y of the alphabetic baseline):

```text
baseline_y = container.content.y + line_top
             + max(strut_ascent_with_half_leading, max_text_ascent_with_half_leading, …)
```

Exact formula should match **existing** text emission: text glyph top ≈ `content_y + half_leading`, baseline ≈ glyph top + ascent. Prefer **deriving baseline from the same metrics path text already uses** over inventing a second baseline.

5. Place each member’s **margin box** relative to `baseline_y` by `vertical-align`:

| `vertical-align` | Placement rule (Slice C subset) |
|------------------|----------------------------------|
| `baseline` (default) | If `baseline_is_bottom_edge()` (img, empty atomic): **margin-bottom edge on `baseline_y`**. Text: keep current half-leading emission (baseline through metrics). Other inlines: treat as bottom-edge if empty atomic; else leave top-aligned until a later slice. |
| `middle` | Align vertical midpoint of margin box to `baseline_y − 0.5 * x-height` (x-height ≈ `0.5 * font_size` OK for v1; or metrics if cheap). |
| `sub` / `super` | **Optional same PR** if cheap: baseline ± `0.2 * font_size` (probe-defined); else defer. |
| top / bottom / text-* / length | **Defer** — parse stays, layout ignores, ledger in digest. |

6. **Line box height** after place:

```text
line_box_height = max over members of
  (distance above baseline + distance below baseline)
# includes strut descent under bottom-edge boxes (existing line_below_baseline intent)
```

Close line with `cursor_y += line_box_height` (replace ad-hoc `line_height.max(line_below_baseline)` only if the new accumulators are strictly more general — do not regress empty atomic strut tests).

### Invariants

- **No double shift:** text-align still horizontal only (`translate_subtree` / `x_offset`); valign is **vertical only**.  
- **Leaves do not self-valign in paint** — layout owns Y (same story as text-align Slice A).  
- **B2 `TextLine.x_offset`** remains FLOW ⊕ ALIGN; C does not rewrite x_offset.  
- **Advance contract** stays orthogonal: advances/ascent on commands; C does not re-open glyph advance ownership.

---

## 4. Recommended PR shape (1–2 nights after gate)

### Night C0 — probe before patch (mandatory; Atlas method, 3-for-3)

Before editing IFC:

1. On **post-#37 master**, run `mixed-inline-img.html` → layout.json / y_table.  
2. Capture Chrome (CfT 148) vs RustKit:  
   - Y of text “before” baseline band vs img bottom edge (baseline rows).  
   - Y of img mid vs text mid (`.mid` row).  
3. Write three numbers into the PR body: `rk_img_bottom`, `rk_text_baseline`, `chrome_delta`.  
4. **If** baseline rows already match within ~2px structural band, C shrinks to `middle` only — do not invent work.

**Falsification fixture rides with the PR** (not a separate doc after the fact).

### Night C1 — place by baseline (default)

1. In **both** IFC loops, when positioning an inline member on the current line:  
   - Compute / update running `line_baseline_offset` from text metrics + strut.  
   - For `baseline_is_bottom_edge()` children with `vertical_align == Baseline`: set content Y so **margin bottom** lands on baseline.  
2. Keep `line_below_baseline` / strut descent so empty atomic + lone img line height tests stay green (`test_inline_block_border_box_position_and_line_strut`, lone inline-flex height).  
3. Units:  
   - `text + 16×16 img + text` share one line; `img.margin_box().max_y() ≈ text_baseline ± 1px`.  
   - Dual-path: same assertion through `layout_with_collapse`.

### Night C2 — `middle` (same PR if C1 is small)

1. Read `child.style.vertical_align`.  
2. `Middle` → midpoint rule above.  
3. Fixture `.mid` row hard-assert.  
4. Leave other enum variants unmatched (`_` → baseline behavior) with a one-line comment “Slice C subset”.

### Explicit non-combine

Do **not** fold into C:

- DIG-2 form buttons (separate dig PR; queued by Atlas)  
- Nested-inline fragmentation  
- Campaign / KF threshold edits  
- CI workflow churn (CI-1/2 already shipped #38/#40)  
- GradientText (already shipped #39)  
- Windows DW port (Athena ports contract when IFC reaches line-level valign)

---

## 5. Files likely touched (~estimate)

| File | Change |
|------|--------|
| `crates/rustkit-layout/src/lib.rs` | Both IFC place loops; maybe tiny helper `fn align_inline_member_y(...)`; units |
| `parity-tests/repro/mixed-inline-img.html` | already present — only if probe needs a stricter oracle band |
| optional `parity-tests/repro/mixed-inline-valign-middle.html` | only if splitting baseline vs middle fixtures helps CI clarity |

Expected size: **~80–150 LOC** layout + tests if C1+C2 stay scoped. If it grows past “shared line model rewrite,” stop and split.

---

## 6. Outside-eye checklist (Prometheus when PR opens)

- [ ] Gate §0 cited in PR body (B2 merge SHA + wrap probe receipt).  
- [ ] Dual-loop mirror (or shared helper used by both).  
- [ ] `vertical_align` actually **read** for Baseline + Middle; others fall through intentionally.  
- [ ] `baseline_is_bottom_edge` img: margin-bottom on baseline (probe numbers in body).  
- [ ] Strut unit tests still green (empty atomic line height).  
- [ ] No text-align / x_offset rewrite; no GradientText; no threshold churn.  
- [ ] Fixture rows: left/center/right still one line; `.mid` moves img only.  
- [ ] Portable paragraph for Athena (contract only).

---

## 7. Guidance by seat

### Atlas

1. **Gate open** — see `2026-07-11-ifc-slice-c-GATE-OPEN.md`.  
2. **C0 probe → C1/C2** from this brief (mandatory probe numbers in PR body).  
3. Optional parallel (separate PR): DIG-2 buttons from css-selectors heatmap.  
4. Ring Prometheus for outside-eye when C PR opens.

### Athena

Portable contract only until Windows IFC is on line-level place:

- Layout owns vertical-align for replaced + empty atomic.  
- Paint does not invent baseline for images.  
- Same dual-path mirror if Windows still has two block-children entry points.

### Pete

- C is quality structure (mixed replaced baseline), not a campaign-avg promise.  
- css-selectors residual post-DIG-1 is **16.65** (was ~18.97) — still dig debt (DIG-2+), **not** a matcher reopen; not a C scoreboard promise.

---

## 8. Residual map (context, not C scope)

Local attribution snapshot (working tree diffs; may predate some merges — re-measure after B2):

| Case | ~diff% | Dominant taxonomy |
|------|--------|-------------------|
| image-gallery | 21.4 | text_metrics |
| css-selectors | 19.0 | text_metrics |
| settings / sticky / about | 16–18 | gradient + text_metrics |

C may nibble **image-gallery** / mixed-inline structure; it will **not** clear gradient cliffs or pure advance font delta. Do not sell C as a scoreboard sweep.

---

## 9. Sequencing (updated ladder)

```
wrap → advances → mixed share lines → line-level align → mid-line Center/Right → baseline/valign
#15     #36         A+B #31            A+B                B2 #37 (open)           **C (this brief)**
```

Standing parallel chores (not C): GradientText advance-carry · CI path re-home · H3 gate honesty after aggregate finds data.

---

## 10. Non-goals (repeat)

- Implementing before §0 gate  
- Prometheus engine or merge  
- Full css-inline baseline-source matrix  
- `vertical-align: top/bottom` line-box semantics  
- Matching PR #22 +1.7px font delta  
- Raising/lowering campaign thresholds to pretty the board  

---

## Receipts

- Sketch: `trench/IFC_PHASE3_SKETCH.md` § Slice C  
- B2: `forensics/2026-07-11-ifc-b2-midline-split-BRIEF.md` · `…-ifc-b2-PR37-REVIEW.md`  
- Advance residual: `…-gradienttext-advance-carry-IMPLEMENT.md`  
- Strut history: PR #22 / `…-post22-settings.md`  
- WPT menu: `trench/WPT_TIER1_SUBSET.md` Tier-1B  
- Method: probe-before-patch (Atlas day falsifications; Prometheus css-selectors empty_siblings miss)

— Prometheus
