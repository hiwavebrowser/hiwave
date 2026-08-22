# HiWave Trench Campaign — Plan of Record
Started 2026-07-07. Owners: Atlas (macOS seat), Athena (Windows seat). Authorized by Pete.

## Why this exists
HiWave stalled at the berserker→trench transition (mirror session, 2026-07-07). This campaign makes trench motion visible without Pete driving it: agents grind nightly, Pete reads a noon digest, Fridays converge.

## Metrics
- **Campaign metric (per seat, pinned in BASELINE-<os>.md):** pixel-parity vs **Chrome 148.0.7778.216 (pinned, frozen for the campaign)**. Re-pin only at campaign boundaries, deliberately, both seats in lockstep.
- **North star (Friday trendline):** WPT (Web Platform Tests) pass-rate — absolute conformance, not defined in terms of Chrome. Stand up in Phase 0.5.
- **Line-box / WPT strategy (Prometheus, 2026-07-10):** `trench/LINE_BOX_WPT_ROADMAP.md` — which WPT Tier-1 slices fund "replace Chrome", the Chrome-parity trap, and the honest line-box slice ladder (0→E). Campaign metric stays pinned-Chrome t15; Friday also plots Tier-1 WPT %.
- **Thresholds (Pete-locked 2026-07-08): t15 stays.** No re-tiering after the re-pin — pass means pass, grind the rest.
- **CI audits:** seats may trigger CI runs as needed (Pete, 2026-07-08) — first audit: settings 100%-vs-30.8% CI/local discrepancy.
- **Quirks ledger (`trench/QUIRKS.md`):** diffs traced to Chrome deviating from spec get recorded and dropped, not chased. Match the spec, not the bug.

## Phases
- **Phase 0 — Revive the instruments (night 1).** No renderer code until the harness is green.
  - macOS: parity_oracle npm deps; fresh pinned-Chrome baseline; classify run; rebuild .aleph with vendor masking (42% of fastrender syms are vendor — mask before agents navigate).
  - Windows: build parity-capture; same pinned baseline; build .aleph index + same mask.
  - Exit: `BASELINE-<os>.md` with current overall parity % and per-bucket shares. Jan's "59% text" is re-verified, not inherited.
- **Phase 0.5 — WPT runner** (either seat, whoever exits Phase 0 first): minimal WPT run against HiWave; record pass-rate; add to Friday trendline.
  - **GATE OPEN 2026-07-15** (Prometheus): dig preconditions met (wrap production, IFC A–C, gallery closed). Scaffold still stub (rustkit-test reftest = HTML strcmp). Implement stack W0a→W0b→W0c: `trench/forensics/2026-07-15-wpt-phase05-GATE-OPEN.md`. Execute after #53+atomic preferred; W0a anytime.
- **Phase 1 — Decompose (day 2).** Identical bucket formulas + thresholds on both OSes (text metrics / gradients / layout / compositing). Ranked defect ledger on the exchange. Each seat pins ONE metric from its own data.
- **Phase 2 — Nightly trench (day 3+).** One capped ~2h agent session per seat per night. Branches `atlas/trench-<metric>`, `athena/trench-<metric>`. Test-passing commits, never force-pushed. Digest appended to `trench/digest-<os>.md`, posted to the exchange, doorbelled at noon. Silence between digests.
- **Phase 3 — Friday convergence.** Trendline review, portable-fix merges, metric health. 7 days without movement → new angle or a written funeral note. No zombie loops.

## Direction update (Pete, 2026-07-09)
- **macOS seat leads.** macOS is furthest along; Windows work is deferred until macOS lands more major improvement. Athena's lane: no new tasking from this seat for now. Major discoveries still get posted to the exchange so Windows never re-derives them.
- **Goal restated:** make RustKit's rendering of REAL websites converge on Chrome's. That names the line-box/text-wrap gap (session 9: `TextShaper::wrap_text` has zero callers; text never wraps) as the campaign's main lane — real pages are text-dominated, so nothing else moves the needle like wrapping. Line-box lane is greenlit as multi-session work.
- **Smoke runner is honest now** (hiwave-macos `6460a42`): `visual_test_runner.sh` pixel-diffs every case against the pinned Chrome baselines with the same sensor + thresholds as parity_test.py. It was liveness-only ("13/13" while pages rendered wrong) — measurement lie #6, found by Pete's eyes. Honest baseline: **7/13**.

## Path forward (ADOPTED 2026-07-10 — Prometheus's PATH_FORWARD.md, Atlas-reviewed, Pete-directed)
- **Atlas epic: scroll/sticky/overflow** (3-5 days, milestones nightly; overflow/clip FIRST since parity baselines are unscrolled first frames, sticky math second). Parser-SSO chore PRs interleaved (one delete per two feature PRs). Then IFC quality.
- **Athena epic: paint stack** (images → backgrounds/gradients) after W1 honest re-measure + W2 positioned-semantics port + W3 CI PRs. 
- One multi-day epic per seat at a time; merge trains on Windows; portable notes on every epic PR; same metric formula both seats.
- Full doc: trench/PATH_FORWARD.md. Decision board 1/2/4: YES per Pete via Atlas review; item 3 (shared IFC quality) queued for Friday.
- **Day-1 exit met early (2026-07-10):** sticky-scroll 48.10 → 18.93 PASS (PR #25, grid Phase-9 subtree translation); committed 22/26 (84.6%), avg 10.3 — PATH_FORWARD §8 seven-day bar hit on day one.

## Viewport/resolution plan (ADOPTED 2026-07-10 — Prometheus's VIEWPORT_RESOLUTION_PLAN.md, Atlas-reviewed)
- **R0 (instrument integrity) SHIPPED on macOS (PR #28, 2026-07-10):** hard-fail dimension mismatch, `cases/registry.json`, baseline-audit CI, chrome-120 purge. Suite held 22/26 avg 9.3.
- **R1 (fixed containing block = viewport) SHIPPED on macOS (PR #29):** empirical triage killed stale vh/vw and renderer-default claims; live bug was Fixed CB = flow block. vh/vw already correct.
- **Windows R0 port (Athena):** unblocked. Contracts brief: `trench/forensics/2026-07-10-r0-windows-port-BRIEF.md` (Prometheus) — hard-fail first, then fork-local registry (same schema; keep `chrome.html` path; label subset digests), then audit script. Not a blind file port.
- **Tiers 2–5 still gated** until Windows R0 contracts are green on that seat (expanding multi-viewport before hard-fail multiplies lie #8).

## IFC quality (Bet #2) — greenlight status (2026-07-10)
- Prometheus's IFC_PHASE3_SKETCH.md reviewed: slices A (kill leaf self-align) / B (symmetric inline join) / C (baseline subset) are the right decomposition; his own gate (sticky plateau) is now essentially met.
- **Slice A greenlit for Friday** as the shared-epic kickoff (PATH_FORWARD decision board item 3): one-night PR, parent-only text-align + mixed-run fixtures. B/B2/C follow only after A's layout.json probe is green.

## Write policy (Pete-locked, 2026-07-07)
- Platform-specific code: free-fire on your own OS.
- Shared crates (fastrender core, rustkit-*): PR + **other-seat review**, and on approval the reviewing seat **auto-merges** (Pete, 2026-07-08: "go ahead and auto-merge shared-crate fixes"). Atlas reviews Athena's, Athena reviews Atlas's.
- Every digest flags portable fixes. Each night begins by porting the other seat's proven wins before hunting new bugs. The same glyph bug is never solved twice.
- **Review latency rule (adopted 2026-07-08):** a cross-seat PR un-reviewed after 2 nights gets escalated in the noon digest to Pete; after 3 nights Pete may merge it himself or waive review for that PR. Review is a lane, not a parking lot.

## Effort + tooling rules
- Nightly cap: one ~2h agent session per seat. Sustainable beats heroic; this is the trench.
- Aleph: vendor masking is the only sanctioned tooling addition. No new infrastructure layers — the campaign metric is parity, not shovel quality.

## Friday convergence agenda (accumulating)
- **TWO ENGINES, ONE NAME (Athena, 2026-07-08):** the Windows capture path has NO CSS engine — hardcoded per-tag UA defaults + inline styles (2 properties), no selector matching, no cascade, no line-breaking; rustkit-css's documented cascade was never implemented. The Windows parity ledger measured resemblance to unstyled HTML. macOS's cascade is REAL (receipt: settings moved 30.8→17.9 on a rustkit-layout patch — pixels respond to layout code). "Re-unify vs fork" is now "the Windows engine needs the macOS engine's cascade or a from-scratch minimal one" — Athena is building minimal cascade (selector match, specificity, application) as her session 3.
- **rustkit-layout has structurally diverged between seats** (found 2026-07-08 via PR #3 review): Windows' flex `apply_positions` returns without laying out item subtrees — macOS's step-11 fix cannot port verbatim. Decide: re-unify the crate (one source of truth, per-platform backends) or formally fork with a divergence ledger. Athena is porting the step-11 semantics by hand as a bridge (PR to Atlas for review).
- PR #4 ledger note: strict §10.3.3 drives margin-right negative in the over-constrained LTR case — paint-identical today; revisit only if overflow-width ever reads it.


- **DIVERGENCE HAS A NUMBER (Athena session 3, 2026-07-08):** salvage falsified with data. rustkit-CSS ports wholesale (91KB superset compiles on Windows — banked). But the ENGINE cascade transplant = 245 errors in engine + ripple into renderer/compositor/net/bindings: the macOS engine drags box types (FormControl/Image), DOM methods, animation plumbing the Windows fork lacks. VERDICT: file-level reuse between the two engines is NOT viable below the whole-crate-set level. Friday choice is concrete — adopt the macOS crate-set wholesale on Windows, OR accept the fork. Athena chose a native minimal cascade (~300 lines) for session 4 to unblock Windows parity NOW; the strategic re-unify call is Pete's.
- **TWO ENGINES ON macOS TOO (session 4, 2026-07-08):** parity renders via `crates/rustkit-*`; the repo also carries `fastrender/` — larger, more sophisticated (real font-metric line-heights, full cascade w/ style-sharing), and it is what January's work (and the ~98.7% claims) built. Aleph currently indexes fastrender and steers sessions to the wrong engine. TACTICAL (done): sessions target rustkit (the metric engine); Aleph re-scoped. STRATEGIC (Pete, Friday): which engine is HiWave's future — grind rustkit to parity, or make fastrender the capture engine and re-baseline? This may be the single biggest resource-allocation decision of the campaign.

## Direction update (Atlas, 2026-08-22 evening — Pete greenlight executed, post-landing retarget)
- **The board landed today.** E0 lane #147→#148→#149 merged to `master` in the Prometheus
  land order. #150 (soft-wrap slice-0) retargeted and merged to `develop` per the standing
  ruling, with the banked docs lane (#151). n27 decision 1 and n29 decision 1's #150 half
  are closed. NOTE for the seat: n29's "nothing merged all week" reading predates this.
- **Trunk answer (interim, Atlas manager call): `develop` is the measurement tree.**
  @font-face (#124–#133) + slice-0 + docs all live on develop; measuring master kept the
  Tier-1 board's `blocked_by: @font-face` attribution pointed at the wrong tree — n29's
  finding (overflow-wrap-001/002 "blocked" yet flipped by slice-0 alone) confirms the
  over-claim. Until develop→master promotion (external-R1 ceremony, queued on the
  exchange), nightly boards measure **develop tip**.
- **Tonight's scope, in order (cap ~3h):**
  1. Fresh parity-capture on develop tip; re-run Tier-1 + campaign boards; commit the new
     develop basis to BASELINE-macos.md. Re-attribute every remaining fail honestly.
  2. Then the named engine lane: the #150 ink residual (glyph ink ~2–3px right of correct
     boxes on lba001/002, paint-side advance under the new breaker — n29 localized it,
     forensics 2026-08-22-abspos-overlay-two-bugs-one-pattern.md). It now lives on develop;
     one contained fix + line-count + ink assertions. PR to develop, review lane.
  3. #152 (abspos margin-collapse + paint-order fixes) is retargeted to develop and queued
     for cross-seat R1 — do not merge it from the trench seat.
- Carried ask (n17→n29) on allowlisting `git worktree`/`gh pr merge`/`null_exchange`:
  still with Pete, re-flagged. MCP-unreachable (n28/n29): likely the fastembed cache
  corruption fixed 2026-08-22 14:04 — tonight's session is the verdict; escalate if it
  recurs.
