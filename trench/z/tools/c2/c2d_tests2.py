#!/usr/bin/env python3
"""The #851 R1 tests: re-pin the transform test, add the three transform cases, the sticky-in-fixed hit and the sticky-over-fixed hit."""
P = "/Users/petecopeland/Repos/.worktrees/z-c2d-rework/crates/rustkit-engine/src/sticky_scroll_tests.rs"
s = open(P).read()
old = """    // `getBoundingClientRect` leaves transforms out here (row C10), so these
    // are Chromium's values less the transform's 100.
    check(PAGE2, &format!("[{}].join(' ')", steps.join(", ")), "1100,400 1100,100 1100,10 1100,10 1100,-420");
"""
new = """    check(PAGE2, &format!("[{}].join(' ')", steps.join(", ")), "1100,500 1100,200 1100,110 1100,110 1100,-320");
"""
assert s.count(old) == 1
s = s.replace(old, new)
s = s.rstrip("\n") + """

/// Sticky boxes under transforms (`trench/z/tools/c2/c2d_r1_probe.mjs`).
const TRANSFORMS: &str = concat!(
    "<!doctype html><style>body{margin:0;height:3000px}.tall{height:600px}.gap{height:50px}",
    ".st{position:sticky;top:0;height:20px;width:50px}",
    "#a-s{position:absolute;left:0;top:0;width:200px;height:100px;overflow:auto;transform:translateX(10px)}",
    "#b-s{position:absolute;left:300px;top:0;width:200px;height:100px;overflow:auto}#b{transform:scale(2)}",
    "#d-s{position:absolute;left:0;top:200px;width:200px;height:100px;overflow:auto;transform:scale(2);transform-origin:0 0}",
    "#sp{height:400px}#c-tr{transform:translateY(50px);margin-left:600px;height:1000px}",
    "</style><body>",
    "<div id=a-s><div class=gap></div><div class=st id=a></div><div class=tall></div></div>",
    "<div id=b-s><div class=gap></div><div class=st id=b></div><div class=tall></div></div>",
    "<div id=d-s><div class=gap></div><div class=st id=d></div><div class=tall></div></div>",
    "<div id=sp></div><div id=c-tr><div class=st id=c></div></div></body>",
);

#[test]
fn it_sticks_in_a_transformed_scroller() {
    check(TRANSFORMS, "$('a-s').scrollTop = 100; at('a')", "10,0");
}

#[test]
fn its_own_transform_goes_with_it() {
    check(TRANSFORMS, "$('b-s').scrollTop = 100; at('b')", "275,-10");
}

#[test]
fn it_sticks_in_a_scaled_scroller() {
    check(TRANSFORMS, "$('d-s').scrollTop = 100; at('d')", "0,200");
}

#[test]
fn it_sticks_to_the_window_under_a_transform() {
    check(
        TRANSFORMS,
        "[0, 300, 450, 700, 1200].map(function (y) { window.scrollTo(0, y); return at('c'); }).join(' ')",
        "600,450 600,150 600,50 600,50 600,50",
    );
}

/// A sticky box under a fixed box takes nothing from a sticky box above that.
const IN_FIXED_IN_STICKY: &str = concat!(
    "<!doctype html><style>body{margin:0;height:3000px}",
    "#sp{height:400px}#ws{position:sticky;top:50px;width:300px;height:200px;margin-left:100px}",
    "#wf{position:fixed;left:400px;top:100px;width:200px;height:200px}",
    "#wfs{position:sticky;top:10px;width:100px;height:50px}",
    "</style><body><div id=sp></div><div id=ws><div id=wf><div id=wfs></div></div></div></body>",
);

#[test]
fn a_fixed_box_cuts_off_the_sticky_boxes_above_it() {
    check(
        IN_FIXED_IN_STICKY,
        "[0, 500, 1000].map(function (y) { window.scrollTo(0, y); return at('wfs') + ':' + hit(410, 110); }).join(' ')",
        "400,100:wfs 400,100:wfs 400,100:wfs",
    );
}
"""
open(P, "w").write(s)
print("ok")
