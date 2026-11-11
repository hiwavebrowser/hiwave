# HiWave branch ledger, 2026-11-10 (Atlas cleanup)

Pete's order: keep master/main, develop, gh-pages, open-PR heads (and bases), atlas/trench-realsite (OPS1); everything else off the remote. Live re-scan 2026-11-10 ~21:00 ET with blobless clones; `git cherry origin/develop` + ancestor checks, PR state from `gh`, supersession by merged PR titles/commit subjects/files on develop.

Classes: KEEP; RECENT (last commit <6h, left alone); A fully contained (deleted, no tag); S unique patches but landed in another form (tag `archive/<b>` then delete); U unlanded (tag `archive/<b>` then delete). Tags keep every commit reachable: `git fetch origin refs/tags/archive/<b>`.

Judgement call: `metrics-history` is KEPT in all three repos although not in the order's KEEP list: the metrics workflow on develop checks it out and pushes rows to it, so deleting it would break CI history appends.

## hiwave-macos (63 branches)

| branch | tip sha | last commit | class | PR(s) and state | archive tag | note |
|---|---|---|---|---|---|---|
| `athena/cb3-button-line-height` | `7ff824e16b8e5697ab715d263f6aeeebeb455360` | 2026-11-10 16:07 | KEEP | #1037 OPEN base=develop | - | head of open #1037 |
| `athena/cb3c-button-widths` | `8d90f8bb61de8884232a89dd7c507c13058238f0` | 2026-11-10 20:45 | KEEP | #1061 OPEN base=athena/cb3-button-line-height | - | head of open #1061 (base athena/cb3-button-line-height) |
| `atlas/trench-realsite` | `7618c1a49fd0d0c9fd9ce9f258ea237b33f8b7fb` | 2026-11-05 13:21 | KEEP | - | - | live realsite data branch (row OPS1) |
| `atlas/z-ch2-e20-inserted-link` | `1088cbc4c56cb277f4ce3a54543f224ec017caa6` | 2026-11-10 14:14 | KEEP | #984 OPEN base=develop | - | head of open #984 |
| `coverage/auto-develop-nov10` | `384636e1c2160267d46acf1aabe10803f244f296` | 2026-11-10 16:19 | KEEP | #1049 OPEN base=develop | - | head of open #1049 |
| `develop` | `d8c9e8b2f44c1ddf936dfa6065eb39d3af10a9ab` | 2026-11-10 20:54 | KEEP | #794 MERGED base=master; #660 MERGED base=master; #439 MERGED base=master; #248 MERGED base=master; #190 MERGED base=master; #110 MERGED base=master; #104 MERGED base=master; #98 MERGED base=master | - | protected branch |
| `feat/inc5-incremental-layout-stage1` | `ae69762e542e5dbf23175d9cbbc1aca7135bc485` | 2026-11-10 17:25 | KEEP | #1063 OPEN base=develop | - | head of open #1063 |
| `lat20-hover-layout-scope` | `a7ba8764be806bbe3fbe377f14be7fca1042ed91` | 2026-11-10 16:59 | KEEP | #1062 OPEN base=develop | - | head of open #1062 |
| `lay1-flex-aspect-ratio` | `4995d259e93c85a5db58cfe6b73741b3a523c9e5` | 2026-11-10 11:50 | KEEP | #1043 OPEN base=develop | - | head of open #1043 |
| `master` | `200cb6031cd78022851a749951d8c40e67c6003f` | 2026-10-23 21:07 | KEEP | - | - | protected branch |
| `metrics-history` | `5dc2f55efe5a6a42c2a07e0ead3910cc1c1c393c` | 2026-11-02 12:18 | KEEP | - | - | CI data branch: metrics workflow on develop checks out and pushes it |
| `rescue/c8b` | `afb50e7a16c4facb7220a1e7e679e6f042387df8` | 2026-11-10 14:48 | KEEP | #1052 OPEN base=develop | - | head of open #1052 |
| `rescue/ch2-b19` | `7f802f83b97f040edc1809a14b62ef583fbe6cc1` | 2026-11-10 14:12 | KEEP | #1051 OPEN base=develop | - | head of open #1051 |
| `rescue/ch2-b25b` | `e087a660cc9a16b82d9749bfd8294e0a944b76c9` | 2026-11-10 14:49 | KEEP | #1055 OPEN base=develop | - | head of open #1055 |
| `talos/js2-sort-panic` | `22accfd29e02d3cef02181b80ccdbfe08cc90a96` | 2026-11-10 20:35 | KEEP | #1060 OPEN base=develop | - | head of open #1060 |
| `feat/inc5-incremental-layout-stage2` | `a900dedf11c6e10ce8195d020f1a48124fa96862` | 2026-11-10 18:07 | RECENT | - | - | last commit <6h old; left alone |
| `atlas/dt-t6c-followups` | `cacf5917f8618e0fc75c5e6890e826f1d4f101f0` | 2026-10-27 13:39 | A | - | - | no + lines in git cherry vs develop |
| `atlas/z-board-r2` | `921526e7767d8d7b26eb664f4c2d805adb7123bd` | 2026-11-08 01:50 | A | - | - | ancestor of develop |
| `atlas/z-ch2-b17b-control-min-max` | `919de38fb5845db9424769b70bc6a7a69fb8e9e3` | 2026-11-08 17:15 | A | #985 CLOSED base=develop | - | no + lines in git cherry vs develop; CH2.B17b text-control min/max; all 6 commit subjects now on develop via #1050 |
| `atlas/z-ch2-b4-gcs-null` | `599b5f939a828099d615dd32cefc5eb4f602978d` | 2026-11-05 03:13 | A | - | - | no + lines in git cherry vs develop |
| `atlas/z-forced-layout` | `f3d9320a92c941e9a9d6f0c5e5ebce4fecb915ee` | 2026-10-26 21:51 | A | - | - | no + lines in git cherry vs develop |
| `batch/20` | `d4831187452f65cfab0d2ee0c741177a2c5c8d8e` | 2026-11-05 06:29 | A | - | - | no + lines in git cherry vs develop |
| `talos/js1-pin-50m` | `e787e7c0095cfb058fe2bd72d05b3408bd8e7ac5` | 2026-11-10 13:03 | A | - | - | ancestor of develop; JS1 follow-up pins under the 5 s turn budget (check cherry) |
| `athena/e54b-srcset` | `20e1cfb72a2561bb99544d93fecd9823d72776e3` | 2026-11-10 04:51 | S | #1036 CLOSED base=develop | `archive/athena/e54b-srcset` | E54b first cut (closed #1036); image_source.rs landed via #1039; only the probe tools/parity_oracle/srcset_probe.mjs is not on develop Superseded by #1039. |
| `atlas/z-ch2-e30-budget-bound` | `45506a4fdf30990c5ce15ae10725125af66c105d` | 2026-11-07 19:46 | S | - | `archive/atlas/z-ch2-e30-budget-bound` | Subresource-budget bound test room; develop 8a822286 (#1044) re-bounded the same test Superseded by #1044. |
| `atlas/z-ht27-triage` | `fb0097ae7963cf3f024f5d896fa67b4e96d484e8` | 2026-10-28 03:31 | S | - | `archive/atlas/z-ht27-triage` | HT27 red tests; all subjects on develop via the HT27 PR series Superseded by #818 #821-#824 #830. |
| `atlas/z-matchmedia` | `6d471bd16252783980d6a950a8483b7253e4ee6c` | 2026-10-28 10:13 | S | - | `archive/atlas/z-matchmedia` | matchMedia + getComputedStyle content; landed as #818 and #821 Superseded by #818 #821. |
| `atlas/z-page-handle` | `d7a96cdd9d5bfb3420144d9279793d5d9ce27b3e` | 2026-10-16 04:05 | S | - | `archive/atlas/z-page-handle` | M4 PR1 PageHandle protocol (closed #723); superseded by #730 one content thread (medium confidence) Superseded by #730. |
| `athena/cb2-canvas-container-size` | `4100735f62dbad10f9ca44f793f69f728c70a1b8` | 2026-11-09 22:53 | U | - | `archive/athena/cb2-canvas-container-size` | Regression pin for CH2.E10b canvas-in-container sizing (bug not reproduced); never PR'd |
| `athena/lat15b-fragment-click` | `497c89d515d17debcdaad6a67b48c02976303366` | 2026-11-10 00:53 | U | - | `archive/athena/lat15b-fragment-click` | Regression pin for same-page #fragment click during load (LAT15b, not reproduced); never PR'd |
| `atlas/board-receipt-022aa2fa` | `4488ebbca46a6bac8cfc60fa104ad67cc4cc22e3` | 2026-11-08 14:01 | U | - | `archive/atlas/board-receipt-022aa2fa` | Chrome-board receipt at develop 022aa2fa (trench/chrome BOARD.md/json) |
| `atlas/config-receipt-lanes-pause-20261108` | `b8cae9a7ef3878c3d4f003ee5c414add7859d18b` | 2026-11-08 12:35 | U | - | `archive/atlas/config-receipt-lanes-pause-20261108` | Config receipt: macOS trench lanes paused 2026-11-08 (plist, launchctl) |
| `atlas/dt-t16-save-html` | `71e24daeb4fdbcec14aabdd0bbeedbd62218e68e` | 2026-11-05 18:55 | U | - | `archive/atlas/dt-t16-save-html` | T16 parity-capture --save-html (not on develop) |
| `atlas/dt-t17-script-nav` | `010be0891e0e45818c37d7b60ad0323fa761675e` | 2026-11-06 00:57 | U | - | `archive/atlas/dt-t17-script-nav` | T17 parity-capture follows one script navigation |
| `atlas/dt-t18-replay-proxy` | `ca4cbaa435aedc252b402e8d7bf5932e6e5a500d` | 2026-11-06 06:42 | U | - | `archive/atlas/dt-t18-replay-proxy` | T18 hiwave --replay-proxy replays a HAR in the real window (not on develop) |
| `atlas/dt-t20-budget-stop-rows` | `2e01dbcbfa23629fce3984958004c0188a0b3cea` | 2026-11-05 06:57 | U | - | `archive/atlas/dt-t20-budget-stop-rows` | T20 inspector console folds repeated budget stops into one row |
| `atlas/dt-t21-file-timers` | `946bf0cf921d0f380858c5723ffeb480862f1bbf` | 2026-11-05 12:44 | U | - | `archive/atlas/dt-t21-file-timers` | T21 --html-file with --live-ms turns the live loop |
| `atlas/dt-t23-r1-split` | `9060ae101dd8212d934246581f38e9f71546bf03` | 2026-11-06 19:25 | U | - | `archive/atlas/dt-t23-r1-split` | T23 r1_cases split into 16 parts (may be overtaken by T41/T41b test-speed work) |
| `atlas/dt-t26-record` | `36958b441a680558d457c49609a68afea2da3f8c` | 2026-11-07 00:43 | U | - | `archive/atlas/dt-t26-record` | T26 real_window driver.py --record screen-records the pass |
| `atlas/z-729-merge-wip` | `cf503bb1c06f81a50727e6975350e89836efd6ac` | 2026-10-20 16:01 | U | - | `archive/atlas/z-729-merge-wip` | Merge-WIP stack of closed #727-#737 (load tail, HAR replay, adopted sheets); pieces re-cut later, not line-verified |
| `atlas/z-733-merge-wip` | `bc7a63f78e100137014891c24109abae84936d24` | 2026-10-21 03:57 | U | - | `archive/atlas/z-733-merge-wip` | Merge-WIP stack of closed #727-#737; not line-verified |
| `atlas/z-736-merge-wip` | `040704608e2816adce7e805e06761a49ce0b2abb` | 2026-10-21 21:10 | U | - | `archive/atlas/z-736-merge-wip` | Merge-WIP stack of closed #727-#737 (48 unique patches); not line-verified |
| `atlas/z-c8b-path-clip` | `872056842b90fad8dd58ab4d0fdfa7f90db7913e` | 2026-11-07 22:26 | U | - | `archive/atlas/z-c8b-path-clip` | C8b clip-path polygon/path/shape; work carried by open rescue PR #1052 (not landed yet) |
| `atlas/z-ch2-b19-justify-unsafe` | `75a47bcd5747c29c114da7492b37bc383f7bf3a8` | 2026-11-06 00:25 | U | #935 CLOSED base=develop | `archive/atlas/z-ch2-b19-justify-unsafe` | CH2.B19 unsafe justify of overflowing flex line (closed #935); carried by open rescue PR #1051 |
| `atlas/z-ch2-b25b-inline-abspos` | `506415911dcb07f8f598e5005351bd7a4a81184d` | 2026-11-08 09:16 | U | - | `archive/atlas/z-ch2-b25b-inline-abspos` | CH2.B25b inline abspos static position; carried by open rescue PR #1055 |
| `atlas/z-ch2-b5-select-value` | `9ffe60085eb0464296e7008d283f833a4a828a16` | 2026-11-05 06:40 | U | - | `archive/atlas/z-ch2-b5-select-value` | CH2.B5 pins: select value set from script is painted (test only) |
| `atlas/z-ch2-e29b-inline-invalid` | `f8f04b11b58b410bef8a476565fccb369bda75cd` | 2026-11-07 21:08 | U | - | `archive/atlas/z-ch2-e29b-inline-invalid` | CH2.E29b invalid inline keyword/number dropped from style block (css+bindings, oracle JSON) |
| `atlas/z-ch2-e34-textkey-publish` | `fb50002e82ae0ad3b15278874a9d1690f8ddbd54` | 2026-11-08 00:30 | U | - | `archive/atlas/z-ch2-e34-textkey-publish` | CH2.E34 page lays out and publishes after a field-editing key |
| `atlas/z-ch2-e37-enter-modifiers` | `655b554acdf2b6dcd6d917f90429e0200a8a06ee` | 2026-11-08 00:44 | U | - | `archive/atlas/z-ch2-e37-enter-modifiers` | CH2.E37 Enter keydown carries modifiers; textarea newline; oracle log |
| `atlas/z-ch2-e38-history-on-commit` | `0f83eb1b3911cf2c255f54dcfd5d88d1ec357147` | 2026-11-08 02:51 | U | - | `archive/atlas/z-ch2-e38-history-on-commit` | CH2.E38 history recorded on navigation commit, not request |
| `atlas/z-ch2-e42-empty-img-src` | `69848afd0a127a181d16dd710c0045f32132537c` | 2026-11-08 12:14 | U | - | `archive/atlas/z-ch2-e42-empty-img-src` | CH2.E42 empty <img> src requests nothing (red + fix + oracle) |
| `atlas/z-s9-google-header` | `783e4d38056bb02a50d329a56544a3ee6783a3e2` | 2026-11-04 21:47 | U | - | `archive/atlas/z-s9-google-header` | S9 percent-height base for grid items and inline boxes (google header); overlaps open #1043 LAY1 |
| `batch/17` | `69d2a03b2b31acb67d12b881702a1259bbed6461` | 2026-11-04 23:52 | U | - | `archive/batch/17` | Linux gate-runner batch scratch (BATCH.md + merges of landed PRs) |
| `batch/18` | `c4024da2db299967479a1d2f8486b5cbbe90674b` | 2026-11-05 00:36 | U | - | `archive/batch/18` | Linux gate-runner batch scratch |
| `batch/18b` | `cb057a7ac3c28896909b83a956b893ebd46fb710` | 2026-11-05 01:07 | U | - | `archive/batch/18b` | Linux gate-runner batch scratch |
| `batch/19` | `ef0b4e1fda034de8b23cf103ca70d2f350355aa2` | 2026-11-05 04:37 | U | - | `archive/batch/19` | Linux gate-runner batch scratch |
| `batch/19b` | `7214a634fa9ca3120870b325c0fd900ad1535891` | 2026-11-05 04:52 | U | - | `archive/batch/19b` | Linux gate-runner batch scratch |
| `cloud/c15-abspos-icb` | `201a5faca79076336feafd39bb84ba723f06fdec` | 2026-11-04 22:18 | U | #886 CLOSED base=develop | `archive/cloud/c15-abspos-icb` | C15 abspos with only static ancestors placed from ICB (closed WIP #886) |
| `cloud/history-replace-followups` | `ad3ca6a4ff2fbc48e278cae7a5c13421cc3bfe2e` | 2026-10-16 03:00 | U | - | `archive/cloud/history-replace-followups` | Reload/replace/same-URL navigations replace history entry; no PR found (medium) |
| `cursor/critical-bug-identification-33ac` | `0ea29043229ad1c0d7df123999e294e8d9296a19` | 2026-11-10 11:17 | U | #1042 CLOSED base=master | `archive/cursor/critical-bug-identification-33ac` | Cursor bot fix: drop harvested script navigation once newer load starts (#1042 closed unmerged, base master) |
| `reduce/ch2-e10b-canvas-container-size` | `0f2f79a90434d067e7fee9074069e692ef2de8f5` | 2026-11-10 09:52 | U | - | `archive/reduce/ch2-e10b-canvas-container-size` | Diagnostics: CH2.E10b reduced page + measurements |
| `reduce/settings-button-line-height` | `d36514209f26f01dafdb672bb1644fe45b90fa2f` | 2026-11-10 09:52 | U | - | `archive/reduce/settings-button-line-height` | Diagnostics: settings button line-height reduced page (CB3 evidence) |
| `talos/t41b-parallel-gpu-tests` | `0c46358d6105850d31fd37ed3efd4c726bad45c9` | 2026-11-10 08:04 | U | #1045 CLOSED base=develop | `archive/talos/t41b-parallel-gpu-tests` | T41b-2 GPU tests run in parallel (closed draft #1045); its base #1044 merged, this commit did not |

## hiwave-linux (21 branches)

| branch | tip sha | last commit | class | PR(s) and state | archive tag | note |
|---|---|---|---|---|---|---|
| `develop` | `becd24b4640ecdae0d79dd58413a36f562123178` | 2026-11-10 14:13 | KEEP | - | - | protected branch |
| `main` | `cbd5c73e0f533070cb2665b53726e2bbd964aab1` | 2026-01-09 22:48 | KEEP | - | - | protected branch |
| `master` | `5b47be7047f3a7dfc3a81554efa83b330d75ee5e` | 2026-10-06 10:22 | KEEP | - | - | protected branch |
| `metrics-history` | `3de74e41157345a00d77dc9cb6cf7db2255ec5b8` | 2026-10-06 14:28 | KEEP | - | - | CI data branch: metrics workflow on develop checks out and pushes it |
| `archive/linux-chrome-font-chains` | `a5a31c7956771641969bed6e1654c09b49980cc9` | 2026-10-02 09:09 | A | - | - | no + lines in git cherry vs develop |
| `archive/linux-control-hang` | `5b80bf9aa092aede7f047189f3818b75a938fa14` | 2026-10-02 10:51 | A | - | - | ancestor of develop |
| `archive/linux-css-content-escapes` | `d6be6022ff26992a9f7895b50d62b818f648c4b9` | 2026-09-30 21:53 | A | - | - | ancestor of develop |
| `archive/linux-paint-advances` | `f0ad47d232e962da1e1641b48a55f0af975b759d` | 2026-09-30 16:31 | A | - | - | ancestor of develop |
| `archive/linux-realsite` | `425cd7a7b522ce302926f8013b5c75c7fdf64cf8` | 2026-09-30 21:49 | A | - | - | ancestor of develop |
| `archive/linux-webfont-variations` | `224da1acf58002ea19d46704fe0d7d46d738c123` | 2026-09-30 21:49 | A | - | - | ancestor of develop |
| `archive/macos-sync-wave3` | `23067ddc63297a895a61ea581a83e1632189d5ca` | 2026-09-28 13:27 | A | - | - | ancestor of develop |
| `archive/macos-sync-wave6` | `f0d0be8cec297f121d97ecbd9630ec14716cd86f` | 2026-09-30 16:16 | A | - | - | ancestor of develop |
| `castor/l4-lat2-ignore` | `a6e355bcb19966c24d52726338b30f49d791c42f` | 2026-11-06 13:29 | A | #91 CLOSED base=develop | - | no + lines in git cherry vs develop |
| `castor/n3-sync-2026-10-29` | `401e377ea98a8beb1b8ba37efac2966fccf226e1` | 2026-10-29 15:58 | A | #85 MERGED base=develop | - | ancestor of develop |
| `castor/s2-sync-2026-10-29` | `87972513eee8fc08b7f47d4269144a83c5456139` | 2026-10-29 21:21 | A | #86 MERGED base=develop | - | ancestor of develop |
| `talos/linux-webfont-inspect` | `6c8f2ffb75ab71fd9bb5316aa5dfb386fc9534a1` | 2026-10-03 18:59 | A | #81 MERGED base=master | - | no + lines in git cherry vs develop |
| `talos/linux-window-fixes` | `ec976991ed069e8c3eb7584be37dfbcc4e5efb58` | 2026-11-06 16:19 | A | #93 MERGED base=develop | - | no + lines in git cherry vs develop |
| `talos/n2-sync-2026-10-15` | `7d0a71a99c9f12c362a68ba2b742514820e65f56` | 2026-10-15 11:14 | A | #84 CLOSED base=master | - | ancestor of develop |
| `archive/linux-integration-tip` | `fc58ba416adefc089fa19409f9c92735533b57f5` | 2026-10-02 09:10 | S | - | `archive/archive/linux-integration-tip` | macOS-sync wave 7 archive; 3 unique patches are merge-duplicates, superseded by syncs #85/#86 Superseded by #85 #86. |
| `renders` | `fbe3403560e04c5e348dcd208a3e27c0c3f56178` | 2026-10-05 10:25 | U | - | `archive/renders` | Per-case render frames (Linux N1, data) |
| `talos/z2t1-handshake-profile` | `911dc18567e02b107c4595a0ef75edb259c74642` | 2026-10-05 11:30 | U | #83 CLOSED base=master | `archive/talos/z2t1-handshake-profile` | Z2-T1 test-only TLS/h2 handshake probes (closed #83); measurement |

## hiwave-windows (21 branches)

| branch | tip sha | last commit | class | PR(s) and state | archive tag | note |
|---|---|---|---|---|---|---|
| `athena/url-for-log-char-safe` | `07fa7c696fe3845e99bc0d8bbada4ac6e0d25d21` | 2026-11-10 20:07 | KEEP | #155 OPEN base=develop | - | head of open #155 |
| `develop` | `6004215a2a585c4b8306b9b55a2b686e14925557` | 2026-11-10 18:51 | KEEP | #110 CLOSED base=master; #83 MERGED base=master | - | protected branch |
| `master` | `970dea926f6053ff50ce2c6c68f35ce9e07d06fa` | 2026-10-02 17:03 | KEEP | - | - | protected branch |
| `metrics-history` | `2e103a237a0ce8b013455361031aab17300ca639` | 2026-10-02 21:16 | KEEP | - | - | CI data branch: metrics workflow on develop checks out and pushes it |
| `archive/athena-render-integration` | `cebb2638b432200d6e0dd6fb23024f81d6af7602` | 2026-07-10 08:38 | A | - | - | no + lines in git cherry vs develop |
| `archive/athena-w-box-shadow-paint` | `219a33d3fdd4f69d4fb0692496ade1dc09a12ebf` | 2026-07-31 19:33 | A | - | - | no + lines in git cherry vs develop |
| `archive/athena-w-native-tabs` | `128cafef30a863bd7794fd26732918a6730c7e99` | 2026-08-05 22:16 | A | - | - | no + lines in git cherry vs develop |
| `archive/athena-w-wire-shadow-filter` | `263d7fbe2aa17b8aefab20f5f811dbe61f167973` | 2026-07-30 15:44 | A | - | - | no + lines in git cherry vs develop |
| `archive/athena-w-wire-transform` | `53bae46bfbae4f855be5451931cfc28696c0820f` | 2026-07-30 12:27 | A | - | - | no + lines in git cherry vs develop |
| `archive/feature-macos-rendering-fixes` | `5a0631c78c6996b1f906bb8cfbc2f7c09436a0ee` | 2026-01-06 21:44 | S | - | `archive/archive/feature-macos-rendering-fixes` | Jan sRGB double-gamma port + readme; sRGB gamma landed in #14 Superseded by #14. |
| `athena/native-restore-tabs` | `89710776178d6ba2132caf111da56d9b783ba4ea` | 2026-11-08 16:20 | S | - | `archive/athena/native-restore-tabs` | Reopen previous session tabs; re-cut and merged as #139 Superseded by #139. |
| `athena/native-shelf` | `7c0df27287f24a1427eb122d98c0936bd384d05e` | 2026-11-08 16:20 | S | - | `archive/athena/native-shelf` | Shelf get/add/restore; re-cut and merged as #142 + #146 Superseded by #142 #146. |
| `archive/athena-rescue-jan-wip` | `f9bdfc0a45f440e3a0f6a7b67562184fbe0a1739` | 2026-07-07 19:44 | U | - | `archive/archive/athena-rescue-jan-wip` | Jan renderer WIP (glyph.rs, lib.rs) saved 07-07; renderer since rewritten |
| `archive/phase-1-critical-bug-fixes` | `13ff1a99ea8a9e4b053668c224155d264e1a92a6` | 2026-01-16 10:55 | U | - | `archive/archive/phase-1-critical-bug-fixes` | Jan 2026 phase 1 LineHeight/flex/grid; mostly re-landed, not line-verified |
| `archive/phase-2-text-rendering` | `7ea091f1755e1e2c4a3dc746d9d544febe792b9f` | 2026-01-16 11:02 | U | - | `archive/archive/phase-2-text-rendering` | Jan 2026 phase 2 text-transform; not line-verified |
| `archive/phase-3-sticky-positioning` | `54700fa883a296be51ccc8ae986b8a0c5602300b` | 2026-01-16 11:08 | U | - | `archive/archive/phase-3-sticky-positioning` | Jan 2026 phase 3 sticky; not line-verified |
| `archive/phase-4-grid-phase-7` | `55e1fcf6b7db4521232bbcfc1fdbacc8ea1107dd` | 2026-01-16 13:11 | U | - | `archive/archive/phase-4-grid-phase-7` | Jan 2026 phase 4 grid; not line-verified |
| `archive/phase-5-hsl-repeating-gradients` | `c982b1596361946dd0d195a7749d19812cca88ed` | 2026-01-19 08:48 | U | - | `archive/archive/phase-5-hsl-repeating-gradients` | Jan 2026 phase 5 HSL/repeating gradients + DirectWrite ALIASED + file:// address bar (file:// not on develop) |
| `athena/evidence-139` | `23b42256e6d94243878e354880ebe8262c6887a9` | 2026-11-09 21:20 | U | - | `archive/athena/evidence-139` | Window captures for PR #139 ("not for merging") |
| `athena/native-ctrl-number` | `a96519ed345807b2c6617cd76639aca3817448fd` | 2026-11-08 16:21 | U | - | `archive/athena/native-ctrl-number` | Ctrl+1..9 count only visible tabs (fe5f9aa, shell_tabs::pick_visible); not on develop |
| `renders` | `a0fa3a4c27b31c676d683138869d3c04654f5899` | 2026-10-05 11:40 | U | - | `archive/renders` | Interactive parity-capture record frames (data) |

## Open PRs whose base is not develop/master

- macos #1061 `athena/cb3c-button-widths` -> base `athena/cb3-button-line-height` (head of open #1037). Base kept. Land #1037 first, then retarget #1061 to develop before the base branch is deleted.
- macos #1042 (base master) seen in the morning audit is now CLOSED unmerged; its branch is archived (U) here.

## Suspected duplicate / overlapping work (report only, nothing closed)

1. macos `atlas/z-s9-google-header` (U, S9) vs open #1043 `lay1-flex-aspect-ratio`: both change `crates/rustkit-layout/src/grid.rs` so a grid item's height becomes a definite percent base for its children (S9 783e4d38 "a grid item with a height is its children's percent base" vs LAY1 4995d259 "a percentage height under a stretched grid item stays definite"). Likely the same fix twice; review S9 against #1043 before reviving it.
2. macos #1063 `feat/inc5-incremental-layout-stage1` vs `feat/inc5-incremental-layout-stage2` (RECENT, no PR): stage1 is an ancestor of stage2 (stage2 = stage1 + 2 commits). Intentional stack, but stage2 must not be opened as an independent PR re-carrying stage1.
3. macos #1061 (CB3c widths) stacked on #1037 (CB3/CB3b heights): same files (rustkit-css lib.rs, rustkit-layout lib.rs). Stack, not duplicate; landing order matters.
4. macos `cursor/critical-bug-identification-33ac` (U, closed #1042) vs develop: develop already has "with the content thread, New Tab drops a script navigation the replaced page sent (#730 R1 NIT 4)". #1042 generalises it to URL-bar loads (webview_rustkit.rs, +96). Partial overlap; the URL-bar half may still be a real bug.
5. macos `cloud/c15-abspos-icb` (U, C15) vs open #1055 `rescue/ch2-b25b` and merged #983: all three place abspos static positions in rustkit-layout lib.rs (+182 in C15). Different triggers (only-static ancestors vs inline-level vs grid), but same function family; check C15 after #1055 lands.
6. macos `atlas/dt-t23-r1-split` (U) and `talos/t41b-parallel-gpu-tests` (U, closed #1045) vs merged #1038/#1044: all are engine-test wall-clock work. T23 likely overtaken; #1045's parallel phase is the only unlanded piece.
7. macos `atlas/z-ch2-e42-empty-img-src` (U) vs merged E54 #1019 and E54b #1039: same <img> source/load path in rustkit-engine. Check whether develop already requests nothing for an empty src before reviving.
8. macos `athena/e54b-srcset` (S) vs merged #1039: same row re-cut; only the srcset_probe.mjs tool is unique.
9. macos `atlas/z-729/733/736-merge-wip` (U) vs merged LAT15 #1006, LAT17 #1013, #786, HAR replay: old merge stacks whose pieces were re-cut; 48 unique patches on 736 not line-verified.
10. Cross-platform: windows #155 (url_for_log, follow-up to windows #153 content-IPC guard) has no macOS twin (`content_ipc_guard` absent on macOS develop); linux #135 analytics hardening (merged) is a similar content-page lockdown. Ports, not duplicates; no Windows/Linux open PR duplicates macOS develop.

## Executed 2026-11-10 ~21:15 ET

Each delete re-checked live first (tip unchanged, not an open-PR head/base, >=6h old); S/U tags verified on the remote at the tip before the branch was deleted. Nothing skipped.

| repo | branches at start of day / at ledger / after | deleted (A/S/U) | archive tags created |
|---|---|---|---|
| hiwave-macos | 73 / 63 / 16 | 47 (7/5/35) | 40 |
| hiwave-linux | 21 / 21 / 4 | 17 (14/1/2) | 3 |
| hiwave-windows | 21 / 21 / 4 | 17 (5/3/9) | 12 |

Left: macos = master, develop, metrics-history, atlas/trench-realsite, 11 open-PR heads, feat/inc5-incremental-layout-stage2 (RECENT). linux = main, master, develop, metrics-history. windows = master, develop, metrics-history, athena/url-for-log-char-safe (#155).
