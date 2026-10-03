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
