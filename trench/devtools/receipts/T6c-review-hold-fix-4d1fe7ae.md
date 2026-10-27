**Independent review HOLD + Prometheus nits answered @ 4d1fe7ae** (plain push on `atlas/dt-t6c`, no develop merge needed: the PR was CLEAN).

1. **HIGH, lost expand: fixed.** Live questions now coalesce per *slot*. The slot is the kind, except `Subtree`, whose slot is the expanded node. Expanding A, B and C asks all three. Expanding the same node twice while it is out is still one question. Test: `expanding_two_nodes_while_one_expand_is_out_asks_both`.
2. **MEDIUM, a page that is always slow: fixed.** A late answer is dropped only when a newer question for its slot was wanted meanwhile (for a hover, a newer pointer position), and then that newer question is asked. When nothing newer is waiting, the late answer is shown, because a late answer beats none. Test: `a_page_that_always_answers_late_still_shows_its_answers` (late at 2.1 s, answered at 2.5 s: tree and element shown, nothing asked again, busy clears).
3. **LOW, stale hover outline: fixed.** A late hover whose `hover_next` is `Some(None)` (the pointer left the view) is shown as `Node(None)`. `answered` then calls `hovered_now(None)`, which clears the outline and the row mark. Test: `a_late_hover_after_the_pointer_left_clears_the_outline`.
4. **Clearing on navigation and close.** I pulled the two paths out as `forget_page()` (navigation) and `forget_questions()` (close), with no behaviour change, and added a test. After a navigation, the old page's late tree answer is not shown, nothing is asked again, busy clears, and the console read is kept. Close empties `asked`, `again` and the busy state. Test: `a_navigation_forgets_live_questions_and_a_close_forgets_all`.

**Prometheus nits**
- (a) Newer questions parked behind a late one: item 2 covers any page that eventually answers. The late answer is shown, or replaced by the parked newer question, and the slot frees. On a page that **never** answers they stay parked, and the busy line says why. The `take_page_answers` doc comment now says so.
- (b) `#page-busy` greyed: this was not happening. In inspector.html, the JS variable `domTreeContainer` is `document.getElementById('dom-tree')` (L941), not `#dom-tree-container`. `#dom-tree` is a *sibling* of `#page-busy`, so `setPageBusy` greys only the tree. I added a comment there instead of moving the element.
- Hover: covered by item 3.

**Red before.** I restored the old behaviour for each item in one mutation run: Subtree slot = kind, late answers always dropped and asked again, `Some(None)` dropped. Result: 4 of 9 panel tests failed (the three new tests, plus the updated first test, which now expects the late element to be shown).

**Results.** `cargo test -p hiwave-app --bin hiwave` passed 64 with 0 failures (60 before plus 4 new). No campaign: the change is confined to `hiwave-app` (`devtools_panel.rs` plus a comment in `inspector.html`), and parity-capture does not link hiwave-app.
