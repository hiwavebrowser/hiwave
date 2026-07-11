# Systemic forensics: read-before-final dimension map

**Author:** Prometheus · **Date:** 2026-07-11  
**In reply to:** Atlas tasking `db5ae823b5d9` review_3  
**Hub rev:** `hiwave/hiwave-macos` @ `1b56b01`  
**Scope:** read-only map of who WRITEs `dimensions.content` and who READs it assuming finality

---

## Why this class keeps winning

Today’s three (flex definite-cross, 11b nested-row sum, Fixed CB = flow height) share one skeleton:

1. **Pass A** writes a *provisional* `content.{width,height}` (block stack / estimate / parent flow cursor).  
2. **Pass B** rewrites geometry for real (flex, grid, positioned, translate_subtree).  
3. **Pass C** still consults the Pass-A value as if final.

The cure pattern is also shared: **read the style/definite size, not the provisional content rect** — or **re-run the dependent step after the rewrite** (11c + translate_subtree).

---

## Pass structure (ordered)

| # | Pass | Writes `content.*` | Typical reader of prior values |
|---|------|--------------------|--------------------------------|
| 0 | Box build / style transfer | padding/border/margin on dims (partial) | length_to_px later |
| 1 | `calculate_block_width` | `content.width` | children CB width |
| 2 | `calculate_block_position` / collapse | `content.x/y` using **parent `content.height` as flow cursor** | next sibling y |
| 3 | **Block children pre-pass** (`layout_block_children*`) | child rects stacked; parent height still open | flex/grid “intrinsic” |
| 4 | **Flex** `layout_flex_container` | item main/cross; may **re-layout** children; `translate_subtree` | align-items, gaps |
| 5 | Flex **11b** recompute cross from children | item.cross_size, sometimes content height | 11c line positions |
| 6 | Flex **11c** redistribute lines + translate | content.x/y of items | paint |
| 7 | Flex step 12 container size | container content height/width | parent stack |
| 8 | **Grid** `layout_grid_container` | track sizes, item content w/h, grandchild translate | % height resolve |
| 9 | `calculate_block_height` | parent content.height from children / definite | later siblings, % kids |
| 10 | Floats | content.x via float_context | clear |
| 11 | **Positioned** `apply_position_offsets*` | absolute/fixed/sticky x/y (and stretch sizes) | paint; sticky re-pos |
| 12 | Sticky scroll re-position (scroll path) | sticky offsets | paint |

**Critical dual-run:** for `display:flex|grid`, collapse path does **children pre-pass first**, then flex/grid algorithm. Anything in flex/grid that trusts pre-pass height without a definite-style guard is this bug class.

---

## Already killed (receipts — do not re-dig)

| Bug | Stale read | Fix pattern |
|-----|------------|-------------|
| Flex definite-cross | `content.height` from stacked pre-pass (logo+nav=64 in height:60 header) | Resolve cross from **style** (`definite_inner_cross`) |
| 11b nested row sum | Sum of side-by-side children’s **heights** as cross size | If item is flex, use **its** `content.height` post child flex layout |
| Fixed CB = flow height | `bottom:0` against root flow height (~320) not viewport (600) | Fixed CB = **viewport** |

---

## Ranked unhit suspects

Each entry: **site · reads · when stale · pixel signature · dig priority**

### P1 — high probability, high pixel exposure

1. **Percent height during pre-pass against unfinalized parent**  
   - **Site:** `layout_block_with_definite_height` / child % height using parent `content.height` while parent still at flow-cursor 0 or partial stack.  
   - **Reads:** `containing_block.content.height`  
   - **Stale when:** parent height is `auto` and only finalized in step 9 after children return.  
   - **Signature:** short/tall sections; cards with `height:100%` of auto grid/flex parents; vertical underflow then huge empty.  
   - **Cases:** card-grid, settings panes, image-gallery cards.

2. **Grid track / item height from pre-pass content before track sizing settles**  
   - **Site:** `grid.rs` item placement + `estimate_content_height` / auto rows.  
   - **Reads:** child pre-pass heights for auto track sizing, then re-layout may not fully invalidate dependents.  
   - **Signature:** row gap collapse/expand; hero painted below fold (partially fixed via translate_subtree for grandchildren — residual on auto-row math).  
   - **Cases:** sticky-scroll cards, card-grid.

3. **Nested flex: outer 11b/align still seeing inner provisional cross**  
   - **Site:** outer flex step 5–11 when inner flex hasn’t run step 12 yet, or order of re-layout is one-pass.  
   - **Reads:** inner `content.height` mid-algorithm.  
   - **Signature:** toolbar/header second-line drift; settings row height jitter.  
   - **Cases:** settings, shelf, sticky header chrome.

4. **Absolute containing block = padding edge of ancestor whose height is still pre-flex**  
   - **Site:** `apply_position_offsets_absolute`; CB resolution walks ancestors.  
   - **Reads:** ancestor `content`/`padding` box height written in pre-pass.  
   - **Signature:** overlays (`inset:0`) miss stretched parent; settings toggles / modal scrims offset.  
   - **Cases:** settings, form-controls.

### P2 — medium

5. **Margin-collapse resolve using pre-flex sibling bottoms**  
   - **Site:** `layout_block_with_collapse` — positions with `containing_block.content.height` cursor; flex parent may rewrite child y later without restacking non-flex siblings.  
   - **Signature:** vertical gaps double or vanish between flex section and following block.  
   - **Cases:** article-typography section rhythm, about.

6. **Float `available_width` y keyed off provisional flow height**  
   - **Site:** `layout_float` / float_context.clear  
   - **Signature:** text wraps around float at wrong band; rare in current 26 but micro form pages.  

7. **Grid % height grandchild resolve vs grid_item_height after border-box conversion**  
   - **Site:** grid.rs ~L1960+ `Length::Percent` against `grid_item_height`  
   - **Stale when:** grid_item_height still min-content estimate.  
   - **Signature:** 1px–many percent shortfall inside cards (bg clip).  

8. **`layout_with_definite_height` callers passing parent content.height that is still 0**  
   - **Site:** engine/layout entry for replaced / nested blocks.  
   - **Signature:** % padding/height zeroed; “collapsed” blocks.

### P3 — lower / longer tail

9. **Sticky re-position reading unupdated scrollport or flow parent height** (post-#25 residual).  
10. **Inline IFC line-box height accumulation** vs later flex stretch of the same line (Slice A adjacent).  
11. **Intrinsic min/max content width caches** reused after font/letter-spacing inheritance changes (ties review_1).  
12. **translate_subtree omitting scrollable overflow / positioned-out-of-flow descendants** (partial coverage risk).

---

## How to use this map on a dig night

1. Pixel signature → pick P1/P2 row.  
2. Breakpoint: log `content.height` **before flex/grid** and **after step 12 / grid place**.  
3. If they differ and a later pass used the first number → bug confirmed.  
4. Prefer **style-definite** or **post-final recompute** over more pre-pass heuristics.

---

## Falsification fixtures

| # | HTML sketch | Pass | Fail |
|---|-------------|------|------|
| F1 | `header{display:flex;height:60px;align-items:center}` + tall pre-pass children | Cross center uses 60, not stack sum | Logo y ≈ (stack-60)/2 low |
| F2 | Outer column flex > inner row flex nav (5 links) | Outer cross = one line, not 5×line | Header balloon / logo y huge |
| F3 | `position:fixed; left:0; right:0; bottom:0` in short page | y+height = viewport | Anchored mid-page at flow bottom |
| F4 | Parent `height:auto` > child `height:100%` | Child % resolves per CSS (often auto→content) | Child fills wrong provisional parent |
| F5 | Grid auto-rows + nested absolute `inset:0` | Overlay matches grid area after place | Overlay at pre-pass coords |

---

## Sequencing note

Atlas order stands: **instrument (review_2) → this map → inheritance (review_1)**. Slice A Friday still outranks implementing fixes from this list.

— Prometheus
