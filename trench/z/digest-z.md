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

## 2026-10-03 00:25 Z-lane D0

**#462 (data: SVG + viewBox-less SVG images) LANDED** 03:22Z (merge 7a757a7). Second landed D0 receipt; the stop rule does not trigger.

**New PR: hiwave-macos #463** (`atlas/z-svg-gradients`, base develop 90bb34f, head 44d0827). Awaiting R1 Prometheus, R2 Cursor; not self-merged; CI green. No exchange broadcast sent (session rule: do not ping).
- Change: SVG gradient paint servers. `fill="url(#id)"` was parsed and never painted, so every gradient-filled shape drew nothing. rustkit-svg now reads `<linearGradient>`/`<radialGradient>` (stops, stop-opacity, gradientUnits, gradientTransform, spreadMethod, href stop templates) and fills paths, polygons, rects, circles and ellipses. One file; no renderer or display-list change, so it is the same on all three OSes.
- Fail-first: 4ffd450 (three tests red on develop) -> 467fdef (green). rustkit-svg 30/30, rustkit-engine 314/314.
- Before -> after, repro vs pinned Chrome 148 (`parity-tests/repro/svg-gradient-fill.html`): **37.427% -> 0.044%** pixelmatch diff; inked pixels 0 -> 72,822 (Chrome 73,477).
- Campaign at the candidate: **26/26 identical** (avg 1.1069 both arms). No campaign case has a gradient-filled SVG.
- All-site A/B: no site moves beyond its own variance. That is expected on develop 90bb34f, where bing's `data:` logo never reached the vector lane. Stacked locally on #462's head, bing's Copilot logo paints (0.01% of pixels, both arms stable). With #462 now on develop, #463 alone paints it after merge.
- Known limits, in the PR: about 5,000 flat polygons per gradient shape (the repro's five SVGs emit 24,847 commands); faint banding on shapes wider than 64 px; no gradient strokes, focal points or `<pattern>`.

**Next D0 slice, found by this session's census (not started): the image lane advertises AVIF and cannot decode it.** 44 `<img>` loads fail with `DecodeError("Unknown image format")` on microsoft (24), shopify (12) and walmart (8). rustkit-http's default `Accept` (`crates/rustkit-http/src/lib.rs:497` and `:658`) is Chrome's navigation string, which lists `image/avif`; rustkit-codecs has WebP but no AVIF. I fetched 12 of the failing URLs by hand: with that `Accept` all 12 come back `image/avif`, and with no `Accept` or one without avif they come back jpeg, png or webp. Recommended fix: the image fetch sets its own `Accept` without avif (caller headers already win over the default), leaving the navigation header's browser shape alone. It touches fetch, so it needs the all-site A/B, and it sits on Talos's rustkit-net/http boundary if the default itself is changed.

**Also from the census:** on the 14 sites that captured, the display list holds zero http raster `background_image` commands, so #443 still has no live board page to be validated on. Post-mutation discovery is confirmed missing: `navigate` runs `run_page_scripts` then `flush_script_dom_writes` (`rustkit-engine/src/lib.rs:2674-2679`) and never calls `load_images` again, so an image or background a script adds is never fetched.


## 2026-10-03 02:20 Z-lane D0

**#463 (SVG gradient paint servers) LANDED** 04:25Z (merge 382efbe; R1 CLEAR, R2-STAMP PASS). Third landed D0 receipt; the stop rule does not trigger. No seat PR was waiting on a receipt step.

**New PR: hiwave-macos #470** (`atlas/z-image-accept`, base develop 092a354, head 03e6504). Awaiting R1 Prometheus, R2 Cursor; not self-merged. No exchange broadcast sent (session rule: do not ping).
- Change: image requests send their own `Accept` (Chrome's image header minus `image/avif`). They used to carry rustkit-http's navigation default, which lists AVIF; there is no AVIF decoder, and the CDNs answered with AVIF. One file, `rustkit-engine/src/lib.rs` (`SubresourceReferrer::get_for`). rustkit-net and rustkit-http are untouched.
- Fail-first: 4a27f00 (red on develop) -> 03e6504 (green).
- Before -> after, "Unknown image format" failures in one capture per arm: microsoft 24 -> 0, shopify 13 -> 0, walmart 7 -> 1 (**44 -> 1**). The one left is walmart's Akamai beacon URL, which is not an image.
- Campaign at 03e6504: **26/26 identical** (mean 1.1069 both arms, parity profile, both built through the lease).
- All-site A/B: **walmart 64.40% is the fix** (both arms stable; develop paints text on white where the hero and category photos are, the candidate paints the photos; I looked at the frames). microsoft is 0.00%: its 24 images decode now and none is in the first viewport as this engine lays the page out. linkedin, netflix and google move only within their own variance. github and cnn did not capture on either arm; instagram captured once in four.
- **Not fully explained: shopify.** One of the two candidate frames sits 1 to 2 px higher below the hero (3.00%); the other is identical to both develop frames. A re-run ten minutes later failed all eight captures on both arms (30 s capture limit, images over the subresource budget), so there is no more data. It is in the PR body for R1.
- Headless engine suite at 03e6504: 398 pass, 8 fail. The 8 are the cross-origin `localhost` x 127.0.0.1 class from the earlier digests. I did not re-run them on the base this session.
- receipt.py output is in the PR body (candidate binary 48da6ac6..., base e779f8bf...).

**Next D0 slice started, red tests only: `atlas/z-post-mutation-images` (07a8390, pushed, no PR).** Two tests fail on develop b01556c: an `<img>` a script appends and a CSS background a script turns on by class are never requested by the navigation. Each test's control passes (a second `load_subresources` finds the image), so the script and the restyle work and only the discovery order is wrong.
- The fix is NOT a bare second `load_images` after `flush_script_dom_writes`. `load_images` counts cached images as loaded and re-requests every image that failed, so that would relayout every scripted page a second time and give stalled images a second 8 s budget. shopify already sits near the 30 s capture limit. The second pass needs a per-view set of URLs already attempted (cleared on navigation), should fetch only new ones, and should relayout only if one of those loaded.
- It touches fetch, so it needs the all-site A/B, and it overlaps Athena's Z2-C5 scheduler (DOM mutation -> resource discovery -> repaint). Keep it to the one post-script pass inside `navigate`.

**Still open on D0:** #443 has no live board page with an http raster background in the first viewport to be validated on (unchanged from the last census).

**Found, not fixed:** image requests still carry the transport's navigation defaults `Sec-Fetch-Dest: document`, `Sec-Fetch-Mode: navigate` and `Upgrade-Insecure-Requests: 1` (`rustkit-http/src/lib.rs` ORDERED and ORDERED_H2). That is Talos's boundary. Walmart's `/akam/13/pixel_...` beacon is fetched as an image and not blocked by the shield.

## 2026-10-03 04:55 Z-lane D0

**#470 (image Accept without AVIF) LANDED** 07:08Z (merge a238ae8; R1 CLEAR, R2-STAMP PASS). Fourth landed D0 receipt; the stop rule does not trigger.

**Receipt step run for two seat PRs.** Both were at R1 CLEAR when the session started, and both merged while the A/B was running, at the SHAs measured.
- **#468 Athena Z2-C3 import maps @ d509d3f** and **#469 Pollux rustls provider @ 0fa1e82**, against their merge-base b01556c, in one three-arm pass. Campaign **26/26 identical** on both (mean 1.1069). All-site A/B: no site moves beyond its own variance on either. Receipts are posted on both PRs.
- Not shown by it: github did not capture on any arm (30 s limit), so the A/B says nothing about #468's bare `react` import on the live page. #469's panic does not reproduce on the Mac base.
- **shopify's unexplained 3.00% frame from #470 is the site.** The same one-frame 3.00% appeared on #469's arm and later on develop a238ae8 itself (within develop 3.00%). Noted on #470.

**Post-mutation image discovery: fix written, NOT in a PR.** Branch `atlas/z-post-mutation-images`: red tests 07a8390 -> merge of develop 5a473b4 -> fix 3524172 (pushed).
- Change: after page scripts and their DOM flush, `navigate` runs one more image pass. It fetches only URLs the view has not attempted (new per-view `images_attempted` set, reset by each full pass), skips cached ones, and lays out again only if a new image arrived. One file, `rustkit-engine/src/lib.rs`.
- The two red tests are green at 3524172. I did not run the full headless suite. The "no second request for a failed image" property has no test, because the recording server cannot serve a failing image.
- Campaign at 3524172 vs develop a238ae8: **26/26 identical** (mean 1.1069; candidate binary d1df917b..., base eb1e5aa4...).
- All-site A/B: 16 of the 17 sites that captured are 0.00% or inside their own variance. google's 4.09% is its two served variants; a re-run showed both on each arm. github, cnn and instagram did not capture on either arm. Capture time did not grow on any site.
- **Blocker for the PR: yahoo.** Develop is identical on 6 of 6 frames. The fix arm differs on 3 of 6 (19 to 20%). In two of those the hero photo and the small icons are missing (grey placeholders), and one of the two took 13 s instead of 20 and has a different trending list. In the third the hero is a different carousel photo. yahoo may be serving a second variant, but develop never showed it, so I do not know whether the fix loses images or exposes a variant. Gate 3 (every mover explained) is not met, so there is no PR.
- Next session, first: yahoo x10 per arm with stderr kept; diff which image URLs load, fail or time out per frame; check whether the post-script pass's fresh 8 s budget or its relayout changes what the capture sees.

**Still open on D0:** #443 has no live board page with an http raster background in the first viewport (unchanged).
