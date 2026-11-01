#!/usr/bin/env python3
"""#853 R1 red tests: Chromium 143's rects (c10b2_r1_probe.mjs, c10b2_var_probe.mjs), each value after translateX(7px) under translateY(3px)."""
P = "/Users/petecopeland/Repos/.worktrees/z-c10b2-r1/crates/rustkit-engine/src/transform_parse_tests.rs"
s = open(P).read().rstrip("\n") + '''

/// The rect of a 100x50 box at (20,10) when this value follows
/// `transform: translateX(7px)` in a parent with `translateY(3px)`: refused
/// reads `27 13 100 50`, as the earlier declaration stays. Chromium 143
/// (`trench/z/tools/c10/c10b2_r1_probe.mjs`, `c10b2_var_probe.mjs`).
#[track_caller]
fn after_an_earlier_one(value: &str, want: &str) {
    let page = format!(
        "<!doctype html><style>body{{margin:0}}#w{{transform:translateY(3px)}}\\
         #b{{--i:2;--a:90deg;position:absolute;left:20px;top:10px;width:100px;height:50px;\\
         transform:translateX(7px);transform:{value}}}</style><div id=w><div id=b></div></div>"
    );
    let mut engine = Engine::new(EngineConfig::default()).expect("engine");
    let view = engine
        .create_headless_view(Bounds { x: 0, y: 0, width: 800, height: 600 })
        .expect("view");
    engine.load_html(view, &page).expect("load");
    let got = engine
        .execute_script(
            view,
            "var r = document.getElementById('b').getBoundingClientRect(); \\
             [r.x, r.y, r.width, r.height].map(function (v) { return +v.toFixed(3); }).join(' ')",
        )
        .expect("script");
    assert_eq!(got, format!("String(\\"{want}\\")"), "transform: {value}");
}

const KEPT: &str = "27 13 100 50";
const ROTATED_45: &str = "16.967 -15.033 106.066 106.066";
const ROTATED_90: &str = "45 -12 50 100";
const NONE: &str = "20 13 100 50";

#[test]
fn perspective_takes_no_negative_length_and_no_bare_number() {
    for value in ["perspective(-10px)", "perspective(10)", "perspective(10%)"] {
        after_an_earlier_one(value, KEPT);
    }
    for value in [
        "perspective(0)",
        "perspective(10px)",
        "perspective(+10px)",
        "perspective(-0px)",
        "perspective(calc(-10px))",
        "perspective(calc(10px))",
        "perspective(none)",
        "perspective(NONE)",
    ] {
        after_an_earlier_one(value, NONE);
    }
}

#[test]
fn calc_in_an_angle() {
    for value in [
        "rotate(calc(-1 * 45deg))",
        "rotate(calc(45deg))",
        "rotate(calc(0.25turn + 45deg))",
        "rotate(calc(90deg / 2))",
    ] {
        after_an_earlier_one(value, ROTATED_45);
    }
    for value in [
        "rotate(calc(2 * (10deg + 35deg)))",
        "rotate(min(90deg, 180deg))",
        "rotate(max(90deg, 45deg))",
        "rotate(clamp(10deg, 90deg, 180deg))",
        "rotate(CALC(90DEG))",
        "rotate(calc( 90deg ))",
    ] {
        after_an_earlier_one(value, ROTATED_90);
    }
    after_an_earlier_one("rotate(calc(1rad - 1rad))", NONE);
    after_an_earlier_one("skew(calc(45deg))", "-5 13 150 50");
    after_an_earlier_one("rotateX(calc(60deg))", "20 25.5 100 25");
}

/// An infinite angle is no rotation.
#[test]
fn an_angle_divided_by_zero_turns_nothing() {
    after_an_earlier_one("rotate(calc(90deg / 0))", NONE);
}

#[test]
fn calc_that_is_not_an_angle_is_refused() {
    for value in [
        "rotate(calc(90))",
        "rotate(calc(0))",
        "rotate(calc(45deg * 2deg))",
        "rotate(calc(45deg + 1))",
        "rotate(calc(90deg+45deg))",
    ] {
        after_an_earlier_one(value, KEPT);
    }
}

#[test]
fn calc_in_a_number() {
    after_an_earlier_one("scale(calc(1.5))", "-5 0.5 150 75");
    after_an_earlier_one("scale(calc(1 + 0.5))", "-5 0.5 150 75");
    after_an_earlier_one("scale(calc(2 * 1.5), calc(4 / 2))", "-80 -12 300 100");
    after_an_earlier_one("scale(calc(50%))", "45 25.5 50 25");
    after_an_earlier_one("scale(min(2, 3))", "-30 -12 200 100");
    after_an_earlier_one("scaleX(calc(2))", "-30 13 200 50");
    after_an_earlier_one("scale3d(calc(2),1,1)", "-30 13 200 50");
    after_an_earlier_one("matrix(calc(2),0,0,1,0,0)", "-30 13 200 50");
    after_an_earlier_one("rotate3d(0,0,calc(1),90deg)", ROTATED_90);
    after_an_earlier_one("scale(calc(1.5deg))", KEPT);
}

#[test]
fn a_list_keeps_all_of_itself_with_calc_in_it() {
    after_an_earlier_one("translate(-50%,-50%) rotate(calc(2 * 45deg))", "-5 -37 50 100");
    after_an_earlier_one(
        "translate(-50%, -50%) rotate(calc(-1 * 45deg)) scale(calc(1 + 1))",
        "-86.066 -93.066 212.132 212.132",
    );
    after_an_earlier_one(
        "translate(-50%,-50%) rotate(calc(var(--i) * 30deg))",
        "-26.651 -42.801 93.301 111.603",
    );
    after_an_earlier_one("rotate(var(--a))", ROTATED_90);
    after_an_earlier_one("scale(var(--i))", "-30 -12 200 100");
}

#[test]
fn units_ignore_case() {
    after_an_earlier_one("translate(5PX,6Px)", "25 19 100 50");
    after_an_earlier_one("translateX(5PX)", "25 13 100 50");
    after_an_earlier_one("rotate(45DEG)", ROTATED_45);
    after_an_earlier_one("rotate(0.25TURN)", ROTATED_90);
    after_an_earlier_one("rotate(100GRAD)", ROTATED_90);
    after_an_earlier_one("rotate(1RAD)", "21.948 -17.581 96.104 111.162");
    after_an_earlier_one("scale(1E1)", "-430 -212 1000 500");
    after_an_earlier_one("translateX(1E1px)", "30 13 100 50");
}

#[test]
fn keywords_ignore_case_and_take_the_earlier_one_away() {
    for value in ["NONE", "None", "initial", "INITIAL", "unset", "revert", "revert-layer"] {
        after_an_earlier_one(value, NONE);
    }
    after_an_earlier_one("inherit", "20 16 100 50");
}

#[test]
fn infinity_and_nan_are_not_numbers() {
    for value in [
        "scale(inf)",
        "scale(infinity)",
        "scale(NaN)",
        "scale(nan)",
        "scale(-inf)",
        "matrix(inf,0,0,1,0,0)",
        "rotate(infdeg)",
        "rotate(nandeg)",
        "translateX(infpx)",
        "rotate3d(inf,0,1,90deg)",
        "scale(5.)",
    ] {
        after_an_earlier_one(value, KEPT);
    }
    after_an_earlier_one("scale(.5)", "45 25.5 50 25");
    after_an_earlier_one("scale(+2)", "-30 -12 200 100");
}
'''
open(P, "w").write(s)
print("ok")
