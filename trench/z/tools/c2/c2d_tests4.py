#!/usr/bin/env python3
"""#851 finding 4 tests: a stuck sticky box and a fixed bar in paint order, Chromium 143 (c2d_r1_probe.mjs)."""
P = "/Users/petecopeland/Repos/.worktrees/z-c2d-rework/crates/rustkit-engine/src/sticky_scroll_tests.rs"
s = open(P).read()
s = s.rstrip("\n") + """

const BAR_STYLE: &str = "<!doctype html><style>body{margin:0;height:3000px}\\
    #bar{position:fixed;left:0;top:0;width:400px;height:40px}\\
    #sp{height:400px}#st{position:sticky;top:0;width:300px;height:30px}";

#[track_caller]
fn over_a_bar(extra_style: &str, body: &str, script: &str, want: &str) {
    check(&format!("{BAR_STYLE}{extra_style}</style><body>{body}</body>"), script, want);
}

const BAR_FIRST: &str = "<div id=bar></div><div id=sp></div><div id=st></div>";
const BAR_LAST: &str = "<div id=sp></div><div id=st></div><div id=bar></div>";

#[test]
fn a_stuck_box_later_in_the_tree_is_over_a_fixed_bar() {
    over_a_bar("", BAR_FIRST, "window.scrollTo(0, 500); hit(10, 10) + ' ' + hit(350, 10)", "st bar");
}

#[test]
fn a_higher_z_index_on_the_bar_keeps_it_on_top() {
    over_a_bar("#bar{z-index:5}", BAR_FIRST, "window.scrollTo(0, 500); hit(10, 10)", "bar");
}

#[test]
fn a_higher_z_index_on_the_stuck_box_puts_it_on_top_of_a_later_bar() {
    over_a_bar("#st{z-index:5}", BAR_LAST, "window.scrollTo(0, 500); hit(10, 10)", "st");
}

#[test]
fn a_bar_later_in_the_tree_is_over_a_stuck_box() {
    over_a_bar("", BAR_LAST, "window.scrollTo(0, 500); hit(10, 10)", "bar");
}

#[test]
fn a_child_of_the_stuck_box_is_hit_over_the_bar() {
    over_a_bar(
        "",
        "<div id=bar></div><div id=sp></div><div id=st><div id=kid style=\\"width:50px;height:10px\\"></div></div>",
        "window.scrollTo(0, 500); hit(10, 5) + ' ' + hit(10, 20)",
        "kid st",
    );
}

#[test]
fn a_sticky_box_not_yet_at_the_bar_changes_nothing() {
    over_a_bar("", BAR_FIRST, "hit(10, 10)", "bar");
}
"""
open(P, "w").write(s)
print("ok")
