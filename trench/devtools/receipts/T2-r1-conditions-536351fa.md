# T2 (#792): Prometheus R1 conditions (a) and (b), plus develop merge

Head `atlas/dt-net-facts` @ 536351fa (was 22813653). develop 68f4c8e1 merged @ a3791247
(merge commit; one conflict, `docs/INSPECTOR_EVENT_LOG.md`, both sides kept: T2's
`queued_ms`/`blocked_by` columns and T3's `script`/`lifecycle` rows).

## (a) ` <+> ` rules
adblock-rust's optimizer joins plain pattern rules that share options and a token into one
filter whose text is the parts joined by ` <+> `. No list writes that text, so the lookup
missed and the match took the first list's name (`default_list`).

Now each part is looked up. The list is named only when every part is from it; otherwise
it is `unattributed` (any part may have matched). With one list loaded, that list is named.

Red-before test `a_joined_rule_names_a_list_only_when_all_its_parts_are_from_it`: with the
old lookup, an EasyPrivacy rule `/adbanner.js` joined with EasyList's `/adbanner.gif` was
labelled `EasyList`, and two joined EasyPrivacy rules were labelled `EasyList` too.

## (b) rule-name cost, gated on `--shield`
`AdBlocker::with_filter_lists()` builds the plain engine again.
`with_filter_lists_naming_rules()` keeps rule text. hiwave-shield-intercept's worker uses it only
after `name_matched_rules()`, which parity-capture `--shield` calls before the build. The
app's shields (intercept worker and `state.rs`) pay nothing. Without rule names, a block
has `rule: null` and the list is named only when a single list is loaded.

Max RSS of `examples/rule_names_rss.rs` (full EasyList + EasyPrivacy from cache, /usr/bin/time -l,
alternating runs):

| run | plain | names |
|---|---|---|
| 1 | 110.0 MB | 118.8 MB |
| 2 | 113.3 MB | 118.9 MB |
| 3 | 109.8 MB | 118.9 MB |
| mean | 111.0 MB | 118.9 MB |

**Rule names cost +7.9 MB.** The 10-24 parity-capture measurement was +9 MB. Same match on both arms:
`pagead2.googlesyndication.com` → plain `{list: unattributed, rule: null}`, names
`{list: EasyList, rule: ||pagead2.googlesyndication.com^}`.

Test `without_rule_names_a_match_names_no_rule` pins plain vs names for one and two lists.
