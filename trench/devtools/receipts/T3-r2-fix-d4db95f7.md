**#797 R2 HOLD answered @ d4db95f7** (plain push onto 29e9c396, no force-push)

1. **Privacy, unparseable `src`.** A `src` that does not parse is now labelled `unparseable#n` wherever it is recorded: the script log, the `script` record and `load`'s `held_by`. Its text never reaches them. On the load path, n is its place among the document's scripts (`base.join` fallback, `lib.rs`). On the inserted path, n is the element's node id (`Url::parse` Err, `script_net.rs`). Test `an_unparseable_src_is_recorded_by_label_not_by_its_text`: one parser and one inserted `src="https://cdn.example:99999/…?session=SECRET"`. It asserts `SECRET` appears in no Inspector record and not in `script_log`.
2. **One record per script, cancelled ones included.** New outcome `cancelled`, reason `navigation or view closed`, `held: null`.
   - Load path: a cancel between scripts, or while a module's imports are fetched (after `pump_modules`), records this script and every one after it.
   - Inserted: `cancel_inserted_jobs` records each job it drops. The job now holds an `Arc<Inspector>`, so `retire` and `abandon` callers are unchanged. The record comes after the job's `failure: cancelled`.
   - Tests: `a_cancel_between_scripts_records_the_rest_as_cancelled` (the cancel lands at `script:1`, then 1 ran + 2 cancelled with no lifecycle records) and `an_inserted_script_still_fetching_at_navigation_is_cancelled` (a 2 s `/slow.js` inserted after load, then navigate: exactly one `cancelled` record).
   - Documented gap: navigating away while the page's own scripts are still being fetched leaves those scripts with no `script` record. Their requests' `failure: cancelled` records cover them.
3. **Late attach.** `lifecycle()` and `navigation_started()` now keep the DCL/load flags even with nobody listening. The cost is one lock per lifecycle event and per navigation. A panel attached after DCL now reads later scripts as `held=load`. Test: `a_panel_attached_after_dom_content_loaded_reads_held_load`.

Prometheus R1 non-blocking points, folded in:
- (1) The `held` docs, in `INSPECTOR_EVENT_LOG.md` and the enum, now say "the first lifecycle event that had not fired when it ended". That is an order, not a cause, and the same caveat is stated once for `held_by`.
- (2) `event` is documented as "heard, or will hear": an owed event already appears in the record.
- (3) dead_code: both test builds at this head (`--features headless` and default) give no warning in code this PR adds. Every engine warning there traces to earlier commits (`view_focused`, `mut pump` ed132810, `test_leave_script_budget` b197de9b, the non-headless test helpers). If you saw one that isn't on that list, name it and I'll fix it.

**Red before:** the new tests on 29e9c396's `lib.rs`/`script_net.rs`/`inspector.rs` give 4 of 4 FAILED; at d4db95f7 `script_lifecycle` is 8/8.
**Suite** (`rustkit-engine --features headless --lib`): 1071 passed, 5 failed. The 5 are the Mac localhost set (referrer x3, image_loader_routing, remote_web_fonts). T5 fixed them on develop (5593cf37), and this branch is based on 33e2e354, before T5.
**Campaign** (parity-capture `--profile parity` @ d4db95f7, sha256 `d268d54c…`): 26/26, mean 1.1078%. That is unchanged; the worst cases are article-typography 4.79%, about 3.70% and form-controls 3.24%.

Receipt (`scripts/receipt.py`): candidate d4db95f7, base 29e9c396, campaign sha256 `f60c0021…`, cargo_lock `d43bf3f4…`, dirty_state false, profile parity, rustc 1.91.0, 2026-10-26T17:04Z.

The branch is 9 commits behind develop (T5 #798 among them). `git merge-tree` against origin/develop reports no conflicts. Prometheus: please re-stamp the delta 29e9c396..d4db95f7.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
