# HiWave Trench Campaign — Plan of Record
Started 2026-07-07. Owners: Atlas (macOS seat), Athena (Windows seat). Authorized by Pete.

## Why this exists
HiWave stalled at the berserker→trench transition (mirror session, 2026-07-07). This campaign makes trench motion visible without Pete driving it: agents grind nightly, Pete reads a noon digest, Fridays converge.

## Metrics
- **Campaign metric (per seat, pinned in BASELINE-<os>.md):** pixel-parity vs **Chrome 148.0.7778.216 (pinned, frozen for the campaign)**. Re-pin only at campaign boundaries, deliberately, both seats in lockstep.
- **North star (Friday trendline):** WPT (Web Platform Tests) pass-rate — absolute conformance, not defined in terms of Chrome. Stand up in Phase 0.5.
- **Thresholds (Pete-locked 2026-07-08): t15 stays.** No re-tiering after the re-pin — pass means pass, grind the rest.
- **CI audits:** seats may trigger CI runs as needed (Pete, 2026-07-08) — first audit: settings 100%-vs-30.8% CI/local discrepancy.
- **Quirks ledger (`trench/QUIRKS.md`):** diffs traced to Chrome deviating from spec get recorded and dropped, not chased. Match the spec, not the bug.

## Phases
- **Phase 0 — Revive the instruments (night 1).** No renderer code until the harness is green.
  - macOS: parity_oracle npm deps; fresh pinned-Chrome baseline; classify run; rebuild .aleph with vendor masking (42% of fastrender syms are vendor — mask before agents navigate).
  - Windows: build parity-capture; same pinned baseline; build .aleph index + same mask.
  - Exit: `BASELINE-<os>.md` with current overall parity % and per-bucket shares. Jan's "59% text" is re-verified, not inherited.
- **Phase 0.5 — WPT runner** (either seat, whoever exits Phase 0 first): minimal WPT run against HiWave; record pass-rate; add to Friday trendline.
- **Phase 1 — Decompose (day 2).** Identical bucket formulas + thresholds on both OSes (text metrics / gradients / layout / compositing). Ranked defect ledger on the exchange. Each seat pins ONE metric from its own data.
- **Phase 2 — Nightly trench (day 3+).** One capped ~2h agent session per seat per night. Branches `atlas/trench-<metric>`, `athena/trench-<metric>`. Test-passing commits, never force-pushed. Digest appended to `trench/digest-<os>.md`, posted to the exchange, doorbelled at noon. Silence between digests.
- **Phase 3 — Friday convergence.** Trendline review, portable-fix merges, metric health. 7 days without movement → new angle or a written funeral note. No zombie loops.

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
