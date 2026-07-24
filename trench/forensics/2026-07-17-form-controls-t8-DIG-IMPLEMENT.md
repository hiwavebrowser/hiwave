# Implement brief: form-controls primary t8 dig (unblocks #55 / #56)

**Author:** Prometheus · **Date:** 2026-07-17 (grind tick, headless)  
**Status:** **EXECUTED** (Atlas night 18 → tip `251b105`) · outside-eye **APPROVE merge** 2026-07-20 (`2026-07-20-form-controls-t8-DIG-OUTSIDE-EYE.md`) · RESULT `2026-07-18-form-controls-t8-DIG-RESULT.md`  
**Exists in service of:** honest merge of DIG-buttons (#55) + metrics land (#56) — both HOLD solely on micro scope cap **t8** for `form-controls`.  
**Elevates:** `2026-07-17-pr54-55-56-STACK-REVIEW.md` §2 blocking CI finding  
**Consumes:** Chrome CfT-148 `baselines/chrome-148/micro/form-controls/{layout-rects,computed-styles}.json`; DIG-1/DIG-2 bare-blob contract; #55 tip `7c5d507`  
**Distinct from:** DIG-buttons InlineBlock (keep); PAINT-0 (closed seating); metrics model; css-selectors S6 author-pad height (already green under #55)  
**Lane:** dig chore on top of #55 (or stacked follow-up PR) — **do not** reverse InlineBlock; **do not** raise thr/scope cap without Pete  
**Non-goal:** Prometheus execute · KF games · fold into website/C3a · Windows port

---

## 0. Verdict (one screen)

| Claim | Status |
|-------|--------|
| #55 design (UA `InlineBlock`) is correct | **TRUE** — Chrome computed `display:inline-block` on bare form controls; css-selectors §6 fixed (`.buttons` h 124.6→33.4) |
| Aggregate red is PATH-BUG | **FALSE** — form-controls primary **10.090% > max 8.0** (micro scope cap) |
| #54 form-controls | **7.978% PASS** (same micro case, pre-InlineBlock) |
| #55 / #56 form-controls | **10.090% FAIL** (metrics does not move the number) |
| Smoking gun (design, pre-probe) | Bare **intrinsic height** mismatch: Chrome **h≈19** (pad 0 + border 2px) vs RK bare blob **~28 (input/select) / ~32 (button)** when `author_pb_v==0` |
| UA form arm sets border/pad? | **NO** — only `display` + font 13.333 + system-ui (`engine/lib.rs` form arm) |
| DIG-1 bare blob preserved "for form-controls look" | Contract was "don't compose author pad when zero" — **not** "blob equals Chrome". Blob ≠ Chrome 19. |
| Atlas action | **Probe layout A/B → fix bare single-line height toward 19 without breaking author-pad compose → re-sim aggregate ≤8** |
| Do **not** | Revert InlineBlock · raise t8/scope · silent known_fail without Pete · paint-only thrash before layout |

---

## 1. Live pins (this tick)

| Pin | Value |
|-----|------:|
| origin/master | `5161571` (#53 merged) |
| #54 PAINT-0 | OPEN · APPROVE · form-controls **7.978** |
| #55 DIG-buttons | OPEN @ `7c5d507` · design APPROVE / **HOLD merge** |
| #56 metrics | OPEN · inherits #55 form-controls **10.090** |
| Gate | `parity_gate.py --per-case-thresholds --primary-viewport-only`; micro scope → **max_diff=8.0** for form-controls |
| Fixture | `websuite/micro/form-controls/index.html` (intrinsic sizing battery; 12 tests) |
| Chrome oracle | CfT-148 layout-rects + computed-styles @ `baselines/chrome-148/micro/form-controls/` |
| Primary VP | **800×1200** (body Chrome h≈1716 — lower sections clipped; Y cascade matters) |

### Gate receipt (from stack review re-sim; matches CI)

```text
form-controls: diff 10.090104166666666 > max_diff 8.0  (known_fail=False)
```

Campaign board thr (form_controls category 12) still "passes" 10.09 — **CI is tighter**. Swarm-green ≠ merge-ready.

---

## 2. Chrome ground truth (CfT-148, form-controls micro)

Measured from `computed-styles.json` + `layout-rects.json` (viewport 800×1200):

| Control class | display | pad | border | h (Chrome) | w (Chrome) | Notes |
|---------------|---------|-----|--------|------------:|-----------:|-------|
| text/email/password/number input | inline-block | 0 | **2px** | **19** | 149 (default) | fs 13.333 |
| input width:300 | inline-block | 0 | 2px | 19 | 300 | author width only |
| bare button | inline-block | 0 | **2px** | **19** | label-dependent | test3 one line |
| fixed button 200×50 | inline-block | 0 | 2px | 50 | 200 | explicit dims |
| checkbox / radio | inline-block | 0 | 0 | **13** | 13 | |
| select single | inline-block | 0 | 1px | 19 | ~137 | |
| select multiple size=3 | inline-block | 0 | 1px | 50 | ~39 | |
| textarea default | inline-block | 0 | 1px | 32 | 178 | |
| textarea rows=5 cols=40 | inline-block | 0 | 1px | 77 | 338 | |
| range | inline-block | 0 | 0 | 16 | 129 | |
| color | inline-block | 0 | 1px | 27 | 50 | |
| flex row (test11) | **block** (flex items) | … | … | 19 | … | author `display:flex` on container |

**Implication:** Chrome's "UA look" for bare single-line controls is **~19px border-box with 2px border and 0 padding**, not a 28–32px blob.

---

## 3. RK mechanism (causal chain on #55)

```text
#55 UA arm (CORRECT — keep):
  button|input|select|textarea =>
    display = InlineBlock   // was Block → stacked; now packs like Chrome
    font_size = 13.333
    font_family = system-ui
    // NO border, NO padding  ← gap vs Chrome computed border 2px

layout_form_control bare path (author_pb_v == 0):
  TextInput/Select height = fs*1.5 + 8  = 13.333*1.5+8  ≈ 28.0
  Button height           = fs*1.5 + 12 = 13.333*1.5+12 ≈ 32.0
  Checkbox/Radio          = fs*1.2                       ≈ 16.0   (Chrome 13)

author_pb_v > 0 (css-selectors S6 pad 8+8):
  height = (fs+1) + author_pb_v   // DIG-1/DIG-2 compose — leave alone
```

### Why InlineBlock made the micro score *worse* (+2.1pp)

Not because InlineBlock is wrong. Because:

1. **Block stacking** inflated early containers (esp. test3 multi-control row) and pushed lower sections **below** the 1200 primary VP clip — some error mass was off-screen.  
2. **InlineBlock packing** matches Chrome flow: more of the page (and more bare-height error surface) sits **inside** the primary VP → higher `%diff` under an honest geometry.  
3. Same pattern as PR #53 / css-selectors S6 unmask: fix stacking cancel → residual becomes visible.

So the dig is **not** "undo #55"; it is "finish bare intrinsic sizing so packing is honest **and** heights match."

### File:line inventory

| Site | Role | DIG action |
|------|------|------------|
| `crates/rustkit-engine/src/lib.rs` form UA arm (~2015) | display + font only | **Candidate:** add UA border 2px (text-like inputs/buttons) / 1px (select/textarea) matching Chrome computed — **only if probe shows style border missing and height wins** |
| `crates/rustkit-layout/src/lib.rs` `layout_form_control` ~1395–1452 | `single_line_box` + bare blobs | **PRIMARY height lever:** bare branch (`author_pb_v==0`) must land ~**19** for TextInput/Button/Select single-line; keep compose branch for author pad |
| same Checkbox/Radio ~1446 | `fs*1.2` | Secondary: → **13** if probe ranks it |
| TextArea branch | `fs*1.2*rows+8` | Tertiary after single-line |
| Render `DisplayCommand::TextInput` border_width **hardcoded 1.0** | paint vs layout | **After** layout ≤8; do not paint-chase first |
| Button paint `_border_radius` / char×0.5 center | DIG-2 residual | Out of t8 scope unless still dense post-height |
| css-selectors S6 author pad | compose path | **Do not touch** if probe green |
| Gate / registry thr | t8 micro | **Do not raise** without Pete |

### Predicted bare heights (no local capture this seat — verify on probe)

| Control | Chrome h | RK bare formula | Δ if unfixed |
|---------|---------:|-----------------|--------------|
| text input | 19 | 28 | +9 |
| bare button | 19 | 32 | +13 |
| select | 19 | 28 | +9 |
| checkbox | 13 | ~16 | +3 |

Width: Chrome default text input **149** vs RK `fs*12≈160` — secondary (less Y-cascade impact).

---

## 4. Implement contract (Atlas)

### 4.0 Probe gate (mandatory before patch; ≤30–45m)

Capture form-controls layout under **#55 tip** (flat metrics OK; metrics stack optional second dump).

| Step | Check | Pass |
|------|-------|------|
| P0 | Layout dump exists @ 800×1200 | file |
| P1 | Join Chrome layout-rects by tag+order (or selector if available) | table of N controls |
| P2 | Rank top-15 by \|Δh\| then \|Δy\| | bare single-line dominate if H1 true |
| P3 | test3: five controls **same line** (post-#55) | same y ±2; x increasing |
| P4 | test1 first text input | report RK (w,h) vs Chrome (149, 19) |
| P5 | One author-pad control from css-selectors (or micro with pad) still **~31** if pad 8+8 | compose not broken |

If P2 shows height Δ is **not** the top residual (e.g. pure paint/AA), **kill H1** and re-rank — do not ship a theory.

### 4.1 Preferred patch order

**H1 — bare single-line height (primary)**

Pick **one** of these; probe picks the winner:

| Option | Change | Pros | Cons |
|--------|--------|------|------|
| **A (recommended if style borders are the missing UA)** | UA arm: set `border_*-width = 2px` (input/button) / `1px` (select/textarea) + colors close to Chrome | Uses existing `single_line_box` compose: author_pb_v=4 → (fs+1)+4≈**18.3** ≈19 | Must confirm border participates in `author_pb_v` and does not double-count paint; author `border:none` pages still compose |
| **B (direct blob calibrate)** | Bare branch: TextInput/Select blob → **19.0** (or `fs+1+4`); Button bare → **19.0** | Explicit; matches oracle | Magic constants; document as Chrome form-controls calibrated |
| **C** | A + B belt: UA border for paint/layout consistency + blob fallback if border zero | Most Chrome-like | Slightly larger diff |

**Invariant:** when `author_pb_v > 0` (css-selectors S6), height stays `(fs+1)+author_pb_v`. **Do not** apply bare blob when author pad/border present.

**H2 — checkbox/radio 13×13** only if H1 lands and residual still >8 with checkbox density high.

**H3 — default text input width 149** only if residual is width-dominated after H1 (unlikely for %-diff vs Y cascade).

**H4 — paint border_width vs layout** only after layout gate green or as separate chore.

### 4.2 Explicit non-fixes

| Do not | Why |
|--------|-----|
| Revert `display = InlineBlock` | Correct vs Chrome; S6 depends on it |
| Raise micro scope cap / form thr | Hides honesty; needs Pete |
| known_fail without Pete ack | Policy; stack review option 2 only with explicit bank |
| Fold metrics (#56) into this dig | Orthogonal; metrics does not fix form-controls |
| Change global `Display` default | Over-broad |
| "Fix" by padding body / clipping | Theater |

### 4.3 Done-when / merge gate

| Gate | Bar |
|------|-----|
| form-controls primary VP | **≤ 8.0** (or Pete-authorized known_fail + kf_ceiling with margin) |
| css-selectors §6 | still same-y buttons; container h **≤ 42** |
| campaign | no new case flips vs #55 baseline; about/gallery unchanged class |
| units | bare input/button height ≈19 ±1 when no author pad; author-pad button still ≈31 |
| KF / thr files | **unchanged** unless Pete known_fail path |
| #55 / #56 | merge only after this gate (or known_fail banked) |

### 4.4 Suggested PR shape

1. **Preferred:** commit dig on top of `atlas/dig-buttons-stack` so #55 becomes green, then merge #55 → #56.  
2. **Alt:** separate `atlas/form-controls-bare-height` stacked on #55; outside-eye trivial if height-only.  
3. Title idea: `fix: bare form-control height ≈ Chrome 19 (unblocks dig-buttons t8)`.

---

## 5. Outside-eye checklist (Prometheus when dig PR opens)

- [ ] InlineBlock retained for form UA arm  
- [ ] Bare single-line heights moved toward Chrome 19 (probe table in PR body)  
- [ ] Author-pad compose path still produces ~31 for pad 8+8 buttons  
- [ ] form-controls primary ≤8.0 (paste gate line)  
- [ ] sec6 / css-selectors not regressed past #55 campaign receipts  
- [ ] No thr/scope/KF silent moves  
- [ ] Paint-only changes not claimed as layout fix without numbers  

---

## 6. Seat routing

| Seat | Action |
|------|--------|
| **Atlas** | Probe §4.0 → H1 patch → re-sim aggregate → land on #55 stack → then merge #54 anytime, #55, #56 |
| **Prometheus** | This pin is the design unit; re-eye only if dig is non-trivial or known_fail text drifts |
| **Athena** | No Windows port until macOS #55+#56 green on master |
| **Pete** | Only if Atlas proposes known_fail / thr / scope change instead of H1 |

---

## 7. Sequencing vs other residuals

| Residual | Blocks #55/#56? | Notes |
|----------|-----------------|-------|
| **This dig (form-controls t8)** | **YES** | sole merge hold |
| Website Tank blurb | No | still 0 Tank on production; parallel product gravity |
| Tank C3a sticky | No | honesty P0 other repo |
| Tank R4 calibrate | No | post-#5 pin banked |
| null #83+#84 / Aleph #29 | No | prior APPROVE, Atlas merge |

---

## 8. Learn (one screen)

DIG-buttons fixed the **display** half of Chrome form UA; form-controls t8 fails on the **sizing** half. Bare RK blobs (28/32) were a deliberate DIG-1 isolation choice, not a Chrome match. Primary VP + InlineBlock packing unmasks that isolation as a merge blocker. Fix height honesty under the existing `single_line_box` compose contract — do not undo the display fix, and do not negotiate the gate.

— Prometheus / design only / 2026-07-17 grind tick
