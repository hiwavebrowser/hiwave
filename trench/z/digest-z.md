# Z phase digest

One section per lane session or seat milestone: `## <date> <HH:MM> <owner> <package>` — before -> after, PRs with SHAs, blockers, decision packets.

## 2026-10-02 20:48 Z-lane D0

**D0-SVG PR up: hiwave-macos #454** (`atlas/z-svg-background`, test ae1e5c5 fail-first -> fix dc616df, base develop d77ad20). Awaiting R1 Prometheus, R2 Cursor; not self-merged. No exchange broadcast sent (session rule: do not ping), so reviewers pick it up from this digest and the PR.
- Change: `discover_background_images` drops the `.svg` skip; the display-list splice paints a cached-SVG `BackgroundImage` as `PushClip` + the document once per tile + `PopClip`; tile placement moved from the renderer into the shared `rustkit_layout::background_tiles` (raster lane unchanged).
- Before -> after: campaign 26/26 **identical** (avg 1.1069 both arms, parity profile, both built through the lease). wikipedia's display list: 99 unpainted http SVG `background_image` commands -> 0 (all spliced to vectors). None of them is in any board site's first viewport, so the board does not move. All-site A/B: every cross-arm mover is that site's own variance; netflix 12.75% is different headline copy served (I checked the frames); github/cnn/squarespace did not capture in 30 s on either arm.
- receipt.py output is in the PR body (candidate binary 83e1f843..., base e9c58841...).
- **Pre-existing, for Talos:** 9 headless `rustkit-engine` tests fail identically on develop d77ad20, including #443's own `a_css_background_image_is_fetched`. All of them make cross-origin `localhost` requests from a 127.0.0.1 page, likely the #445 per-hop private-address vet. PR CI does not run the headless feature, so nothing flagged them.
- D0 still open: (1) `data:image/svg+xml` backgrounds (bing's one background command) are neither discovered nor decoded; (2) post-mutation discovery + paint; (3) validate #443 on a page with a raster background in the first viewport. D1 starts after #454 lands.
- Stop rule: session 1 on D0, no landed receipt yet (PR open).

## 2026-10-02 23:00 Z-lane D0

**#454 (D0-SVG) LANDED** 01:02Z (merge 002b80d; R1 CLEAR + gate-5 re-run by Prometheus, R2-STAMP PASS). That is D0's first landed receipt, so the stop rule does not trigger. **D1 is now unblocked** (it waited on the SVG PR).

**New PR: hiwave-macos #462** (`atlas/z-data-svg-background`, base develop 30b034a, head 5baee6a). Awaiting R1 Prometheus, R2 Cursor; not self-merged.
- data: SVG: `data:image/svg+xml` backgrounds and `<img>`s went to rustkit-image's stand-in rasterizer, which draws only `<rect>`s. The splice now decodes them into `svg_cache` and paints them as vectors on the first layout, with no fetch.
- Moving them to the vector lane exposed `render` drawing a viewBox-less SVG at its own size. images-intrinsic went 0.33 -> 5.85 at 2f47e74. Fix: SVG images get Blink's synthesized viewBox plus `preserveAspectRatio=none` (new `SvgDocument::stretch`). Inline `<svg>` is unchanged.
- Three fail-first tests, each committed before its fix (d32f004/2f47e74, 79f327d/fe1b830, 510246a/5baee6a).
- Campaign at 5baee6a: **26/26 identical** (avg 1.1069 both arms).
- All-site A/B: **walmart 3.98% is a fix**. Develop painted the spark logo ~500px across the hero; the candidate paints it at box size. linkedin's 41% was the server sending each arm a different page; with the arms swapped it was 0. Every other mover equals within-arm variance. cnn, github and squarespace did not capture on either arm.
- Next D0 blocker: bing's logo now reaches the vector lane but still paints nothing, because rustkit-svg has no gradient paint servers (`fill="url(#a)"` is parsed and never rendered). After that: post-mutation discovery.
- Headless engine suite: 395 pass, 8 fail, all in the pre-existing localhost x 127.0.0.1 class flagged for Talos last session.

