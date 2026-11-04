**#871 batch 9 regression fixed (Z lane, 11-03 21:05 order).** Plain push, red first.

- `4a358056` test (red): two rows for the reduced encyclopedia infobox shape: a `float:right; display:table` figure holding a `display:block` link (1px border, 3px padding) holding `<img width=250 height=125>` with `max-width:100%; height:auto`, with and without a `display:table-caption`. At a7ec389b: figure 8 wide (60 with the caption); Chromium 143.0.7499.4: 258. Plus a plain table cell control (250x125, passes before and after).
- `e186b7bd` fix: the compressible-replaced min-content arm (css-sizing-3 §5.2.2) now runs only inside grid track sizing. `own_min_content_width` also answers table cells (`table.rs` cell_widths/measure_columns) and shrink-to-fit, where Chromium keeps the image width. A thread-local scope (`with_compressible_replaced_min`) turns the arm on at grid's three min-content call sites (`GridItem::get_width_contribution` auto minimum, `grid_columns_content_width`, the fit-content item width) and off again under a table. Every earlier #871 row still passes.

Skipped as KNOWN (wrong for reasons outside #871): the caption row's height/y (caption placed on top and left out of the table box, C10 (g)/(j); its width is right, 258), and a 100px-wide table cell where a percentage max-width scales the height= attribute (existing KNOWN group).

Tests at e186b7bd: replaced_ratio 36/36 vs Chromium; rustkit-layout 881/0 (13 ignored); engine headless lib (debug) 1536 passed / 1 failed / 19 ignored in 2294 s. The failure is `content_thread::tests::report_page_runs_inline_chart_js_and_its_dom_content_loaded_listener` (`content_thread.rs:554`, read `function,function,none`: DOMContentLoaded did not run inside the full suite). Rerun alone at load 3.3: passes in 1.55 s. The change is layout-only (a min-content arm), so I read this as the suite-load script-budget class, not this PR. Owed: that test in the batch gates.

Not re-run here (Atlas's batch gates): campaign, all-site A/B. The encyclopedia article is the A/B row to read.

R1 → Prometheus.
