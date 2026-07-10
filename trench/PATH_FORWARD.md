# Path forward — Atlas + Athena (value / Chrome-parity)

**Author:** Prometheus · **Date:** 2026-07-10 · **Audience:** Pete, Atlas, Athena  
**Premise:** Fleet loops work; discounted trust lifted by Pete. Optimize for **pass-rate and real-page readability**, not busywork. Large multi-day bets are in scope when ROI is high.

---

## 1. Where we actually are

### Atlas (macOS) — parity *leader*

| Signal | State |
|--------|--------|
| Campaign metric | ~**21/26 (80.8%)** @ t15, avg ~**11.4** (post-#22/#23 territory; re-measure after every merge) |
| Line-box lane | Phases 1–5 largely **shipped** (#15–#20): wrap, min-content text, shared lines, whitespace, mid-line split |
| Recent high-ROI | **#22** strut/border-box; **#23** Absolute/Fixed + flex definite cross + `inset:0` (shelf PASS, toggles exact); **#24** length parse SSO (dup audit) |
| Remaining shape | Fewer *missing features*, more **hard residuals**: sticky/scroll, selector/paint leftovers, about (bg-clip:text / shrink-to-fit), network images, gradient micro-diffs |

macOS is past “make text wrap.” Further gains are **fewer, harder, higher leverage per fix** — or multi-day systems that unlock whole classes.

### Athena (Windows) — capability *catch-up* (correct lane)

| Signal | State |
|--------|--------|
| Early baseline | 1/12 @ t15, paint/cascade nearly dead |
| Recent high-ROI | **#5** zero-width kill; **#6** real cascade; **#7** ClearType glyphs; **#8** text wrap; **#9/#10** IFC + real DW widths (re-land after merge race); **#11** bullets/tables/inputs |
| Structural truth | Windows fork **is not** macOS rustkit; file-level salvage of full macOS engine was falsified. Native cascade + port *semantics* is the winning path. |
| Gap vs Chrome | Still large on suite %, but **foundation** (style → text → inline flow) is finally real |

Windows should **not** chase macOS’s last 5 failing micros. It should **import the feature classes** macOS proved move real pages, then re-measure.

---

## 2. Value model (how to pick work)

```
value ≈ (suite pages unlocked + real-site readability)
        / (days × review risk × fork-divergence tax)
```

| Prefer | Deprioritize |
|--------|----------------|
| Unlocks a **class** (positioned, sticky, paint images, cascade) | ±1–2pp glyph/strut polish |
| Shared **contract** both seats can implement | One-seat-only micro hacks |
| Fixes **measurement lies** | Matching Chrome bugs (QUIRKS) |
| Multi-day with clear milestones | Big bang with no intermediate metric |

---

## 3. Recommended path — **Atlas (macOS)**

### Now → 2–3 days (execute)

| Priority | Work | Why |
|----------|------|-----|
| **A1** | **Committed full-suite receipt** after #22/#23/#24 | Scoreboard honesty; ranks the real top-5 fails |
| **A2** | **Finish flex definite-cross / §11b** if anything remains post-#23 | Settings-class UIs; already half-done in #23 — close the ledger with tests |
| **A3** | **Top residual dig** from post-merge table (likely **css-selectors** paint, **about** shrink-to-fit / bg-clip, or **gpu-gradient** residual) | Best *short* ROI once ranked |

### Multi-day bet #1 (highest Chrome-parity ROI on macOS) — **Scroll + sticky + overflow**

**Why big:** `sticky-scroll` has been the structural worst case all campaign; real sites are scroll-dominated; #23 activated Absolute/Fixed — sticky is the natural sequel (positioned family).

**Scope (3–5 trench days):**

1. Spec map: `position:sticky` containing block, sticky constraint rectangle, scroll container detection.  
2. Overflow: `overflow:auto/scroll` scrollport + clip (even without scrollbars UI).  
3. Sticky paint/layout coupling in rustkit-layout + compositor.  
4. Suite: sticky-scroll + any overflow micros; **manual** real article page as human gate.

**Exit:** sticky-scroll enters “near t15 or diagnosed as paint-only residual”; one real scrolled page looks intentional in the app.

### Multi-day bet #2 (north star) — **IFC quality, not more phase labels**

Phases 1–5 exist; remaining pain is **quality**:

- Line-level `text-align` for mixed runs (session-3 falsification)  
- Baseline / `vertical-align` for replaced + text  
- Advance-based breaks (replace estimate where DW/CT already shapes)  
- vertical rhythm vs Chrome ±1–2px → **QUIRKS**, don’t grind

**Exit:** “Some **bold** text” centers as one line; mixed inline+img doesn’t explode; Friday WPT Tier-1 (css-text/css-inline) has a **number**.

### Multi-day bet #3 (platform debt with pixel payoff) — **Parser SSO completion**

#24 started length. Continue: **color, gradient, shorthand** only in `rustkit-css`; delete engine island; one `Color::lerp` (linear for gradients).  

**Exit:** no dual parse_color; gradient digs stop regressing when css changes.

### Atlas — explicit non-goals (this phase)

- Porting **fastrender** as capture engine mid-campaign (Friday strategy only)  
- Matching +1.7px strut font delta  
- Windows tasking (review Athena PRs; don’t divert nights)

### Atlas sequencing (recommended)

```
Week slice:
  Day 0: A1 re-measure → publish top-5 fail table
  Days 1–4: Bet #1 sticky/overflow (milestones each night)
  Parallel chore: Bet #3 one delete PR every 2 feature PRs
  When sticky plateaus: Bet #2 IFC quality sprint (2–3 days)
```

---

## 4. Recommended path — **Athena (Windows)**

### Now → 2–3 days (execute)

| Priority | Work | Why |
|----------|------|-----|
| **W1** | **Honest suite number** after #6–#11 on pinned CfT 148 | Can’t steer without post-cascade/text baseline |
| **W2** | **Port positioned semantics from macOS #23** (Absolute/Fixed + inset stretch) on *Windows engine* | Highest portability from today’s macOS win; settings/shelf-class UIs |
| **W3** | **Land open CI PRs (#3/#4)** so Windows truth shows up in hub CI | Stops “decorative badge” failure mode |
| **W4** | **Image paint path** (macOS #11 class: bind real textures, not glyph atlas) | Builtins/websuite were ~99% paint-dead; cascade alone doesn’t paint photos |

### Multi-day bet #1 (highest ROI on Windows) — **Paint stack: images + backgrounds/gradients**

**Why big:** Athena’s own Phase 0 autopsy: display lists were almost only Text + SolidColor. Cascade + text without paint keeps builtins near-useless.

**Scope (3–5 days):**

1. Image decode → texture → correct bind group (port macOS #11 lessons, implement in Windows renderer).  
2. Background layers + basic linear gradients (reuse css types; one paint path).  
3. Re-measure builtins (about, settings, new_tab, shelf) — expect **class** moves, not +1pp.

**Exit:** builtins leave the ~99% cliff; at least one gradient websuite case becomes “layout-shaped residual” not “white page.”

### Multi-day bet #2 — **Flex/grid parity with macOS contracts**

Port **semantics** (not files) from macOS:

- Flex definite cross size / §11b  
- Border-box flex sizing (#14)  
- Grid `1fr` min-content (#5 macOS) if Windows grid is live  

**Exit:** settings-like rows and card-grid stop being infinite columns / blown toggles.

### Multi-day bet #3 — **IFC convergence checklist with macOS**

Keep Windows IFC (#9/#10) but maintain a **shared checklist** (slice ladder): wrap → real advances → mixed inlines → line-level align. Avoid a third divergent line model.

**Exit:** same HTML fixture corpus passes “horizontal flow” on both seats; divergences ledgered.

### Athena — explicit non-goals

- Wholesale macOS engine transplant (already falsified)  
- Chasing macOS’s last micro fails before paint works  
- Silent stack merges that drop PRs (#9 race) — use linear history / merge trains

### Athena sequencing (recommended)

```
Day 0: W1 full suite receipt + top fails
Days 1–2: W2 positioned port (from #23 notes) + W3 CI
Days 3–6: Paint bet #1 (images first, then backgrounds)
Then: flex/grid contracts; IFC checklist with Atlas
```

---

## 5. Cross-seat coordination (avoid thrash)

| Topic | Rule |
|-------|------|
| **Review** | Athena post-hoc on macOS shared crates still fine; reverse: Atlas reviews Windows **design** when IFC/flex contracts change |
| **Merge trains** | One PR → master at a time on Windows until stack tooling is safe |
| **Portable notes** | Every macOS layout PR lists “Windows exposure” in 5 lines (Athena already does the reverse) |
| **Metric** | Same formula: pass @ t15 vs CfT 148; Windows may use smaller case set until harness full — **label it** |
| **Big bets** | Only **one** multi-day epic per seat at a time; other seat does portable support or chore SSO |

---

## 6. Pete decision board (optional)

1. **Green-light Atlas multi-day sticky/overflow** as macOS main epic? (Recommended: **yes**)  
2. **Green-light Athena multi-day paint (images→gradients)** as Windows main epic? (Recommended: **yes**)  
3. **IFC quality** as the *shared* Friday epic after both have one intermediate metric win? (Recommended: **yes**)  
4. Defer fastrender-vs-rustkit strategic call until sticky+paint land? (Recommended: **yes** — don’t open a third front)

---

## 7. One-line assignments

| Seat | Next week in one line |
|------|------------------------|
| **Atlas** | Re-measure → **sticky/overflow multi-day** (with parser SSO chores in between) → then IFC quality. |
| **Athena** | Re-measure → **port positioned #23 semantics** → **image/gradient paint multi-day** → flex contracts. |
| **Prometheus** | Forensics for sticky containing-block + paint bind checklist; IFC quality design when they start; challenge Chrome-parity traps. |

---

## 8. Success in 7 days

| Seat | Success looks like |
|------|---------------------|
| Atlas | sticky-scroll no longer “hopeless structural”; committed pass rate **≥22–23/26** or clear paint-only residual |
| Athena | builtins **off the 99% cliff**; documented suite % that a human believes |
| Both | One shared IFC fixture file both seats run; portable notes on every epic PR |

— Prometheus
