#!/usr/bin/env python3
"""Atlas 11-01 10:58 C10 (1), (2): `held` under a filter, and a fixed box in an element scroller. Chromium 143, held_probe.mjs."""
P = "/Users/petecopeland/Repos/.worktrees/z-c2d-rework/crates/rustkit-engine/src/transform_rect_tests.rs"
s = open(P).read()
old = """/// The rect of a 100x50 box at (20,10) when this value follows `translate:7px`:"""
new = '''/// How far a window scroll of 500 moves a fixed box under a wrapper with this
/// style. Only the move: where layout places a fixed box under its containing
/// block is row C10 (m).
#[track_caller]
fn fixed_moves_by(wrapper: &str, want: &str) {
    let page = format!(
        "<!doctype html><style>body{{margin:0;height:3000px}}</style><div style=\\"height:100px\\"></div>\\
         <div id=w style=\\"width:200px;height:50px;{wrapper}\\">\\
         <div id=f style=\\"position:fixed;left:3px;top:4px;width:10px;height:10px\\"></div></div>"
    );
    check(
        &page,
        "var a = $('f').getBoundingClientRect().y; window.scrollTo(0, 500); String($('f').getBoundingClientRect().y - a)",
        want,
    );
}

/// A filter is a containing block for fixed boxes, so the page takes them along.
#[test]
fn a_filter_holds_a_fixed_box_to_the_page() {
    fixed_moves_by("filter:blur(1px)", "-500");
}

#[test]
fn what_is_no_containing_block_leaves_a_fixed_box_alone() {
    for wrapper in ["", "filter:none", "opacity:0.5", "isolation:isolate"] {
        fixed_moves_by(wrapper, "0");
    }
}

/// Neither the window's scroll nor the scroller's moves it.
#[test]
fn a_fixed_box_in_an_element_scroller_stays_put() {
    check(
        "<!doctype html><style>body{margin:0;height:3000px}</style>\\
         <div id=s style=\\"width:200px;height:100px;overflow:auto\\">\\
         <div id=f style=\\"position:fixed;left:3px;top:4px;width:10px;height:10px\\"><div id=k style=\\"height:5px\\"></div></div>\\
         <div style=\\"height:800px\\"></div></div>",
        "window.scrollTo(0, 500); $('s').scrollTop = 40; \\
         var r = function (i) { var b = $(i).getBoundingClientRect(); return b.x + ' ' + b.y; }; r('f') + ' | ' + r('k')",
        "3 4 | 3 4",
    );
}

/// The rect of a 100x50 box at (20,10) when this value follows `translate:7px`:'''
assert s.count(old) == 1
s = s.replace(old, new)
open(P, "w").write(s)
print("ok")
