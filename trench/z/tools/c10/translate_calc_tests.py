#!/usr/bin/env python3
"""Red tests: the `translate` property with spaces inside a function. Chromium 143, translate_calc_probe.mjs."""
P = "/Users/petecopeland/Repos/.worktrees/z-c10-translate-calc/crates/rustkit-engine/src/transform_rect_tests.rs"
s = open(P).read()
old = """const INLINES: &str = "<!doctype html>"""
new = '''/// The rect of a 100x50 box at (20,10) when this value follows `translate:7px`:
/// refused reads `27 10`, as the earlier declaration stays.
#[track_caller]
fn translate_after_an_earlier_one(value: &str, want: &str) {
    let page = format!(
        "<!doctype html><style>body{{margin:0}}\\
         #b{{position:absolute;left:20px;top:10px;width:100px;height:50px;translate:7px;translate:{value}}}</style>\\
         <div id=b></div>"
    );
    check(&page, "box('b')", want);
}

/// Tailwind's slide-out panel: `-translate-y-[calc(100%+1px)]`.
#[test]
fn translate_takes_a_function_with_spaces_in_it() {
    translate_after_an_earlier_one("0px calc(-100% - 1px)", "20 -41 100 50");
    translate_after_an_earlier_one("calc(10px + 5%) 0", "35 10 100 50");
    translate_after_an_earlier_one("calc(10px + 5%)", "35 10 100 50");
    translate_after_an_earlier_one("calc(1px + 1px) calc(2px * 2) 0", "22 14 100 50");
    translate_after_an_earlier_one("calc( 1px + 1px ) 3px 0px", "22 13 100 50");
    translate_after_an_earlier_one("min(1px, 2px) max(3px, 4px)", "21 14 100 50");
}

/// With no perspective a depth flattens, as in `translate3d`.
#[test]
fn translate_flattens_a_depth() {
    translate_after_an_earlier_one("1px 2px 3px", "21 12 100 50");
    translate_after_an_earlier_one("1px 2px calc(1px + 1px)", "21 12 100 50");
}

#[test]
fn translate_takes_three_values_at_most() {
    translate_after_an_earlier_one("1px 2px 3px 4px", "27 10 100 50");
    translate_after_an_earlier_one("calc(1px + 1px) calc(2px * 2) 0 0", "27 10 100 50");
    translate_after_an_earlier_one("none", "20 10 100 50");
}

/// The page's shape: an opaque panel slid up out of a clipping wrapper, which
/// is what keeps it from showing. Where layout puts the wrapper is row C15; the
/// panel's move from it is this one.
#[test]
fn a_panel_slides_out_of_its_clipping_wrapper() {
    let page = "<!doctype html><style>body{margin:0;height:2000px}\\
        #h{position:sticky;top:0;height:72px;width:800px;display:flex}\\
        ul{display:flex;margin:0;padding:0;list-style:none}li{display:flex;z-index:30;margin-left:100px;width:90px}\\
        #w{position:absolute;top:72px;left:0;width:100%;overflow:hidden auto;max-height:500px}\\
        #p{position:relative;background:rgb(2,9,10);height:200px;translate:0px calc(-100% - 1px)}\\
        </style><body><div id=h><ul><li><div id=w><div id=p></div></div></li></ul></div></body>";
    check(
        page,
        "$('p').getBoundingClientRect().y - $('w').getBoundingClientRect().y + ' ' + $('p').getBoundingClientRect().height",
        "-201 200",
    );
}

const INLINES: &str = "<!doctype html>'''
assert s.count(old) == 1
s = s.replace(old, new)
open(P, "w").write(s)
print("ok")
