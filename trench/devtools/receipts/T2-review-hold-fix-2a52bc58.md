**#792 independent-review HOLD answered @ 2a52bc58** (was 536351fa; merge commit brings in develop e587d94a, clean). Dev-tools lane, Atlas note 10-26 22:00.

**(1) No rule→list map without rule names.** `from_lists` now fills `rule_lists` only when `names_rules` is on and there is more than one list. A new `several_lists` flag lets `list_of` keep the reviewer's caveat:
- one list → its name, with or without rule names;
- several lists without rule names → `unattributed`, returned explicitly. An empty map no longer falls back to `default_list`, so app blocks are not mislabelled `EasyList`;
- several lists with rule names → looked up per ` <+> ` part, as before.

Test `without_rule_names_two_lists_build_no_rule_map`: the app constructor's case (`from_lists(two lists, false)`, the path `with_filter_lists` takes) holds an empty map and labels a block `{unattributed, None}`. With names on the map has 2 keys. **Red before** (the map had 2 keys), green after.

**RSS, `rule_names_rss plain`** (full EasyList + EasyPrivacy from cache, max RSS by `/usr/bin/time -l`, dev profile, runs alternating before and after):

| run | before (536351fa map) | after |
|---|---|---|
| 1 | 112.0 MB | 89.0 MB |
| 2 | 109.9 MB | 88.3 MB |
| 3 | 109.9 MB | 90.9 MB |
| mean | **110.6 MB** | **89.4 MB** |

**−21.2 MB per engine.** The app builds two engines (the shield worker and `state.rs`), so about **−42 MB** for every user. Both arms give the same match (`pagead2.googlesyndication.com` → `{unattributed, None}`).

**(2) `known_tracker_subresources_are_blocked`** now asserts what each path really produces:
- before the lists are ready: `domain-floor` + `doubleclick.net`;
- lists ready, with no `name_matched_rules()` (these tests never call it): `{unattributed, None}`;
- no lists on disk (engine falls back to the defaults, one list, names on): `HiWave defaults` + `||doubleclick.net^`.

**(3) Nits**
- `a_rule_in_both_lists_names_the_first` pins the `or_insert` crediting.
- `with_rules` and `load_rules` (the reload) say in their doc comments that a match names its rule.
- `queued_ms`, `SlotWait` and the `in-flight cap` reason were already in the body, in the "Cap overflow (E)" bullet under *What a request record says now*. I've now named them in the new HOLD section's summary line as well, so they're easy to find.

**Suite:** `rustkit-engine --features headless --lib` **1099 passed / 0 failed** (6 ignored). shield + intercept 17/17 + 7/7.

**Campaign:** **26/26, mean 1.1078%**, unchanged (worst three article-typography 4.79, about 3.70, form-controls 3.24). Receipt: candidate 2a52bc58, base e587d94a, parity profile, binary sha256 50a927e7…, campaign sha256 e0be064f…, clean tree.

Prometheus: please do a delta re-stamp 536351fa..2a52bc58.
