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

## 2026-10-03 07:55 Z-lane D0

No seat PR was waiting on a receipt step (no open PRs on hiwave-macos at 07:05).

**New PR: hiwave-macos #473** (`atlas/z-post-mutation-images`, head 3524172, receipts against develop a238ae8). Awaiting R1 Prometheus, R2 Cursor; not self-merged; CI was still running when the session closed. No exchange broadcast sent (session rule: do not ping). The code is the fix from the 04:55 entry, unchanged; this session answered the yahoo question that kept it out of a PR.

**Before -> after on the blocker: yahoo "unexplained" -> explained, on both arms.**
- The odd yahoo frame is the page with no scripts run. One script fetch passes the 5 s script budget, `navigate` then gives the scripts a zero budget, and the hero photo and header icons that yahoo's scripts move into place are missing. It is 13 to 16 s instead of about 20 because the scripts and their relayout are skipped.
- yahoo x13 per arm with logs: develop 13/13 identical, candidate 12/13. The odd candidate frame: 0 scripts ran, 53 over budget, web fonts took 6.6 s to fetch instead of 2.3 s.
- The fresh all-site A/B then caught it on develop too: A1 and B2 ran no scripts, B1 and A2 ran all 54 and are identical (0.00%).
- Last session's odd frames have no logs; they match by appearance only.

**All-site A/B, re-run with the engine log kept per frame** (`scratch/zd0/ab4.py`, raw table `ab-pm.txt`, in the PR body):
- The new pass requested no image on any of the 20 sites. No board frame changes because of #473; the two red-first tests are what pins it.
- linkedin's 40.97% is also scripts ran (5) against not ran (18 over budget), the same on both arms. This is what earlier digests called "the server sent each arm a different page".
- shopify's 3.00% has two frames, each once per arm (A1 = B2, A2 = B1). The script counts do not separate them. Still not explained, and still on both arms.
- github and cnn did not capture on either arm; instagram once in four; squarespace three in four.
- Campaign at 3524172 vs a238ae8: 26/26 identical (mean 1.1069), from the 04:55 session's run on the same two binaries.
- Headless engine suite at 3524172: 408 pass, 8 fail (the localhost x 127.0.0.1 class; not re-run on the base).

**Found, not fixed (not D0; for Atlas to place):** on live pages the 5 s script budget is all-or-nothing. One slow script fetch means zero scripts run, and that decides the frame on yahoo, linkedin and squarespace run to run. Per frame this session: youtube 0 of 42, walmart 0 of 88, microsoft 0 of 255 scripts ran on every capture; weather ran 150 once and 0 three times. Any all-site A/B should print scripts ran / over budget per frame (ab4.py does) before a mover is read as a paint change.

**Stop rule:** this session has no landed receipt (#473 is open). The session before landed #470. If #473 has not landed by the end of the next D0 session and nothing else lands, D0 goes to blocked.

**Left on D0 after #473:** #443 still has no live board page with an http raster background in the first viewport. D1 has been unblocked since #454.

## 2026-10-03 09:03 Z-lane D0

Same session as the 07:55 entry (07:05 to 09:05).

**#473 (post-mutation image discovery) LANDED** 12:03Z (merge 877fa55; R1 CLEAR). Fifth landed D0 receipt; the stop rule does not trigger.

**New PR: hiwave-macos #474** (`atlas/z-bg-size-position`, head 5cf8e38, base develop 877fa55). Awaiting R1 Prometheus, R2 Cursor; not self-merged. No exchange broadcast sent (session rule: do not ping). This is D0's "validate #443" item.
- How it was found: no board page has an http raster background in the first viewport, so I probed 12 other live pages. wordpress.org has one (`wcus_map.png`, `cover`), and it is fetched and painted. Then nine url() background cases over a local http server, RustKit against pinned Chrome: six matched, three did not.
- Wrong: `background-size` with a percentage (`50% auto`, `auto 100%`) painted nothing; `background-position` in px (`10px 20px`, the sprite-sheet case) painted at 0 0.
- Fix: rustkit-layout resolves the percentage where the command is emitted; `DisplayCommand::BackgroundImage` carries a px `offset` that the shared `background_tiles` adds. Engine and renderer pass it through.
- Fail-first, twice: c33638c red -> bd9a385 green; f86c288 red -> e2c42a1 green. rustkit-layout 604/604. Headless engine suite not run on this branch.
- Before -> after, repro vs pinned Chrome: **7.399% -> 0.166%** pixelmatch diff (ink px 316,136 -> 272,023; Chrome 272,228). Before is develop a238ae8, after is e2c42a1.
- Campaign at 5cf8e38 vs 877fa55: **26/26 identical** (mean 1.1069; candidate binary b93b0ff6..., base 71b84287...).
- All-site A/B: no site moves outside its own variance, so the board does not show the fix. google's 8.49% is one develop frame; linkedin's differences are all present between the two develop frames; shopify is its two frames again. github and cnn did not capture; instagram once in four; squarespace three in four.

**Found, not fixed (in the PR body):** a float after a block collapses its top margin with the block's bottom margin (row 10 px high; layout, D1 territory). wordpress.org's hero box is 680x741 where Chrome has a 1280x92 banner (layout). `images.rs` `render_background_image` is a second copy of the tile placement with no caller outside its tests. Edge-offset and `calc()` background positions are not parsed.

**Left on D0 after #474:** nothing listed. Finish line 2 (backgrounds on the live board at the right size and position) cannot be shown on the board until a board site has one in its first viewport. If #474 lands, D0 can go to done and the lane moves to D1.

**Tooling note:** the last A/B batch ran past the 10-minute tool limit and finished in the background; four sites per batch is the safe size when github and cnn each cost two minutes of timeouts.

## 2026-10-03 10:12 Z-lane D0

Session 09:05 to 10:15. No seat PR was waiting on a receipt step (the only open PR at 09:05 was #474).

**#474 (url-background percentage size + px position) LANDED** 13:15Z (merge b7addf2; R1 CLEAR). Sixth landed D0 receipt; the stop rule does not trigger.

**New PR: hiwave-macos #475** (`atlas/z-bg-position-edges`, head 9fca084, base develop b7addf2). R1 CLEAR at 14:04Z, CI green, Cursor reviewer check passed; not merged when the session closed, and not self-merged. No exchange broadcast sent (session rule: do not ping). It fixes the item #474 listed as found and not fixed.
- Wrong: `background-position: right 5px bottom 10px` painted as `right bottom` (the far-edge offset was dropped). A `calc()` position was split at its spaces and painted at 0 0; the `background` shorthand skipped it.
- Fix: a position value can be a percentage plus px (`BackgroundPositionValue::Calc`). The parser splits outside parentheses and turns a far-edge offset into `100% - offset`. Layout passes it as the `(position, offset)` pair from #474. The renderer is unchanged.
- Fail-first: ebff7b9 red -> 9fca084 green. rustkit-engine lib 320/320, rustkit-layout 605/605, rustkit-css 49/49. Headless engine suite 409 pass, 8 fail (the localhost x 127.0.0.1 class; not re-run on the base).
- Before -> after, nine-case repro vs pinned Chrome 148: **7.157% -> 0.525%** pixelmatch diff (ink px 411,743 -> 415,237; Chrome 416,956). Every image is where Chrome puts it. What is left is resampling at the edges of the down-scaled images and a one-pixel line on a tile row that starts at y = 367.5.
- Campaign at 9fca084 vs 5cf8e38 (the develop tree): **26/26 identical** (mean 1.1069; candidate binary 0699c051..., base b93b0ff6...).
- All-site A/B: no site changes because of the PR, so the board does not show the fix. 11 sites are 0.00% on every pair. github and cnn did not capture; facebook once in four; instagram three in four.
- Three movers looked like the fix and are the site. linkedin was 40.81% across with 0.00% within each arm, twice: the server has two landing pages and each arm got one on all four frames; a third run gave both arms the same page, 0.00%. netflix was 4.8% across against 2.1% within: its "Get Started" button was white on both develop frames and red on both candidate frames, and the develop binary alone then painted it white, then red, on two loads. bing's 0.24% is the header with or without "Copilot".
- receipt.py output is in the PR body.

**Not done (named in the PR):** background positions in em, rem or viewport units (the parser has no font size or viewport), and `calc()` in `background-size`. I did not look for a live page that uses either.

**D0 has no work left.** Every item in the package row has landed except #475, which only needs its merge. Finish line 2 still cannot be shown on the live board: no board site has a url background in its first viewport. Next session: if #475 has merged, set D0 done; start D1 (L0) either way. D1 has been unblocked since #454 and has had no session yet.

## 2026-10-03 13:10 Z-lane I0

Session 11:33 to 13:15. First session on I0. No seat PR was waiting on a receipt step (#476 is Pollux's Z2-I1, not a C0/C1/C2 seat PR).

**D0 closed.** #475 merged 14:16Z (1585ad1). D0 set to done.

**New PR: hiwave-macos #480** (`atlas/z-live-click`, head 732c9a0, base develop 1585ad1). I0 part (a). Awaiting R1 Prometheus, R2 Cursor; not self-merged. No exchange broadcast sent (session rule: do not ping).
- Before: a click in the live browser hit-tested for focus and a link and never told the page. No mousedown, mouseup or click reached a listener. A link whose listener cancels the click navigated anyway.
- After: the engine fires mousedown on press, mouseup and click on release, through the page's own listener registry. It lays out what the listeners wrote, then focuses and follows the link unless the click was cancelled. The shell calls it.
- Second fault found on the way: a click on a block link's line box hit a layout box with no DOM node, so it reached no element. `hit_test` now reports the nearest ancestor's node for such a box. This reverses an earlier comment in the tests; flagged for R1 in the PR.
- Fail-first: e793237 red (0 of 3) -> 732c9a0 green (4 new tests). One test changed between the two commits: it built a link with `a.href = ...`, which our bindings do not reflect to the attribute.
- rustkit-engine headless lib 413 pass, 8 fail (the localhost x 127.0.0.1 class; not re-run on the base). rustkit-layout 605/605, rustkit-bindings 150/150. hiwave-app type-checks.
- Campaign at 732c9a0 vs 1585ad1: **26/26 identical** (mean 1.1069; candidate binary 344b2817..., base 0699c051...).
- All-site A/B: 12 sites 0.00% on every pair. google, linkedin and netflix moved and are the site: google has the same two frames on both arms; linkedin moves 3.43% within the candidate arm on a re-run; netflix moves 3.45% to 12.83% with the develop binary on both arms. facebook, github, squarespace and cnn did not capture on either arm; instagram once per arm.
- receipt.py output is in the PR body.

**Not verified: the real window.** Nobody has clicked in the built app at this SHA. The engine half is tested headless; the shell half only compiles. One click on a script-driven control in the live app is the acceptance check (Pete or Prometheus). The red test is engine-level, not an action-script test, because Z2-I1 (#476) has not landed.

**I0 is not closed. Left:**
- (c) late content: cause confirmed, not fixed. `RustKitView::process_events()` in hiwave-app is an empty function. Nothing on the live loop runs timers, promise jobs or network callbacks after load. A `setTimeout` set by a click listener never fires either. This is the next PR.
- (b) plain link clicks failing and the inverse resize scale: not looked at. The line-box fix does not explain it, because the link lookup already inherited from ancestors.
- Found, not fixed: `a.href = '...'` does not set the attribute. Inline `onclick="..."` handlers not checked. Focus moves on release, not press. Modifier keys are always false in the event.

**Stop rule:** this session has no landed receipt (#480 is open). If #480 has not landed by the end of the next I0 session and nothing else lands, I0 goes to blocked.

**Tooling:** worktree `z-i0` (no Aleph index, same as z-d0). The first `cargo check -p hiwave-app` there took 8 min 39 s. Campaign and A/B still run from `z-d0/scratch/zd0` (camp.py, ab4.py); raw A/B table `ab-click.txt`.

**Lead for (b), read only, NOT verified (13:15):** the shell sizes the content view in logical points (`wry_set_bounds`), the engine lays out and sizes the wgpu surface at that same number (`resize_view` -> `resize_surface`), and the viewhost only calls `setFrame:` on the NSView. The CAMetalLayer is created and owned by wgpu (`macos.rs:280`, "let wgpu manage it"). If that layer's frame does not follow the view on resize, a wider surface is squeezed into the old layer: bigger window, smaller page, and clicks land in the wrong place. That would be one cause for both of Pete's reports. First check next session: log the layer's frame and `drawableSize` against the view frame before and after one resize. Nothing was run to test this.

## 2026-10-03 15:52 Z-lane I0

Session 14:53 to 15:52. Second session on I0.

**#480 (live click dispatch) LANDED** 17:35Z (merge 71de6bc; R1 CLEAR, R2 PASS). The stop rule does not trigger.

**Receipt step done for cloud pilot PRs #481 + #483** (both R1 CLEAR, R2 PASS, CI green, held for this). One combined arm (local merge 5eaf1fc2, not pushed) against develop 387ccf88, all 20 sites. Posted on both PRs.
- No site's frame changes because of the two PRs. 15 of 20 sites are 0.00% on every pair. All 20 captured on both arms, github and cnn included (first time today).
- One real change, in the script log: on linkedin the 510 KB main bundle stops throwing `require is not defined` and a timer gets past `crypto.getRandomValues() not supported`. Scripts that ran clean: 5 on develop, 6 with the PRs, on every frame. `crypto.getRandomValues` is #483's.
- The two PRs conflict with each other in `rustkit-bindings/src/lib.rs` (a `mod` line each at the same place). Keep both lines. Whichever lands second needs that.
- #481 landed during the session (767c602b). #483 was still open when the session closed. Nothing more is owed on either from the lane.

**New PR: hiwave-macos #486** (`atlas/z-live-pump`, head 35f29d3e, base develop 387ccf88). I0 part (c). R1 CLEAR at 35f29d3e (19:29Z), CI green and CLEAN; no R2 stamp when the session closed. Not self-merged. No exchange broadcast sent (session rule: do not ping).
- Before: after the load nothing ran a page's timers or sent its fetches. `process_events()` in hiwave-app was empty and the loop slept until input.
- After: `Engine::pump_live` runs one turn (timers on real elapsed time, the page's requests through its own FetchPolicy, one layout, new images) and says when the next timer is due. The shell runs it each loop pass and wakes for the next timer.
- Fail-first: a2d35cd2 red (0 of 4) -> b11f9042 green (4 of 4, plus one bindings test). 35f29d3e is the shell wiring.
- rustkit-engine headless lib 420 pass, 5 fail; the same 5 fail on develop 387ccf88 (run this session). rustkit-bindings 151/151. hiwave-app type-checks.
- Campaign at 35f29d3e vs 387ccf88: **26/26 identical** (mean 1.1069).
- All-site A/B: no site moves because of the change; 15 of 20 are 0.00% on every pair, all 20 captured. google was 4.09% across with 0.00% inside each arm on the first pass; three re-runs each gave a candidate frame identical to a develop frame.
- receipt.py output is in the PR body.

**New PR: hiwave-macos #487** (`atlas/z-view-resize`, head 2a28f8cf, base develop 387ccf88). I0 part (b), the inverse resize scale. R1 CLEAR at 2a28f8cf (19:40Z), CI green and CLEAN; no R2 stamp when the session closed. Not self-merged.
- Cause, measured: `ViewHost::set_bounds` (the one the engine calls) had only a Windows arm. On macOS the NSView never changed size. The engine resized its drawable and laid out at the new size, and the drawable was stretched into the old view.
- A probe with a real, never-shown NSWindow: on develop the view stays 1280x720 and the page scale is 0.800 at 1600x920 and 1.600 at 800x420. With the fix it is 1.000 at every size.
- The 13:10 lead (wgpu's Metal layer not following the view) was wrong. wgpu follows the view; the view was not moving.
- Fail-first: d85be3d7 red (frame stays 1280x720) -> 2a28f8cf green. The test makes a real NSWindow and runs without the test harness.
- Campaign at 2a28f8cf vs 387ccf88: **26/26 identical** (mean 1.1069). No all-site A/B: the change is window geometry, and parity-capture's headless views never reach it.
- CI compiles the new test and does not run it (f1-test-compile builds every test target; unit-suites runs --lib only). It ran on this Mac only.

**Not verified: the real window, for all three parts.** Nobody has clicked, waited or resized in the built app at these SHAs. The engine and viewhost halves are tested; the tao loop wake-up in #486 is type-checked only. Acceptance checks for Pete or Prometheus are named in each PR body.

**I0 is not closed. Left:**
- Plain link clicks failing (the other half of b): #487 should explain it (a view that keeps its old frame is hit-tested at the wrong scale, and it also does not move when the sidebar or shelf change the content rectangle), but no click was tested in the window.
- How real sites feel with their timers running (#486): intervals, animation loops and polling now run on the UI thread, with a full relayout per DOM-writing turn and up to 2 s blocked per fetching turn. Not measured on any site.
- Found, not fixed: `ViewHost::set_visible` has the same Windows-only gap; `MacOSViewHost` in macos.rs is a dead copy of the view host; the shell discards every `set_bounds` result; on a 2x display the drawable is sized in points (half resolution, stretched), not checked on Retina; `a.href = ...` does not reflect; inline `onclick` not checked.

**For Atlas (F0), found this session: the shared Z target dir can build a wrong binary with no error.** `z-cargo.py` gives every Z worktree one `CARGO_TARGET_DIR`. Cargo gives a workspace crate the same unit hash in every worktree and judges freshness by file time, so a build in one worktree reuses a crate compiled from another worktree's sources when its own files are older.
- It broke a build here: the engine in z-i0 linked the bindings compiled from z-d0.
- I rebuilt every measured arm after touching all crate sources. The #486 candidate is byte-identical. The develop base and the cloud arm differ only in three embedded path strings plus UUID and signature (three crates had been compiled in the other worktree from identical sources). No result changes; notes are on #481, #483 and #486.
- Earlier Z receipts from today were not re-checked.
- Fix to consider: one target dir per worktree in z-cargo.py (sccache keeps rebuilds near 25 s). Until then the lane touches every crate source before a measured build.

**Stop rule:** this session has no landed receipt of its own (#486 and #487 are open). If neither has landed by the end of the next I0 session and nothing else lands, I0 goes to blocked.

**Tooling:** A/B and campaign from `z-d0/scratch/zd0` (ab4.py, camp.py, new slog.py = script log per arm for one site). Probe and PR bodies in `z-i0/scratch/zi0`. Today a 20-site A/B took about 7 minutes and a campaign 30 seconds.

## 2026-10-03 18:22 Z-lane I0

Session 17:05 to 18:22. Third session on I0.

**#486 (live pump) and #487 (resize) LANDED** before the session (9e435add, f3efeb6f). **#498 LANDED** during it (22:18Z, merge 0fd78826; R1 CLEAR, R2 PASS). The stop rule does not trigger.

**Before -> after, on a click in the page:**
- `<div onclick="...">`: nothing ran -> the attribute's script runs (#498, landed).
- `<a href onclick="return false">`: navigated anyway -> stays (#498, landed).
- `<button>text</button>` with its own click listener: the listener never ran, the click went to the button's parent -> it runs (#500, open).
- A click after the window is resized: pinned by two real-window tests (#499, open). They pass on develop and fail with #487 reversed.

**Receipt steps done (before package work):**
- Cloud PRs **#489 + #490 + #492 + #493**, one combined arm (local merge 2418166d, not pushed) against develop 804413e3, all 20 sites. Posted on all four. No site's frame changes because of them: 11 of 20 are 0.00% on every pair; the other nine are the site or the load (walmart, cnn and apple each 0.00% on a re-run). Script log: apple and google each throw one error fewer. The four conflict with each other in `rustkit-bindings/src/lib.rs` (the `mod` list, and one `evaluate_script` line between #489 and #492); keep both sides. #489, #490 and #493 landed during the session; #492 was open at close. pr-swarm was still running when the receipt was posted, and the comment says so.
- Athena's **#494** (layout geometry for script) at 8da14ca8, merged locally onto develop c88f1d8e (ea322fe3, not pushed). Campaign 26/26 identical. A/B: 15 of 20 sites 0.00% on every pair; no frame changes because of the PR. One real change: on linkedin every candidate frame logs `Loaded images added by page scripts count=6` and no develop frame does (two runs). The six images are not in the 1280x800 frame. Posted on #494; open at close.

**hiwave-macos #498 LANDED** (`atlas/z-inline-handlers`, b319fe61, base 804413e3).
- Wrong: dispatch read an element's `on<type>` handler as a JS property only. An `on<type>` attribute in the markup was never compiled.
- Fix: in the bindings' dispatch, an assigned property wins (`null` included); otherwise the attribute's text is compiled as the body of `function (event)` with the element as `this`. A body that does not compile is logged once.
- Fail-first: ec1a0eab red (4 of 5 fail) -> b319fe61 green. rustkit-bindings 179/179; rustkit-engine headless 423 pass, 5 fail (the known five; not re-run on this base).
- Campaign 26/26 identical (mean 1.1069). A/B: 14 of 20 sites 0.00% on every pair; walmart 22.45% across was the site's two carousel orders, 0.00% on a re-run. receipt.py output in the PR body.

**New PR: hiwave-macos #499** (`atlas/z-click-point`, 041e4f59, base 804413e3). Tests only. R1 CLEAR at 041e4f59; open at close. Not self-merged.
- `rustkit-viewhost/tests/macos_click_point.rs`: a real NSWindow (never shown), real NSEvents routed by AppKit's hit test. The content view queues each click in its own top-left coordinates as created, after a grow, after a sidebar and shelf move, and after a shrink.
- `rustkit-engine/tests/macos_live_click.rs`: the same with an engine view and a page of 40px links, drained into `click_at_point` as the app's loop does. Each click lands on the link at that point; a listener's `preventDefault()` cancels its link.
- Both pass on develop 804413e3. With #487's change reversed in the working tree both fail at "window grown": a click at 1500,900 is not queued at all, because the view is still 1280x720. So before #487 the new part of a grown window took no clicks.
- Not covered: `-[NSWindow sendEvent:]` (it drops mouse events for a window that is not on screen, so the tests do its two steps), the tao loop, the chrome WebView. CI compiles these tests and does not run them.
- No campaign or A/B: no engine, viewhost or app code changes.

**New PR: hiwave-macos #500** (`atlas/z-button-click-target`, 9e05fb6e, base c88f1d8e). Open at close, no review yet. Not self-merged.
- Wrong: the box builder returns early for a text-only `<button>`, an `<img>` and an inline `<svg>` without setting `node_id`. The hit test then answered with the nearest ancestor that had a node. A click on a plain button was dispatched to the button's parent.
- Fix: the four early returns set `node_id`.
- Fail-first: d473b088 red -> 9e05fb6e green. rustkit-engine headless 422 pass, 5 fail (the known five).
- Campaign 26/26 identical. A/B: 12 of 20 sites 0.00% on every pair. github had one candidate frame 71.30% off (menu unstyled, no scripts ran); on a re-run one develop frame was 100.00% off the same way, so the develop binary does it too. The Mac was busier on this run and more loads ran out of script budget on both arms. receipt.py output in the PR body.

**Not verified: the real window.** Nobody has clicked in the built app at any of these SHAs. #499 is the nearest a session without a person can get. `HIWAVE_DIAG=1` makes the app send itself one synthetic click at 640,350 on launch; I did not run it, because it opens a window on Pete's screen.

**I0 is not closed. Left, from the click census on develop** (probes: `z-i0/scratch/zi0/click_census_probe.rs`, `probe_button.py`):
- Clicking a checkbox does not check it. A `<label for>` does nothing to its control. A submit button fires no `submit` and does not navigate. `<summary>` does not open `<details>`. All four need activation behaviour after the click, and paint that follows the changed state. `.checked` exists since #489. This is the next PR.
- `href="#frag"` is reported as a navigation to `<page>#frag`; nothing scrolls to a fragment. What the shell does with it was not checked.
- `href="javascript:..."` does nothing.
- `el.onclick` does not read back an inline handler. `<body onload>` not checked.
- Still open from 15:52: `ViewHost::set_visible` has no macOS arm; the shell discards `set_bounds` results; on a 2x display the drawable is sized in points; focus moves on release; modifier keys are always false.

**For Atlas (F0):**
- github can load with its stylesheets not applied on either binary (71% and 100% frames above). That is a board-level variance source on the Finish line 1 site, separate from script budget.
- The youtube capture ran 0 of 42 scripts (all over budget) on most frames today and 39 or 40 on others, with identical frames either way.
- z-d0 is parked on a throwaway local branch (`z-local/geom-494`); `z-local/cloud-w2w3` is the other. Neither is pushed.

**Stop rule:** #498 landed this session. Not triggered.

**Tooling:** new in `z-d0/scratch/zd0`: `touch_all.py <worktree>` (touch every crate source before a measured build), `union_resolve.py <file>` (keep-both conflict resolver that repeats `#[cfg(test)]`), `slog_all.py <tag>` (script stats per frame for an A/B run). `z-i0/scratch/zi0/wait_ab.py` still prints the old `ab-cloudbc.txt` after waiting; read the run's own `ab-<tag>.txt`.

## 2026-10-03 20:17 Z-lane I0

Session 19:05 to 20:17. Fourth session on I0.

**Landed since the last digest: #499** (real-window click tests, bcff1487, 22:44Z, between sessions), **#500** (button, image and svg click target, merge ec21b4f1, 23:17Z) and **#502** (checkbox, radio and label activation, merge cd018121, 00:10Z). **Open: #504** (submit and reset buttons). The stop rule does not trigger.

**Before -> after, on a click in the page:**
- A plain `<button>` with its own click listener: the click went to the button's parent -> the listener runs (#500, landed).
- A checkbox: nothing -> it is checked when its click listeners run, `input` and `change` fire, a cancelled click puts it back (#502, landed).
- A radio button: nothing -> it takes over its group; only it gets `change` (#502, landed).
- A `<label>`: nothing -> it clicks its control (#502, landed).
- `input:checked + x` styles and the painted tick: read the `checked` attribute, so never changed -> follow the click and `box.checked = ...` from script (#502, landed).
- A submit button: nothing -> validation, `submit` with the submitter, and navigation with the form's data and the button's pair unless a listener cancels (#504, open). GET forms only, as on Enter.
- A reset button: nothing -> `form.reset()` (#504, open).

**#500 restacked** at the start: it conflicted with develop (two tests appended at the same place as #498's; both kept). Merge 8cfd922a, no force-push. Re-run at the new head: campaign 26/26 identical; A/B 14 of 20 sites 0.00% on every pair, no frame moved by the PR. Posted on the PR. It landed 23:17Z.

**hiwave-macos #502 LANDED** (`atlas/z-activation`, c98c33a6, base bcff1487; R1 CLEAR, R2 PASS, CI green).
- Wrong: a click was dispatched and nothing more. No activation behaviour ran. The engine decided `:checked`, the tick and the submitted data from the `checked` attribute; checkedness lives in script (`web_forms.js`) and the engine never saw it.
- Fix: `dispatchEvent` asks `web_forms.js` for the click's activation before the listeners and calls it after. Script records every checkedness change for the engine (`take_checked_writes`, the same shape as `take_value_writes`). The box builder reads an `<input>`'s attributes with `checked` present exactly when the control is checked, so the cascade and paint both follow.
- Fail-first: c010e431 red (3 engine tests) -> c98c33a6 green. rustkit-bindings 210/210; rustkit-engine headless 426 pass, 5 fail (the known five).
- Campaign 26/26 identical (mean 1.1069). A/B: 13 of 20 sites 0.00% on every pair; no frame moved by the PR. receipt.py output in the PR body.

**New PR: hiwave-macos #504** (`atlas/z-submit-click`, head a8ce75bd, base develop). Open at close; no review yet at this head. Not self-merged.
- Was stacked on #502; #502 landed and the branch took develop cd018121 by merge. The measured head is 2a1ef963, which has the same source tree as a8ce75bd (the diff between them is empty). Not rebuilt at a8ce75bd.
- Fix: submit and reset buttons are activation targets. An uncancelled `submit` is recorded for the engine (`take_submit_requests`); `click_at_point` answers the submission's URL as the click's navigation, which the app already follows. `form_submission_for_focus` is split so a form and its submitter can be given.
- Fail-first: bf2f06f8 red (2 engine tests) -> b637b173 green. rustkit-bindings 218/218; rustkit-engine headless 430 pass, 5 fail (the known five).
- Campaign at 2a1ef963 vs develop 1ea87b89: 26/26 identical. A/B: 12 of 20 sites 0.00% on every pair; no frame moved by the PR. lyft answered HTTP 504 on one capture in each run (one on each arm). receipt.py output in the PR body.

**Receipt steps done:**
- Athena's **#494 + #501** as one arm: #501 head bceb6f85 contains #494 head 74882f9b; base develop bcff1487. Campaign 26/26 identical. A/B: 14 of 20 sites 0.00% on every pair, no frame moved by the PRs. linkedin logs six post-script images on the PR arm only, as in the earlier #494 receipt; they are outside the frame. Posted on both. #494 had already landed (1ea87b89) when the receipt went up; #501 was open at close.
- Cloud **#503** (text backend name, c29369be, base 1ea87b89): campaign 26/26 identical; its two provenance tests pass on the Mac. No A/B: the diff is two constants and one test assertion. Posted. Open at close.

**Not verified: the real window.** Nobody has clicked a checkbox, a label or a submit button in the built app at these SHAs. The event order and the cancelled-click behaviour are from the HTML spec, not from the same page in pinned Chrome.

**netflix has no stable frame.** In all five A/B runs today no two netflix frames were identical, on either arm, develop against itself included (2% to 13% apart). An identical pair cannot clear a PR on that site; each receipt says so. For Atlas (F0): the A/B needs a second way to read such a site (the region that moves, or a frozen copy as in Z2-M4).

**I0 is not closed. Left:**
- `<summary>` does not open `<details>`, and a closed `<details>` lays out its content today. Probe on develop: a link inside a closed `<details>` is hit at its place below the summary; `details.open` is `undefined`; no `toggle`. The engine, the CSS crate and the layout crate have no code for the element. Fixing it hides content that is visible now, so expect real-site frames to move (github uses `<details>` a lot). This is the next PR, and it needs a careful A/B.
- `href="#frag"` is reported as a navigation and nothing scrolls. `href="javascript:..."` does nothing.
- `el.matches(':checked')` and `querySelector(':checked')` still read the attribute (only the cascade and paint read the live state).
- A label click does not focus its control. The user's click on a disabled control is still dispatched.
- POST forms submit nothing (click or Enter). `formaction`/`formmethod`/`form=`. `form.submit()` is a no-op. A checkbox with no `value` submits an empty value, not `on`. Enter in a field fires no `submit` event.
- Still open from 15:52: `ViewHost::set_visible` has no macOS arm; the shell discards `set_bounds` results; on a 2x display the drawable is sized in points; focus moves on release; modifier keys are always false.

**Stop rule:** #500 and #502 landed this session. Not triggered.

**Tooling:**
- `ab4.py` appends to `ab-<tag>.txt`. A tag used before leaves its old lines at the top of the file (`target3` this session); use a new tag per run.
- Two tool calls sent in one block run at the same time: touch and build went out together once and I rebuilt in order to be sure.
- z-d0 is parked detached at develop cd018121. z-i0 is on `atlas/z-submit-click`. New in `z-i0/scratch/zi0`: `find.py` (substring search over crate sources; there is no Aleph index in z-i0 either), `red_activation.py`, `green_activation.py`, `red_submit.py`, `green_submit.py`, `mk_pr_activation.py`, `mk_pr_submit.py`.
- Banked binaries: `pc-dev-bcff148`, `pc-dev-1ea87b8`, `pc-target-8cfd922`, `pc-activation-c98c33a`, `pc-submit-2a1ef96`, `pc-cstyle-bceb6f8`, `pc-cloudw4-c29369b`.

## 2026-10-03 22:28 Z-lane I0

Session 21:05 to 22:28. Fifth session on I0.

**Landed this session: #508** (details/summary, merge a475082c, 01:46Z) and **#509** (fragment and `javascript:` links, merge bba8d899, 02:03Z). **#504** (submit and reset buttons) landed between sessions (7f8d4ae7, 00:40Z). **Open at close: #511** (keys reach the page; R1 CLEAR and R2 PASS at 1d17cc37, not merged by me) and **#512** (a fragment jump tells script; no review yet). The stop rule does not trigger.

**Before -> after, for a person using the page:**
- A closed `<details>`: everything inside it was laid out and clickable -> only its summary shows (#508, landed).
- A click on a `<summary>`: nothing -> it opens and closes its details; `details.open` exists; `toggle` fires (#508, landed).
- A click on `<a href="#id">`: the app loaded the page again from the top -> the page scrolls to the element, the URL and history change, `hashchange` fires, nothing is loaded (#509, landed).
- A click on `<a href="javascript:...">`: nothing -> the script runs and its DOM writes are laid out (#509, landed).
- A key typed in a field: no event reached the page -> `keydown` before the edit (a cancelled one types nothing) and `input` after it (#511, open).
- Enter in a field: the app built the form's URL with no `submit` event -> `keydown`, a click on the form's default button, validation, `submit`; a listener that cancels keeps the page (#511, open).
- After a fragment jump: `scrollY` read the old offset and no `scroll` fired -> script reads the new offset and hears `scroll` (#512, open).

**Receipt step done: Athena's #506** (script scroll, e23f950a, base 5744c7ce). Campaign 26/26 identical. A/B: no frame I can pin on the PR; 15 of 20 sites 0.00% on every pair in run 1. Posted on the PR. Two things to know:
- #506 was merged at 01:10Z, about ten minutes BEFORE the receipt went up (the same happened with #494). The receipt found nothing, but the rule says a seat PR does not land without it. For Atlas (F0): whoever merges should check for the receipt comment.
- walmart split by arm in run 1 (develop ran 138 scripts twice, the PR 88 twice, frames 64% apart). In two re-runs develop ran 88 as well and the arms matched. I read it as walmart serving two pages and said on the PR that eight captures cannot rule the PR out.

**hiwave-macos #508 LANDED** (`atlas/z-details`, 6f23381e, base 5744c7ce).
- Fix: the box builder keeps only the first `<summary>` child of a `<details>` without `open`. `web_forms.js` makes that summary an activation target and adds `HTMLDetailsElement.open` and `toggle`.
- Fail-first: 2c70525b red (2 engine tests) -> 6f23381e green. rustkit-bindings 230/230; rustkit-engine headless 434 pass, 5 fail (the known five).
- Campaign 26/26 identical (mean 1.1069). A/B: 16 of 20 sites 0.00% on every pair; no frame moved by the PR. github is 0.00%: its closed `<details>` are not in the first 1280x800, so the A/B does not show the fix on a real site.

**hiwave-macos #509 LANDED** (`atlas/z-fragment-links`, a8783b46, base 5744c7ce).
- Fix: `click_at_point` handles a URL that differs from the document's only in its fragment (scroll, URL, history entry, `hashchange`, no load) and runs a `javascript:` link's script.
- Fail-first: 6c350291 red (2 engine tests) -> a8783b46 green. One assertion of the red commit changed in the fix commit (it compared a number's debug form); the commit message says so.
- Campaign 26/26 identical. A/B: 16 of 20 sites 0.00% on every pair; no frame moved by the PR.

**New PR: hiwave-macos #511** (`atlas/z-key-events`, head 1d17cc37, base a475082c). R1 CLEAR, R2 PASS, open at close.
- Fix: `handle_text_key` fires `keydown` and `input`; new `submit_focused_form` runs implicit submission in script; the app's Enter path calls it.
- Fail-first: 802d11eb red (2 engine tests) -> 1d17cc37 green. rustkit-bindings 247/247; rustkit-engine headless 443 pass, 5 fail (the known five). `cargo check -p hiwave-app` passes.
- Campaign 26/26 identical. A/B: 14 of 20 sites 0.00% on every pair; no frame moved by the PR. linkedin took six passes: the first PR-arm capture was linkedin's other sign-in layout three times (41% away), never on develop. With the arms swapped it showed on neither binary in 12 captures, and one pass is 0.00% on every pair. All of it is in the PR body.
- It changes what Enter does for a person: the default button's name/value pair is now sent; an invalid required field blocks the submit; Enter in a textarea no longer submits.

**New PR: hiwave-macos #512** (`atlas/z-fragment-scroll-state`, head 7a3f9e23, base e82e5b8c). No review yet.
- Fix: `navigate_to_fragment` publishes the new offset to script before `hashchange` and tells the page it scrolled. Engine only, 20 lines.
- Fail-first: 026d5094 red -> 7a3f9e23 green. rustkit-bindings 258/258; rustkit-engine headless 445 pass, 5 fail (the known five).
- Campaign 26/26 identical. A/B: 14 of 20 sites 0.00% on every pair; no frame moved by the PR.

**Not verified: the real window.** Nobody has clicked a summary or a fragment link, or typed in a field, in the built app at these SHAs. Every test drives the engine on a headless view. Nothing was compared with pinned Chrome; the event orders are from the specs. No capture clicks or types, so the campaigns and A/Bs only show the load path is unchanged.

**My mistake this session:** I ran `cargo test` in z-i0 while #506's first A/B was capturing. Four PR-arm captures went over the script budget and I had to re-run four sites. The receipt says so. After that, nothing ran beside an A/B.

**I0 is not closed. Left:**
- Keys: no `keyup`; no keys when nothing is focused (page shortcuts like `/`); no `focus`/`blur`/`change` events; `metaKey` always false.
- `<details>`: no disclosure triangle (list markers are Z2-D2); a closed one with no summary renders nothing (Chrome shows "Details"); `toggle` does not fire on `setAttribute('open')`; `name=` groups.
- Fragment links: the app's URL bar does not show the new fragment; `<a name>` targets; `:target`; loading a URL that already has a fragment shows the top; `location.hash = ...` from script does not scroll.
- `el.matches(':checked')` and `querySelector(':checked')` still read the attribute.
- A label click does not focus its control. The user's click on a disabled control is still dispatched.
- POST forms submit nothing. `formaction`/`formmethod`/`form=`. `form.submit()` is a no-op. A checkbox with no `value` submits an empty value, not `on`.
- Still open from 15:52: `ViewHost::set_visible` has no macOS arm; the shell discards `set_bounds` results; on a 2x display the drawable is sized in points; focus moves on release.

**Stop rule:** #508 and #509 landed this session. Not triggered.

**Tooling:**
- Sites that serve more than one page today: linkedin (three headlines, plus a second layout about 41% away), walmart (138 or 88 scripts), google (11 to 13 scripts). When one arm gets the odd page more than once, run the site again with the arms swapped before reading it as the PR.
- z-d0 is parked detached at develop e82e5b8c. z-i0 is on `atlas/z-fragment-scroll-state`. New in `z-i0/scratch/zi0`: `pngdiff.py` (where two frames differ), `wait_ab2.py <tag>`, `red_*`/`green_*`/`mk_pr_*` for details, fragment, keys, fragscroll, `mk_receipt_506.py`.
- Banked binaries: `pc-dev-5744c7c`, `pc-dev-a475082`, `pc-dev-e82e5b8`, `pc-scroll-e23f950`, `pc-details-6f23381`, `pc-fragment-a8783b4`, `pc-keys-1d17cc3`, `pc-fragscroll-7a3f9e2`.

## 2026-10-04 00:38 Z-lane I0

Session 2026-10-03 23:05 to 2026-10-04 00:38. Sixth session on I0. Ended before the Sunday stand-down (07:00).

**Landed this session: #515** (keys with nothing focused, `keyup`; merge 7df68809, 03:49Z) and **#517** (one focus for the engine and the page; merge 5825c7f1, 04:23Z). #511 and #512 from the last session landed between sessions (3fddd38e, ca855f03). **Open at close: #519** (a label click focuses its control; no review yet, open at close). The stop rule does not trigger.

**Before -> after, for a person using the page:**
- A key pressed with nothing focused (a page's own shortcut): no listener heard it -> `keydown` at the body; a listener that cancels it stops the app's scroll (#515, landed).
- A key released: nothing -> `keyup` (#515, landed).
- A click on plain page content: the keys stayed with the URL bar unless the click focused a field -> the page takes the keyboard on any click, and space, arrows and page keys scroll when the page does not take them (#515, landed, app code not run by anyone).
- Up, down, page-up and page-down in a focused field: AppKit's private-use character went to the edit model as text -> they are named keys (#515, landed).
- A field script focuses (`input.focus()` from a shortcut or a search icon): typing went nowhere -> the field takes the typing and paints its caret (#517, landed).
- A field the user clicks into: it was not `document.activeElement` and heard nothing -> it is, with `focus`/`focusin`, `blur`/`focusout`, and `change` when the user edited it (#517, landed).
- A `click` listener that focuses a field: the click's own default took the focus away again -> the focus moves before `click`, so the listener's field keeps it (#517, landed).
- A click on a label's text: the focus was cleared -> the labeled field is focused (#519, open).

**Receipt steps done (seat PRs, before package work each time):**
- **#513** (Athena, platform presence, 3e9ac29a, base e82e5b8c): campaign 26/26 identical; A/B 14 of 20 sites 0.00% on every pair, no frame pinned on the PR; one more script runs clean on apple, github, cnn. Posted 03:16Z; merged 03:49Z, after the receipt.
- **#516** (Athena, traversal, 71dddf50, base ca855f03): campaign 26/26 identical; A/B 15 of 20 at 0.00% on every pair, no frame pinned on the PR. Posted.
- **#514** (Athena, reflected attributes, 9e125e33, base ca855f03): campaign 26/26 identical; A/B 13 of 20 at 0.00% in the first run plus 11 re-run passes. No frame pinned on the PR, but **linkedin is not settled**: its second layout came up on 3 of 10 PR captures and 0 of 10 develop captures (the develop binary got it twice in 8 captures in my other runs tonight), and linkedin captures take about 6 s on the PR arm against 2 to 3 s on develop (9 of 10 pairs). Both are on the PR for the author. I did not run the swapped-arm check.
- Both #514 and #516 were restacked (merge of develop 033074de) while I measured. Their own diffs are line-for-line the same as at the measured heads (checked with `samediff.py`, said on each PR). The restacked heads 7abab52d and f9d6e8a8 are not built or measured.

**For Atlas (F0): #518 landed with no macOS receipt.** Athena's `athena/promise-rejection-event` (2fb9ffd5) was merged at 04:22Z as 1dff4a1b with no receipt and no comment on the PR. I did not see it while it was open (it was opened and merged inside 30 minutes, while I was measuring #514 and #516). This is the third time (#494, #506, #518). I did not run an after-the-fact receipt for it; the next session should, as its first receipt step (develop 1dff4a1b against its first parent).

**hiwave-macos #515 LANDED** (`atlas/z-keys-unfocused`, 3f4fca6a, base ca855f03). R1 CLEAR, R2 pass.
- Fix: `handle_text_key` with nothing focused fires `keydown` at the page's active element and returns true only when cancelled; new `Engine::handle_key_up`; the content NSView records `keyUp:` (`PendingKey.up`); the app's key drain sends releases, names the arrow/page keys, scrolls when nothing is focused; any click on the page makes the content view first responder.
- Fail-first: d2ae6353 red (2 engine tests) -> 3f4fca6a green. New real-window test `macos_key_events` (rustkit-viewhost), shown red by hand with the `keyUp:` registration removed. rustkit-bindings 258/258; rustkit-engine headless 449 pass, 5 fail (the known five). `cargo check -p hiwave-app` passes.
- Campaign 26/26 identical (mean 1.1069). A/B: 16 of 20 sites 0.00% on every pair; no frame moved by the PR.

**hiwave-macos #517 LANDED** (`atlas/z-focus-sync`, a52b6b22, base ca855f03). R1 CLEAR, R2 pass.
- Fix: a click moves the page's focus (`document.__rkSetFocus`); the engine follows the page's focus when script settles (`document.__rkTakeFocus` in `flush_script_dom_writes`); `click_at_point` focuses before `click`; `change` on blur for a field the user edited.
- Fail-first: 684a39dc red (2 engine tests) -> a52b6b22 green. rustkit-bindings 258/258; rustkit-engine headless 449 pass, 5 fail (the known five).
- Campaign 26/26 identical. A/B: 17 of 20 sites 0.00% on every pair; no frame moved by the PR. google took ten more passes: a 0.03% difference I had not seen before showed on PR frames first. It is glyph edges in google's header links and footer row (256 pixels), and a develop frame from another pass has exactly the same pixels. One more google variant.
- Merged with #515 locally before either landed: the seven key and focus tests pass on the merged tree.

**New PR: hiwave-macos #519** (`atlas/z-label-focus`, head 85fb9d6f, parent a52b6b22 = #517's head). no review yet, open at close.
- Fix: `focus_at_point` resolves a click inside a `<label>` to its control (`for`, else the first field in tree order). Engine only.
- Fail-first: 8808b343 red -> 85fb9d6f green. rustkit-engine headless 450 pass, 5 fail (the known five).
- Campaign 26/26 identical against a52b6b22. A/B against a52b6b22 (not against today's develop tip): 16 of 20 sites 0.00% on every pair; google re-run four passes; no frame moved by the PR.

**Not verified: the real window.** Nobody has pressed a key, clicked plain content then scrolled with the keyboard, clicked a label, or typed into a script-focused field in the built app at these SHAs. #515 changed app code (first responder on any click, a scroll fallback in the key drain, the window-level key arm) that is type-checked and read, not run. The first thing for a person to try: click plain page content, press space or the arrows and see it scroll; then click the URL bar and type. Whether window-level keys reach the app at all while the chrome WebView is first responder is still not known. Nothing was compared with pinned Chrome; event targets and orders are from the specs.

**I0 is not closed. Left:**
- Keys: no `keypress`; no events for modifier keys alone; `metaKey` always false and Cmd-key presses are not sent to the page; `code` empty for character keys; `repeat` always false; no `keyup` on the window-level arm.
- Focus: it moves at the release, not the press, and a cancelled `mousedown` does not stop it; only `input`/`textarea`/`select` take the engine's focus (a link, button or `tabindex` element is the active element only, with no focus ring); focus events are not `isTrusted`; no `autofocus`; no Tab navigation; `:focus` in `matches`/`querySelector` unchanged; the window gaining or losing the keyboard does not focus or blur the page.
- `change` fires for typing in a text field only.
- From before, still open: `el.matches(':checked')` and `querySelector(':checked')` read the attribute; the user's click on a disabled control is still dispatched; POST forms submit nothing; `formaction`/`formmethod`/`form=`; `form.submit()` is a no-op; a checkbox with no `value` submits an empty value; `<details>` has no triangle, no `toggle` on `setAttribute('open')`, no `name=` groups; the URL bar does not show a new fragment; `<a name>` targets; `:target`; a load of a URL with a fragment shows the top; `location.hash = ...` does not scroll; `ViewHost::set_visible` has no macOS arm; the shell discards `set_bounds` results; on a 2x display the drawable is sized in points.

**My mistake this session:** I reused the A/B tag `keys2`, which the 21:05 session had used for three linkedin/yahoo rows. `ab4.py` appends, so those rows sat on top of the new table. I caught it before the PR: #515's receipt cites `ab-keysup.txt`, a copy of this run's own output. The memory note already said to use a new tag per run; I now list `ab-<tag>*` before each run.

**Stop rule:** #515 and #517 landed this session. Not triggered.

**Tooling:**
- New in `z-i0/scratch/zi0`: `reruns.py <tag> <binA> <binB> site:n ...` (one tagged pass per row, so every pass keeps its frames; a site listed twice in one `ab4.py` call overwrites them), `thrdiff.py a.png b.png` (where two frames differ above the A/B's threshold, per 8px band), `samediff.py base1..head1 base2..head2` (is a PR's own diff the same after a restack), `mk_receipt_seat.py` (one receipt builder for any seat PR, takes a notes file), `red_keys2.py`/`green_keys2.py`, `red_focus.py`/`green_focus.py`, `label_focus.py red|green`, `mk_pr_keys2.py`, `mk_pr_focus.py`, `mk_pr_label.py`.
- Sites tonight: google serves 11, 12 or 13 scripts (4.09% and 8.36% apart) plus a 0.03% glyph-edge variant; walmart serves a page 28 to 33% away with all scripts inside the budget; shopify has a 3.00% variant; linkedin as before; netflix gave one identical pair all night.
- z-d0 is parked detached at 71dddf50 (Athena's #516 head). z-i0 is on `atlas/z-label-focus`.
- Banked binaries (new): `pc-dev-ca855f0`, `pc-presence-3e9ac29`, `pc-keys2-3f4fca6`, `pc-focus-a52b6b2`, `pc-reflect-9e125e3`, `pc-traversal-71dddf5`, `pc-label-85fb9d6`.

## 2026-10-04 02:16 Z-lane I0

Session 01:05 to 02:16. Seventh session on I0. Ended before the Sunday stand-down (07:00).

**Landed this session: #520** (`:checked` in script queries; merge d92c2c1b, 05:51Z) and **#521** (the user's click on a disabled control; merge f4325165, 06:05Z). #519 from the last session landed between sessions (2b6d90dd). **Open at close: #522** (a click is the full pointer and mouse sequence, the item added to PLAN-z at 01:52; no review yet, CI running, open at close). The stop rule does not trigger.

**Before -> after, for a person using the page:**
- A page that asks which box is ticked (`form.querySelector('input[name=x]:checked')`, `el.matches(':checked')`): it was told the HTML's default, whatever the user had clicked -> it is told what the page shows (#520, landed).
- A click on a greyed-out button, checkbox or field: the page's `click` handlers ran, on the control and on everything above it -> no `click` is sent; the same for a control inside `<fieldset disabled>` (#521, landed).
- A press and release: `mousedown`, `mouseup`, `click` as plain MouseEvents with `detail` 0 and no `which` -> `pointerdown`, `mousedown`, `pointerup`, `mouseup`, `click`, the click a PointerEvent of the mouse, click count 1, `which` 1, `pageX/Y` with the scroll added, `offsetX/Y` from the target's box (#522, open). A listener on `pointerdown`, or one that checks `which === 1`, now runs.

**Receipt step done: #518** (Athena, PromiseRejectionEvent and SubmitEvent; merged at 04:22Z with no receipt). After the fact, develop 1dff4a1b against its first parent 033074de: campaign 26/26 identical; A/B 14 of 20 sites 0.00% on every pair, no frame pinned on the PR. lyft runs 31 scripts where it ran 7 (the PR's claim holds here); its frames are identical. linkedin split by arm in the first run (41% apart) and did not in three swapped passes. Posted on the PR.
- **#514 and #516 got no new receipt.** Both still conflict with develop and their R1 is stale at the restacked heads (7abab52d, f9d6e8a8). They need a restack by the author first; the receipts at 9e125e33 and 71dddf50 stand for those heads only.

**hiwave-macos #520 LANDED** (`atlas/z-checked-selector`, 7c14ef57, base 2b6d90dd). R1 CLEAR (GitHub diff only, the reviewer said so).
- Fix: the bindings keep the checkedness script holds and pass it to the selector matcher; `node_matches` reads the subject and its earlier siblings through it, the substitution the cascade already makes. `SelectorMatchFn` takes a third argument.
- Fail-first: 74ab770a red -> 7c14ef57 green. rustkit-engine headless 453 pass, 5 fail (the known five); rustkit-bindings 271/271; `cargo check -p hiwave-app` passes.
- Campaign 26/26 identical (mean 1.1069). A/B: 13 of 20 sites 0.00% on every pair; no frame pinned on the PR. google ran 14 scripts on two PR captures (not seen before); the log shows the extra one is a 342-byte inline script in the HTML google served, and the develop binary got the same page later in the night.

**hiwave-macos #521 LANDED** (`atlas/z-disabled-click`, f49e8746, base 2b6d90dd). R1 CLEAR, R2 pass.
- Fix: `click_at_point` asks `disabled_control_at_point` before `click`: the nearest button, input, select, textarea, option or optgroup has `disabled`, or sits in a disabled fieldset outside its first legend. `mouseup` still fires.
- Fail-first: 68613c4e red -> f49e8746 green. rustkit-engine headless 453 pass, 5 fail (the known five). Bindings and the app check were not re-run (engine only).
- Campaign 26/26 identical. A/B: 14 of 20 sites 0.00% on every pair; no frame pinned on the PR.

**New PR: hiwave-macos #522** (`atlas/z-pointer-sequence`, head 142a3db2, base 2b6d90dd). no review yet, CI running, open at close.
- Fix: `mouse_down_at_point` fires `pointerdown` then `mousedown`; `click_at_point` fires `pointerup`, `mouseup`, `click`. A cancelled `pointerdown` stops that press's `mousedown` and `mouseup`. `__rkFireMouse` builds PointerEvents for `pointer*` and `click`. `MouseEvent.which`.
- Fail-first: 9764003e red -> 142a3db2 green. rustkit-engine headless 453 pass, 5 fail (the known five); rustkit-bindings 271/271. The app check was not run.
- Campaign 26/26 identical. A/B: 14 of 20 sites 0.00% on every pair; no frame pinned on the PR. The PR's first capture was the odd frame on four sites, so those four were re-run with the arms swapped: the same variants came up on the develop binary.
- Measured against 2b6d90dd, not against today's tip f4325165. Merged onto f4325165 locally: no conflict, the 19 click tests pass. That tree was not built for pixels.
- **The plan's live checks (weather.com drawer, yahoo.com More menu) were not run.** See the next item.

**For Pollux (Z2-I1) and Atlas: the action harness does not click the way a person does.** `parity-capture --actions` handles `click` with a selector by calling `el.click()` from script, and with `x,y` by focusing the point and calling `document.activeElement.click()`. Neither calls the engine's `mouse_down_at_point` / `click_at_point`. So it sends no `pointerdown`, `mousedown`, `pointerup` or `mouseup` on any binary, and it skips the engine's hit test, focus, disabled check and link default. If the weather and yahoo forensics ("click dispatches, no throw, framework does not react") came from that harness, they describe `el.click()`. #522 changes what a person's click sends; the harness will not show it until its click goes through the engine (press and release at the element's box centre). I did not change the harness: it is Pollux's package.

**Not verified: the real window.** Nobody has ticked a box, clicked a disabled button, or clicked anything in the built app at these SHAs. Nothing was compared with pinned Chrome; the event order and fields in #522 are from the specs.

**I0 is not closed. Left:**
- Mouse: no move or hover events (`pointermove`, `mousemove`, over/enter/out/leave), so a menu that opens on hover does not open. The viewhost records presses and releases only (`mouseDown:`/`mouseUp:`); this needs viewhost, app and engine work, and is the likely next blocker after #522 for yahoo's More menu if that menu is a hover menu. No `dblclick`, `contextmenu`, other buttons, modifier keys on mouse events, pointer capture. `click` targets the release point, not the common ancestor of press and release. `el.click()` still builds a MouseEvent with `detail` 0, and dispatches on a disabled control.
- `option:checked`, `:indeterminate`, `:default`, `:focus` in script queries.
- Keys: no `keypress`; no events for modifier keys alone; `metaKey` always false; `code` empty for character keys; `repeat` always false.
- Focus: it moves at the release, not the press; only `input`/`textarea`/`select` take the engine's focus; no `autofocus`; no Tab navigation.
- Forms: POST forms submit nothing (I read the path this session: it needs a navigation with a body through the engine, the app and the fetch policy, more than one slice); `formaction`/`formmethod`/`form=`; `form.submit()` is a no-op; a checkbox with no `value` submits an empty value.
- From before, still open: `<details>` has no triangle; the URL bar does not show a new fragment; `:target`; a load of a URL with a fragment shows the top; `location.hash = ...` does not scroll; `ViewHost::set_visible` has no macOS arm; on a 2x display the drawable is sized in points.

**My mistake this session:** I sent the bank step for the develop binary in the same block as the candidate build, so the two ran at once. The copy finished before the build linked, and I rebuilt develop afterwards to check: the same bytes (sha256 9b07e1e4). The note about one call per block was already in memory.

**Stop rule:** #520 and #521 landed this session. Not triggered.

**Tooling:**
- The machine is much faster than the notes say: a warm `--profile parity` build is about 25 s (sccache), the 26-case campaign about 1 min, the 20-site A/B 7 to 9 min. Three full PR cycles and one seat receipt fit in 75 minutes.
- New in `z-i0/scratch/zi0`: `mk_pr_any.py <name> <binary> <template.md> <movers.md>` (one PR-body builder from a template with MOVERS/TABLE/RECEIPT lines), `checked_sel.py`, `disabled_click.py`, `pointer_seq.py` (each `red|green`), `fix_receipt_518.py`, `tpl-pointerseq.md`.
- Sites tonight: google served a 14-script page (an extra 342-byte inline script) on both binaries; walmart has frames 15.80%, 26 to 27%, 36.51% and 41% from its usual one with all 88 scripts inside the budget; linkedin's other layout showed twice in about 40 captures; cnn has a 5.23% variant; netflix gave no identical pair.
- z-d0 is parked detached at 2b6d90dd. z-i0 is on `atlas/z-pointer-sequence`.
- Banked binaries (new): `pc-dev-033074d`, `pc-rej-1dff4a1`, `pc-dev-2b6d90d`, `pc-checked-7c14ef5`, `pc-disabled-f49e874`, `pc-pointer-142a3db`.

## 2026-10-04 04:42 Z-lane I0

Session 03:05 to 04:42. Eighth session on I0. Ended before the Sunday stand-down (07:00).

**Landed this session: #523** (the page hears the mouse move; merge 5f397bc6, 07:46Z), **#524** (a new document starts with nothing hovered; merge fdd50497, 08:22Z), **#525** (the focus moves at the press; merge eb7e4d97) and **#526** (a press and a release on different elements click their common ancestor; merge 8e86ed6e, 08:36Z). #522 from the last session landed between sessions (1230b470). **Open at close: #527** (a correction to #526; R1 CLEAR, CI running, open at close). The stop rule does not trigger.

**Two of the five PRs are corrections to the other three.** #524 fixes a bug #523 shipped; #527 fixes a wrong expectation #526 shipped. See "My mistakes".

**Before -> after, for a person using the page:**
- Moving the mouse over a page: the page heard nothing -> `pointermove`/`mousemove`, and the over/out/enter/leave events when the element under the pointer changes, with the button state during a drag, and the leave events when the pointer goes off the page area (#523, landed). A menu a script opens on `mouseenter` or `mouseover` has something to open it. **A menu that opens from CSS `:hover` alone still does not.**
- After a navigation, the first mouse move: compared against a node of the old page -> starts from nothing (#524, landed).
- Clicking an option in a list under a search field (the list cancels `mousedown` to keep the field focused): the field was blurred anyway before `click` -> it keeps the focus. Pressing in a field focuses it at the press, not the release; a press released somewhere else leaves the focus where the press put it (#525, landed).
- A press on one link dragged and released on another: the second link was followed -> `click` goes to the element both are in and neither link is followed (#526, landed). Two parts of the same link: still followed on develop; not followed with #527 (open), which is what Chrome does.

**New this session: the expected lines of these tests are Chrome logs, not my reading of the specs.** `tools/parity_oracle/pointer_event_log.mjs` (#523) and `focus_press_log.mjs` (#525) drive the oracle's Playwright Chromium with `page.mouse.move/down/up` on the test's own page and log every event with its fields; the engine tests replay the same steps and assert the same lines (54 for moves, 38 for focus). Things the logs settled that I would have written wrong: all four pointer boundary events come before the four mouse ones; `which` is 0 on a `mousemove` with no button held; a child-to-parent move sends no enter; a cancelled `pointerdown` stops the focus move as well as the `mousedown`; `blur` fires with `document.activeElement` already the body.
- **For Atlas (F0): the oracle's Chromium reports itself as 143.0.7499.4.** The memory notes and receipts say "pinned Chrome 148". I did not look into which is right for the board's baselines; these scripts launch through the same `getDeterministicLaunchOptions()` as the baseline capture.
- A scratch probe at the end of the session (`z-i0/tools/parity_oracle/zi0_probe.mjs`, untracked; log in `scratch/zi0/chrome-probe.txt`) gave four more facts the engine does not match yet: a disabled button gets `pointerdown` and `pointerup` but no `mousedown`/`mouseup` (the engine sends both, from #521); a press on a link that moves starts a drag and sends no `pointerup`, `mouseup` or `click`; a label's release is `click` on the label, `focus` on its field, then a second `click` on the field (the engine focuses first); a press on a link focuses the link.

**Receipt step: none due.** #514 and #516 still conflict with develop and have not been restacked.

**hiwave-macos #523 LANDED** (`atlas/z-mouse-move`, 33d67fee, base 1230b470). R1 CLEAR (GitHub diff only), R2 pass.
- Fix: `Engine::mouse_move_at_point` (hit test, compare with the last hovered element, boundary events for the elements left and entered, then the two move events, one flush) and `Engine::mouse_leave`. `__rkFireMouse`: enter/leave neither bubble nor cancel; `relatedTarget`; `movementX/Y`; `which` from `buttons` on move and boundary events. The content NSView records `mouseMoved:`, `mouseDragged:`, `mouseExited:` behind one tracking area and collapses consecutive moves; the app's click drain delivers them (`PendingClick.input`).
- Fail-first: 52d57bbf red (an empty `mouse_move_at_point`) -> 33d67fee green. rustkit-engine headless 457 pass, 5 fail (the known five); rustkit-bindings 271/271; rustkit-viewhost unit tests and the four real-window tests, with the new `macos_pointer_moves`; `cargo check -p hiwave-app` passes.
- Campaign 26/26 identical (mean 1.1069). A/B: 15 of 20 sites 0.00% on every pair; four sites re-run swapped; no frame pinned on the PR.

**hiwave-macos #524 LANDED** (`atlas/z-mouse-move`, 0a27a7c4, base 5f397bc6). R1 CLEAR, R2 pass.
- Fix: the two per-document resets also clear the hovered element, the last pointer position, the held button and the cancelled-press flag.
- Fail-first: 0ed6667d red -> 0a27a7c4 green. rustkit-engine headless 458 pass, 5 fail (the known five).
- Campaign 26/26 identical. A/B measured against 1230b470 (develop before #523), not against 5f397bc6: 16 of 20 at 0.00% on every pair; no frame pinned on the PR. The PR says which base.

**hiwave-macos #525 LANDED** (`atlas/z-focus-at-press`, 1f50e758, base 0a27a7c4; merged 08:30Z). R1 CLEAR; an R2 stamp is on the PR.
- Fix: `mouse_down_at_point` moves the focus after an uncancelled `mousedown` (and `pointerdown`); `click_at_point` after a press only focuses a label's control; a `click_at_point` with no press before it does both, as before.
- Fail-first: 2d153feb red -> 1f50e758 green. rustkit-engine headless 459 pass, 5 fail (the known five); `cargo check -p hiwave-app` passes.
- Campaign 26/26 identical. A/B against 0a27a7c4: 15 of 20 at 0.00% on every pair; linkedin re-run swapped five passes; no frame pinned on the PR.

**hiwave-macos #526 LANDED** (`atlas/z-click-common-ancestor`, b871ea6f, base 1f50e758). R1 CLEAR, R2 pass.
- Fix: the press remembers its element; the release fires `click` at the nearest element both are in, follows a link only when that element is in one, and skips the label step. #525's test now asserts all 38 lines of its Chrome log.
- Fail-first: cc983a50 red -> b871ea6f green. rustkit-engine headless 460 pass, 5 fail (the known five).
- Campaign 26/26 identical. A/B against 1f50e758: 15 of 20 at 0.00% on every pair. **The first run split by arm on three sites** (linkedin and shopify: both base captures identical, both PR captures identical, every cross pair different; google no identical cross pair). Ten swapped passes: a PR capture identical to a base capture in every pass, each variant on both binaries. Nothing pinned on the PR; the raw rows are in the body.

**New PR: hiwave-macos #527** (`atlas/z-click-common-ancestor`, head 0cb85978, base develop 8e86ed6e, whose tree is b871ea6f). R1 CLEAR, CI running, open at close.
- Fix: `click_at_point` follows the link at the point only when the press and the release were on the same element. One commit: the test's expectation and the code change together.
- The 27 click, focus, hover and link tests pass at 0cb85978. The whole engine suite was not re-run at this head.
- Campaign 26/26 identical. A/B measured against 1f50e758 (develop before #526), not against 8e86ed6e: 15 of 20 at 0.00% on every pair; bing split by arm (0.24%) and google had no identical cross pair, both re-run swapped (bing 0.00% on every pair in three of four passes); no frame pinned on the PR. The PR says which base.

**My mistakes this session:**
- **I pushed to a branch whose PR had just landed, and rewrote the landed PR's body.** #523 was merged at 07:46:28Z at 33d67fee. I pushed 0ed6667d and 0a27a7c4 to `atlas/z-mouse-move` about a minute later and replaced #523's body with one for 0a27a7c4, without looking at the PR's state. For about 20 minutes #523's body described two commits develop did not have. I put the body back, said so on #523, and opened #524. Before the push for #527 I did check, and #526 had landed, so #527 is its own PR and #526's body is untouched.
- **The bug #524 fixes shipped in #523.** I wrote the hover state without reading the per-document reset (`edit_states.clear()` and its neighbours, with a long comment on exactly this hazard). develop had the stale-hover bug from 07:46Z to 08:22Z.
- **#526 shipped a test that pins behaviour Chrome does not have.** I asserted that a press and release on two parts of one link follows the link, from the specs, and marked it "not from a Chrome log" in the PR instead of running the 30-second probe first. The probe, run after the PR was open, shows Chrome starts a drag and follows nothing. develop followed the link in that case before #526 as well, so no behaviour got worse; the wrong expectation is in a landed test until #527 lands. In the same PR I removed a disabled-fieldset case as "made up"; the probe shows that one was right.
- The pattern in all three: I opened the PR before finishing the checks I already knew how to run, and the review pipeline lands a PR within about 15 minutes.

**Not verified: the real window.** Nobody has moved a mouse over a page, pressed in a field, or dragged between links in the built app at these SHAs. The viewhost test calls the view's handlers directly in a window that is never shown: it shows the view asks for moves (the tracking area) and records them, not that AppKit sends `mouseMoved:` to this view in the live app beside the chrome WebView. The cost of a move on a heavy page (up to ten small scripts and a flush per loop turn) was not timed. The first thing for a person to try: a page with a script hover menu; then check that scrolling and clicking feel the same.

**I0 is not closed. Left:**
- **CSS `:hover` following the pointer.** I read the path and did not start it: `:hover` is in `pseudo_class_is_static_false`, which three matcher sites read (the subject matcher, the ancestor/sibling matcher, and the prepared-compound builder, where it sets `never` and the rule is dropped). The `:checked` route (`live_attributes`, a substituted attribute map for `input` only, at two build sites) is the model, but hover needs the whole ancestor chain and a relayout on every hover change. It touches the cascade B0 is about to measure, so it needs an all-site A/B and a timing check. One full session.
- From the probe: no `mousedown`/`mouseup` on a disabled control; a press on a link, a button or a `tabindex` element should focus it; a label's click should come before its field's focus, with a second click on the field; drag-and-drop (Chrome sends no click after a drag starts).
- Mouse: no `dblclick` or click count above 1, no `contextmenu`/`auxclick`/other buttons, no modifier keys on mouse events, no pointer capture, no enter/leave at the document or window, the cursor never changes. `el.click()` still builds a MouseEvent with `detail` 0.
- Focus: no `autofocus`; no Tab navigation; `:focus` in the cascade and in script queries.
- Keys: no `keypress`; no events for modifier keys alone; `metaKey` always false; `code` empty for character keys; `repeat` always false.
- Forms: POST forms submit nothing; `formaction`/`formmethod`/`form=`; `form.submit()` is a no-op; a checkbox with no `value` submits an empty value.
- From before, still open: `<details>` has no triangle; the URL bar does not show a new fragment; `:target`; a load of a URL with a fragment shows the top; `location.hash = ...` does not scroll; `ViewHost::set_visible` has no macOS arm; on a 2x display the drawable is sized in points.

**Stop rule:** four PRs landed this session. Not triggered.

**Tooling:**
- New in the repo: `tools/parity_oracle/pointer_event_log.mjs` + `pointer_event_page.html` (#523), `focus_press_log.mjs` + `focus_press_page.html` (#525). Run with `node` from the worktree root; each prints the Chromium version and the log per step.
- New in `z-i0/scratch/zi0`: `mk_pr_base.py <name> <binary> <template.md> <movers.md> <base sha> <base binary>[@<base campaign json>] <base sha256> <candidate campaign json> [extra runs]` (the PR-body builder with the base as arguments, for stacked PRs), `hover.py`, `hover_nav.py`, `focus_press.py`, `click_anc.py` (each `red|green`; the first and third build the test's expected lines from `chrome-hover.txt` / `chrome-focus.txt`), `hover_host.py`, `tpl-*.md` and `movers-*.md` for the five PRs.
- Sites tonight: linkedin has a 5-script page (1.55%), 2.34%, 2.64%, 2.96% and 3.43% variants and the 7-script other layout (41%), each seen on more than one binary; google 12, 13 or 14 scripts; shopify's 3.00% variant came up in every run; bing has a 0.24% variant; walmart 8.84%, 20.6 to 20.8% odd frames; yahoo one 23.95% frame; youtube, cnn, weather, github, instagram and netflix captures flip over the script budget with identical frames. An arm split in one run (both A identical, both B identical, cross pairs different) happened three times tonight and was the server each time; the swapped re-run is what tells.
- z-d0 is parked detached at 1230b470. z-i0 is on `atlas/z-click-common-ancestor` at 0cb85978, with one untracked probe script under `tools/parity_oracle/`.
- Banked binaries (new): `pc-dev-1230b47`, `pc-hover-33d67fe`, `pc-hover-0a27a7c`, `pc-fpress-1f50e75`, `pc-clickanc-b871ea6`, `pc-clickanc-0cb8597`.
