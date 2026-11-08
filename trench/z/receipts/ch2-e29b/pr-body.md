## CH2.E29b: an invalid keyword or number is not in the block

Z plan row **CH2.E29b** (from #977's review): `getComputedStyle` read an invalid inline keyword back as the author's text (`object-fit:bogus` read `bogus`), and the cascade accepted a custom property holding a bad url.

Branch `atlas/z-ch2-e29b-inline-invalid`, base develop **a8e7e28b**. Red first: **1e3fe459** (test only). Fix: **c8eeec4b**. Test split: **cd9a5edb**. Head **f8f04b11** = develop **c7209173** merged in.

**Merge note:** develop's CH2.E14b (#968) and this row edit the same two cascade call sites (sheet and pseudo passes). The resolution keeps both: this row's keyword check runs first, then E14b's `resolve_css_variables_or_invalid`, so an unresolvable `var()` still computes as `unset`.

### What changes
- **Which values are judged.** A value that is one word a keyword-only property does not take is invalid. The tables cover 41 properties with Chromium 148's word lists (`tools/parity_oracle/keyword_grammar_log.mjs`). A `flex-grow`/`flex-shrink` value that is not a non-negative `<number>` is invalid too: `1.`, `-1` and `1px` are rejected, while `.5`, `+2` and `1e1` are kept.
  - Only a lone identifier is judged. Two words, a function or `var()` are left as before.
  - So a word missing from a table can keep an invalid value, but it can never drop a valid one.
- **`el.style`** leaves an invalid declaration out: `length`, `getPropertyValue`, and `setProperty` (which becomes a no-op). `getComputedStyle` then reads the cascaded value, not the author's text. Accepted keywords serialise in lower case and plain numbers in shortest form, as in Chromium.
- **The cascade** drops the same declarations through `rustkit_css::keyword_grammar::invalid_value`, in the sheet, inline and pseudo passes.
  - Before this, the property arms reset the property to its default. So `position: middle` in a style attribute wiped a sheet's `relative`, and `flex-direction: down` wiped `column`. This was a layout bug, not only a read bug.
- **Custom properties:** an inline custom property holding a bad url is dropped (`rustkit_css::mask::has_bad_url`, the same rule as the bindings' `hasBadUrl`).
- **No CSS-wide text in reads:** the text of `inherit`/`initial`/`unset` is never used in place of a missing computed row.
- **Table sync:** a bindings test (`style_keyword_table_matches_the_cascade`) holds the JS table to the Rust one. It tries every word in the tables on every property.

### Before → after (Chromium 148.0.7778.216 pins, `style_attr_declaration_cases.json`)
- Develop: **11 wrong** (10 new cases plus the E29 gap case). Candidate: **0 wrong**.
- Three disclosed gaps remain. Each one asserts its last field and is outside this row:
  1. The engine publishes no computed row for many initial values (`table-layout: auto`, `direction: ltr`, …; C9's property list), and it reads `text-align: left` where Chromium reads `start`.
  2. The engine's arms match `position`/`overflow-x` keywords case-sensitively and have no `-webkit-center`.
  3. There is no `initial`/`unset` for most properties, and no `inherit` for `position`.
- For each of the three, `el.style` matches Chromium in full.

### Gates
- **Receipt fields:** base a8e7e28b, candidate c8eeec4b (red 1e3fe459), profile `parity`, toolchain rustc 1.91.0 (f8297e351 2025-10-28), host macOS 26.5.2 arm64, Chromium oracle 148.0.7778.216 (pinned Chrome for Testing). Parity binaries: base sha256 `0eacf266af71f57a55ef8c662f5e4026278d3fbad1ff048c5c5bafaddc0204bf`, candidate sha256 `58cc67fe0baa32adf2789819e5f4ccd859f3e03f8e2db69a3b8e36c879739696`. Fixture: `tools/parity_oracle/style_attr_declaration_cases.json` (41 cases). Raw logs are in hub `trench/z/receipts/ch2-e29b/`.
- **Campaign:** 26 cases at the candidate, **0 moved** against base.
- **All-site A/B** (20 sites, A,B,A,B): **no movers.**
  - 17 sites are 0.00% within and across. cnn fails on both arms (timeouts), as it did in B18b's run.
  - **google** 1.53% is a served page variant: a chip row ("Create images / Ask about files / Brainstorm") instead of two buttons. The base binary alone shows the same split (2 of 4 loads), and the candidate alone showed 0.00% on 4 loads.
  - **linkedin** 76.8% is a served variant with 18 vs 6 script records. In the rerun it appears in the A arm.
- **Crate suites:**
  - rustkit-css 124/0.
  - rustkit-layout 909/0.
  - rustkit-bindings 483/0, which includes the new `style_keyword_table_matches_the_cascade`. That test takes over 60 s in a debug build.
  - Engine `style_attr_declaration` 4/4 on one thread. At default threads, the 41-case test holds the GPU for about 130 s at load 18, so its neighbours can hit the GPU-guard wait.
- **The 41-case test is now four tests** (`style_attribute_declarations_read_as_chromium_N_of_4`, every fourth case, as `grid_in_flex_tests` does). As one test it held the GPU for about 130 s at load 18, past the 120 s GPU test guard. All four pass at f8f04b11 (43 s at 2 threads).
- **Engine headless suite at f8f04b11 (complete):** 2114 tests: **2055 ok, 33 ignored, 25 FAILED** at default threads, load 5 to 22 with other seats' suites running. 22 of the 25 are GPU-guard waits, mostly queued behind `computed_read_tests::r1_cases`, which passes. One test, `test_gpu::tests::a_holder_past_the_limit_fails_the_waiter_by_name`, printed no result line.
  - **Rerun on one thread:** 24 of those 26 pass (`rerun-f8f04b11-1t.log`).
  - **The 2 left are wall-clock asserts in `page_script_tests`:** `a_stalled_subresource_is_dropped_at_the_subresource_budget` (3.5 s against a 2.5 s bound; that bound is CH2.E30) and `scripts_are_fetched_while_the_subresources_load` (5.3 s).
  - **Develop c7209173 fails them the same way at that load.** A one-thread A/B/A/B at load 20–22 gave develop 3.12/3.35 s and 5.16/5.28 s, against the candidate's 3.22/3.36 s and 5.49/5.38 s (`timing-ab.log`). This row does not touch fetch.
- The campaign and A/B above ran at c8eeec4b. Since then the head has added only the test split and develop's batch-38 tree, which batch 38 already gated.


🤖 Generated with [Claude Code](https://claude.com/claude-code)
