**FL step (a), the context split (Pete's option 2), Z lane 2026-10-26 21:05-**

The map (Explore pass over rustkit-engine lib.rs at develop + `8ec85298`):
- The style+layout build is about 40 `&self` Engine methods. Only `relayout_uncounted`, `cache_inline_svgs` and `repaint_restyled` are `&mut`.
  - Entry: `build_layout_for_view`, `build_layout_from_document`.
  - Tree reuse: `reused_tree`, `snapshot_tree`, `refresh_image_sizes`, `img_natural_size`.
  - Sheets: `inline_sheets`, `sheets_fingerprint`, `shared_rule_index`, `build_rule_index`, `extract_css_variables`.
  - The box builder: `build_layout_from_parent_style_and_path`.
  - Cascade: `compute_style_for_element`, `apply_style_property`, etc.
  - Live lookups: `live_attributes`, `edit_value_in`, `checked_in`, `resolve_resource_url_in`, `view_viewport`.
  - Fonts: `install_web_fonts`, `web_font_count`.
- Engine fields the build touches:
  - `config.javascript_enabled` (it can change at runtime: `set_javascript_enabled`).
  - `presenter.host_bounds`, windowed views only.
  - `image_manager` and `font_loader` (both Arc).
  - `style_trace`, `building_view`, `building_focus` and `svg_cache`.
- ViewState fields it reads: document, headless_bounds/viewhost_id, external_stylesheets, focused_node, hover_chain, active_chain, edit_states, checked_states, url.
- ViewState fields it writes: sheet_cache, rule_reads, html_clips.
- `rustkit_layout` calls nothing back. Fonts come from the global webfont registry, and image/SVG sizes are written into the boxes during the build.
- Script runs with only shared borrows of the engine during `bindings.evaluate` (`execute_script`, the live paths). `run_page_scripts` / `run_html_load_scripts` / `complete_load_tail` take the bindings out of the view.

Steps, each green and byte-identical:
- **a1 (done):** `layout_ctx::LayoutCtx` behind `Rc`, holding style_trace, building_view, building_focus and svg_cache (now a RefCell). Read as `self.lctx.*`.
- **a2 (done):** `layout_ctx::ViewLayout` behind `Rc` in each view (`view.lay`), holding focused_node, the two chains, edit_states, checked_states, sheet_cache, rule_reads and html_clips.
- **a3 (next):** the build methods move to `impl LayoutCtx`.
  - LayoutCtx gains `javascript_enabled: Cell<bool>`, the two Arcs, and `building: RefCell<Option<BuildView>>` in place of building_view/focus.
  - `BuildView` = id, `Rc<ViewLayout>`, base url, viewport (headless bounds or the last laid size, so no presenter), and the external sheets `Rc`. The engine fills it at each build start.
  - `cache_inline_svgs` becomes `&self` (svg_cache is a RefCell now).
  - Then campaign 26/26 identical + 20-site A/B, and step (a) can be a PR.
- **(b):** bindings get a forced-layout hook called from `DomHost::ensure_geometry`, outside the dom_host borrow, when the DOM is dirty. The engine installs a closure with `Rc<LayoutCtx>` + `Rc<ViewLayout>` + the document that builds, lays out and publishes geometry, with no paint. Add a per-task count to the event log. Script value writes that are still pending need applying to edit_states first.

Alternative for Atlas (not taken; the ordered shape was followed): during `evaluate` the engine is only shared-borrowed. So a scoped thread-local `&Engine` (the `scoped-tls` crate, no `unsafe` in our code) would let the closure call the existing `&self` build directly, at about one session's cost. It is still engine re-entry, so it would need Pete's word.
