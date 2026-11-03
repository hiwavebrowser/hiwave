#!/usr/bin/env python3
"""replaced_ratio_gen.py <playwright dir> <out .rs> [skip names file]: writes the engine test module for C10 (e)
from the Chromium probe (replaced_ratio_probe.mjs). Rows named in the skip file (one per line) are left out."""
import json, os, subprocess, sys

here = os.path.dirname(os.path.abspath(__file__))
out = subprocess.run(["node", os.path.join(here, "replaced_ratio_probe.mjs"), sys.argv[1]],
                     capture_output=True, text=True, check=True).stdout
lines = out.splitlines()
ver = lines[0].lstrip("/ ")
skip = set()
skipped_doc = ""
if len(sys.argv) > 3:
    for l in open(sys.argv[3]):
        l = l.strip()
        if not l:
            continue
        if l.startswith("#"):
            skipped_doc += "//! " + l.lstrip("# ") + ":\n"
        else:
            skip.add(l)
            skipped_doc += "//! - " + l + "\n"
rows = [json.loads(l) for l in lines[1:]]
rows = [r for r in rows if r[0] not in skip]


def lit(s):
    return 'r##"' + s + '"##'


text = f"""//! Replaced boxes (`<img>`, `<canvas>`) with a natural ratio inside flex
//! and grid, with and without `aspect-ratio` (Z row C10 (e), second slice).
//!
//! The rows are what Chromium {ver} (the parity oracle) reports for each
//! hand-made body: `<width>x<height> @<left>,<top>` of #t's border box from
//! `getBoundingClientRect`, rounded to 0.01. Written by
//! `trench/z/tools/c10/replaced_ratio_gen.py` on the Atlas hub. No text, so no
//! font metrics; the image is a 40x20 PNG data URL (natural ratio 2:1), the
//! canvas 300x150 unless the row says otherwise.
//!
//! Left out (wrong on develop and at this change, or LayoutUnit rounding):
{{SKIPPED}}
use super::*;

const CASES: &[(&str, &str, &str)] = &[
"""
for n, b, w in rows:
    text += f"    ({json.dumps(n)}, {lit(b)}, {json.dumps(w)}),\n"
text = text.replace("{SKIPPED}", skipped_doc + "\n")
text += """];

const READ: &str = "(function () { var r = document.getElementById('t').getBoundingClientRect(); \\
    var f = function (v) { return String(Math.round(v * 100) / 100); }; \\
    return f(r.width) + 'x' + f(r.height) + ' @' + f(r.left) + ',' + f(r.top); })()";

#[test]
#[cfg(all(target_os = "macos", feature = "headless"))]
fn replaced_ratio_in_flex_and_grid_matches_chromium() {
    let mut engine = Engine::new(EngineConfig::default()).expect("engine");
    let view = engine
        .create_headless_view(Bounds::new(0, 0, 800, 600))
        .expect("headless view");
    let mut wrong = Vec::new();
    for (name, body, want) in CASES {
        let html = format!("<!doctype html><style>body{{margin:0}}</style><body>{body}");
        engine.load_html(view, &html).expect("load_html");
        let value = engine.execute_script(view, READ).expect("script");
        let got = value
            .strip_prefix("String(\\"")
            .and_then(|v| v.strip_suffix("\\")"))
            .unwrap_or(&value);
        if got != *want {
            wrong.push(format!("{name}: {got}, Chromium {want}"));
        }
    }
    assert!(
        wrong.is_empty(),
        "{} of {} wrong:\\n{}",
        wrong.len(),
        CASES.len(),
        wrong.join("\\n")
    );
}
"""
open(sys.argv[2], "w").write(text)
print(len(rows), "rows;", len(skip), "skipped")
