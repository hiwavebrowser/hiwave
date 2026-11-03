#!/usr/bin/env python3
"""offset_parent_gen.py <playwright dir> <out .rs>: writes the engine test module for C10 (c) from the Chromium probe.
Leaves out rows whose numbers rest on font metrics, and the non-table rows that are not this item."""
import json, os, re, subprocess, sys

SKIP = {
    "a span in a td", "inner table is the target", "in a caption", "caption is the target",
    "transform ancestor", "filter ancestor", "contain paint ancestor", "will-change transform ancestor",
    "fixed in a transform", "positioned body",
}
# Not offsetParent: an absolute box with no positioned ancestor is placed from its static parent (Z lane 10-31 16:45
# finding, unplaced), and the parser keeps a <td> outside a table where Chromium drops it.
KNOWN = {
    "absolute target in a td", "fixed target in a td", "absolute target in a relative td",
    "absolute target, td, relative wrapper", "td with no table",
}
SKIP |= KNOWN
here = os.path.dirname(os.path.abspath(__file__))
out = subprocess.run(["node", os.path.join(here, "offset_parent_probe.mjs"), sys.argv[1]], capture_output=True, text=True, check=True).stdout
ver = out.splitlines()[0].lstrip("/ ")
rows = []
for line in out.splitlines()[1:]:
    name, body, want = json.loads("[" + line.strip().rstrip(",")[1:-1] + "]")
    if name not in SKIP:
        rows.append((name, body, want))


def lit(s):
    return 'r##"' + s + '"##'


text = f"""//! `offsetParent` through tables (Z row C10 (c)).
//! A static element stops at the nearest `table`, `td` or `th`, by element
//! name and not by display; a positioned one walks past them. Offsets are from
//! the padding edge of the parent found.
//!
//! The rows are what Chromium {ver} (the parity oracle) reports for each hand-made
//! body: `<offsetParent id, or tag, or null> <offsetLeft> <offsetTop>` of #t,
//! written by `trench/z/tools/c10/offset_parent_gen.py` on the Atlas hub. Rows
//! that rest on font metrics are left out.

use super::*;

const CASES: &[(&str, &str, &str)] = &[
"""
for n, b, w in rows:
    text += f"    ({json.dumps(n)}, {lit(b)}, {json.dumps(w)}),\n"
text += """];

const READ: &str = "(function () { var e = document.getElementById('t'); var o = e.offsetParent; \\
    return [o ? (o.id || o.tagName.toLowerCase()) : 'null', e.offsetLeft, e.offsetTop].join(' '); })()";

#[test]
fn offset_parent_through_tables_matches_chromium() {
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
print(len(rows), "rows of", len(rows) + len(SKIP))
