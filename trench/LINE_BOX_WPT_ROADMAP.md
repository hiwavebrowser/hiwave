# HiWave line-box / WPT roadmap

**Author:** Prometheus (Grok seat) · **Date:** 2026-07-10 · **Status:** design / strategy  
**Audience:** Atlas (macOS), Athena (Windows), Pete (Friday agenda)  
**Scope:** advise only — no merges, no force-push, no harness rewrites this tick.

One page of strategy. Ties the campaign's dual metrics to the line-box lane Pete
greenlit 2026-07-09, and names which WPT slices buy "replace Chrome" vs which
are Chrome-parity thrash.

---

## 1. Two meters, one north star

| Meter | What it measures | Role |
|-------|------------------|------|
| **Campaign metric** (nightly) | Unified pass rate @ t15 vs **pinned CfT 148** on the websuite/builtins set | Trench motion; noon digests; seat scoreboard |
| **North star** (Friday trendline) | **WPT / reftest pass-rate** — absolute conformance to CSS/HTML specs, *not* "matches Chrome's bug" | "Replace Chrome" credibility; escapes the parity trap |
| **Human read** (always) | Can a real page's **paragraphs wrap, cascade paint, images show, cards flex** without looking broken? | Ship gate for demos / reddit audience |

PLAN.md already says this. Practice drifts: nights optimize the campaign metric;
WPT Phase 0.5 is still a stub (`tests/wpt/` = a handful of toy HTML files +
January harness work-order "completed"). This doc re-anchors.

**Rule of thumb:** move campaign pixels *through* subsystems that also increase
WPT pass rate. If a pixel dig only makes us more like Chrome and *less* like the
spec, ledger it in `trench/QUIRKS.md` (create when first needed) and stop.

---

## 2. The Chrome-parity trap (name it so we can refuse it)

Trap patterns observed this campaign:

1. **Taxonomy misdirect** — `gradient_interpolation` blamed two nights; true cause
   was line-box geometry (strut / vertical drift). Attribution is a hint, not a lane.
2. **Pixel grind on dead features** — chasing gradients/images while text never
   wraps. Real pages are text-dominated; wrap is the needle (session 9: ≥6 of 8
   remaining macOS fails paid the no-wrap tax).
3. **Matching Chrome's bugs** — over-constrained margin quirks, font-metric
   ±1.7px strut deltas. Spec wins; Chrome-only quirks go in QUIRKS and drop.
4. **Honest-vs-instrumentation lies** — reset-less Chrome baselines, liveness-only
   smoke, January-pinned gitlinks. Measure truth first; then engine work.
5. **100% pixel plans as identity** — historical `100pct-pixel-parity-plan.md` /
   98% folklore. Those docs are archaeology. Campaign uses **today's** ledger and
   pinned CfT 148, not January memory.

**Refuse the trap:** a night that raises t15 by chasing a Chrome-only quirk while
line-box/WPT stay flat is a *failed* night, even if the digest number is green.

---

## 3. "Replace Chrome" for HiWave (what actually has to work)

Not "pass all of WPT." Not "byte-match Chrome." The product dream (mirror
session): a real browser people open instead of Chrome for daily reading/apps.

**MVP product surface (ordered by user pain on real pages):**

| Rank | Capability | Why | Current truth (2026-07-10) |
|-----:|------------|-----|----------------------------|
| 1 | **Text wraps in content width** | Without this, every article/card is broken | macOS: `wrap_text` exists, **zero production callers** (session 9). Windows: #8 greedy estimate wrap = **slice-1 only** (not IFC) |
| 2 | **Cascade + specificity** | Unstyled HTML is not a browser | macOS: real. Windows: #6 shipped minimal cascade (engine-local; crate re-unify is Friday) |
| 3 | **Glyphs + images paint** | Empty boxes fail demos | macOS: glyphs+images fixed. Windows: #7 DirectWrite glyphs; images still lag |
| 4 | **Block + simple flex** | Cards, settings, shelves | Both seats grinding; flex-item definite height still open on macOS |
| 5 | **Basic inline-block / line metrics** | Vertical rhythm, badges, pills | macOS #22 (strut descent) open; Windows not there |
| 6 | **Position sticky / scroll** | One showcase page | Defer dedicated dig; not the main lane |

Everything below that (full grid, animations, service workers, WebGL, full SVG,
JS fidelity) is **post-MVP**. Do not spend trench nights there until wrap +
cascade + paint are boring.

---

## 4. Line-box lane — honest names, ordered slices

**Naming (from Prometheus #8 review):** call Windows #8 *"text-node greedy wrap
(estimate)"* — **not** "line boxes." Real line boxes start when mixed inlines
share a line (spans, images, form controls). Digests that say "Windows has line
boxes" after #8 are wrong and will mislead Friday.

### Shared contract (keep forever)

- `word-break: normal` / css-text-3 §5.2: unbreakable unit **overflows**, never
  mid-word force-break unless `word-break`/`overflow-wrap` say so.
- Layout width estimate **===** paint wrap estimate (disagreement > both approximate).
- Line height honors authored multiplier; multi-line box = N × line-height (until
  real strut metrics replace the estimate).
- Do not couple wrap work to flex/intrinsic "card smartness" PRs.

### Slice ladder (both seats; implement on own fork, converge semantics)

| Slice | What | WPT / reftest signal | Owner hint |
|------:|------|----------------------|------------|
| **0** | Wire wrap into production layout path | campaign: article-typography / card-grid descriptions shrink toward Chrome | macOS: *still open* — highest leverage night. Windows: #8 ≈ done |
| **1** | Greedy soft wrap on whitespace (estimate OK) | local unit: long word overflows, not broken | Windows shipped; macOS needs production callers |
| **A** | Mandatory breaks (`\n`, `white-space: pre-line`) | css-text white-space cases | cheap follow-on |
| **B** | Advance-based break points (DirectWrite / CoreText) | reftests stabilize across fonts | portable-win #1; keep estimate fallback |
| **C** | First-line residual width API | css-text-3 §5.2 residual; entry to IFC | only after true IFC host exists |
| **D** | Soft opportunities beyond `split_whitespace` (UAX #14, `overflow-wrap`) | css-text overflow-wrap / word-break | after B |
| **E** | **Real line boxes** (mixed inlines share a line; strut; baseline) | css-inline + css2.1 §10.8 | macOS #22 is a piece of E; Windows later |

**macOS this week:** Slice 0 is the missing call. Until `layout_text` emits
multiple line runs into the display list, campaign residual stays text-taxed
regardless of flex polish.

**Windows this week:** Hold #8 contract; optional A then B. Do not invent IFC
(C/E) until the paint stack can host it. Do not mid-word break to chase pixels.

---

## 5. WPT slices that matter (and which to ignore)

Phase 0.5 still needs a **minimal real runner** (either seat): clone/subset WPT,
run testharness + a few reftests, publish pass-rate on Friday. Toy
`tests/wpt/{layout,parse,style,reftest}` is not a trendline.

### Tier 1 — fund the north star (subset aggressively)

Pull only directories that exercise the MVP surface. Prefer **reftests and
testharness for layout math** over full browser chrome.

| WPT area | Why it maps to replace-Chrome | Line-box link |
|----------|-------------------------------|---------------|
| **css/css-text** | Soft wrap, overflow, white-space, word-break | slices 0–D |
| **css/css-inline** | Line boxes, baseline, strut, vertical-align basics | slice E / #22 |
| **css/css-cascade** + **selectors** | Real styled pages | Windows #6 path |
| **css/css-flexbox** (basic only: grow/shrink, wrap, definite sizes) | Cards/settings | flex-item height bug |
| **css/css-box** / **css21/box** | Margin collapse, width constraints | already partially ground |
| **html/rendering** (replaced elements: img sizing) | Images not placeholders | macOS #11 family |

**Exit criteria for Tier 1 subset:** a fixed list of ≤200 tests checked into the
harness (manifest), run in CI or nightly, pass-rate on Friday trendline. Grow the
list only when a campaign dig would have been clearer with a WPT assertion.

### Tier 2 — later (do not open lanes now)

css-grid full, css-position sticky edge matrix, css-overflow scrollport
sophistication, css-fonts full metric matrix, css-images gradients-as-identity,
css-animations/transitions, full SVG, service workers, WebCrypto, WebGL.

### Tier 3 — refuse unless QUIRKS demands it

Any test whose failure is "Chrome does X, spec says Y" — record Chrome as
deviant, match the **spec**, leave the campaign pixel red if needed.

### How WPT and the campaign metric interact

```
real page bug ──► minimal repro ──► unit test in rustkit-*
                      │
                      ├─► if it's text/inline/flex/box → also add/track WPT id
                      └─► if only Chrome pixels differ & spec agrees with us
                            → QUIRKS.md, do not "fix" toward Chrome
```

Nightly still digests **t15 vs CfT 148**. Friday also plots **Tier-1 WPT %**.
A week with flat WPT and rising t15 only via Chrome-quirk matching is a warning.

---

## 6. Seat actions (next units — no irreversible acts from this doc)

### Atlas (macOS) — highest campaign leverage
1. **Slice 0:** production-call `TextShaper::wrap_text` / equivalent from
   `layout_text`; multi-line display-list paint. Measure card-grid +
   article-typography before/after. This is the session-9 main lane, still open.
2. Land / merge path for **#22** (inline-block line metrics) per Pete/review policy.
3. Next residual after wrap: flex-item definite height (settings repro already
   committed). Keep it *after* wrap if both compete for one night.

### Athena (Windows)
1. Merge **#6 / #7 / #8** when checks green (Prometheus design-approved; seats
   execute merges). Name #8 correctly in digests.
2. Optional polish: slice **A** (mandatory breaks) if showcase content needs it;
   then **B** (DirectWrite advances). No IFC cosplay.
3. When free: help stand up **Phase 0.5** Tier-1 WPT runner (shared skill; either
   seat) — Windows already has `rustkit-test` scaffolding from January.

### Prometheus (this seat)
1. This document = design unit. Review only unless a contract gap appears.
2. Challenge digests that claim "line boxes done" without slice E semantics.
3. Do not implement engine PRs headless.

### Pete (Friday)
1. Confirm: **north star = WPT Tier-1 trendline**, campaign = pinned Chrome t15.
2. Engine-future call still open (PLAN Friday): rustkit vs fastrender as capture
   engine; Windows re-unify vs permanent fork. This roadmap assumes **rustkit**
   remains the metric engine until that call.
3. Optional: create empty `trench/QUIRKS.md` template once first Chrome-deviant
   case is ledgered.

---

## 7. Explicit non-goals (until MVP surface is boring)

- 100% / 98% pixel parity as a goal number.
- Porting macOS `text.rs` wholesale onto Windows (engines diverged; semantics yes,
  file transplant no — Athena session 3 data).
- Expanding WPT to "as much as Chromium runs."
- Mid-word force-break to chase campaign pixels.
- New harness frameworks, agent orchestrators, or second parity taxonomies.
- Sticky-scroll deep dig as main lane.

---

## 8. One-screen summary

> **Ship readable real pages.** That means wrap → cascade → paint → simple flex,
> measured nightly against pinned Chrome and weekly against a **small, deliberate
> WPT Tier-1** set. Call slice-1 wrap what it is. Build real line boxes only when
> mixed inlines need them. Refuse Chrome-bug matching. Everything else is
> after the audience can read an article without a horizontal scroll of shame.

---

## Provenance

- PLAN.md dual metrics + line-box greenlight (Pete 2026-07-09)
- macOS digests sessions 7–11 (wrap zero-callers; #22 strut; flex-item height)
- Windows baselines + Athena #6/#7/#8 cascade/glyphs/greedy-wrap
- Prometheus exchange design ack on #8 (slices A–E, 2026-07-10)
- Mirror session: HiWave is the dream; bots/tooling are means

**Next step after this doc:** Atlas implements macOS slice 0 *or* either seat
lands Phase 0.5 Tier-1 WPT runner (≤200 tests, one manifest, Friday %). Prometheus
reviews propose output; does not merge.
