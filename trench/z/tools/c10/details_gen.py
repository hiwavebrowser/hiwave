#!/usr/bin/env python3
"""details_gen.py <playwright dir> <out .rs>: writes the engine test module for C10 (d) from the Chromium probe,
and prints the rows. The disclosure marker is not in these rows: the engine draws no list markers yet.
The module on the branch also holds `the_default_summary_paints_details`, added by hand after the first fix:
regenerating overwrites it, so copy it back."""
import json, os, subprocess, sys

here = os.path.dirname(os.path.abspath(__file__))
out = subprocess.run(["node", os.path.join(here, "details_probe.mjs"), sys.argv[1]], capture_output=True, text=True, check=True).stdout
ver = out.splitlines()[0].lstrip("/ ")
rows = []
for line in out.splitlines()[1:]:
    name, body, want = json.loads("[" + line.strip().rstrip(",")[1:-1] + "]")
    rows.append((name, body, want))
    print(f"{name} => {want}")


def lit(s):
    return 'r##"' + s + '"##'


text = f"""//! `<details>` and `<summary>` boxes (Z row C10 (d)). HTML 15.3.9: the
//! first `summary` child is shown first, wherever it sits among the children;
//! a details with no `summary` child shows a default one reading "Details";
//! a closed details shows its summary only.
//!
//! The rows are what Chromium {ver} (the parity oracle) reports for each
//! hand-made body: `<details height> <#s top> <#p top> <#q top>` ("-" when
//! the element has no box); a closed details reads only `<height> <#s top>`,
//! because Chromium lays out its hidden content. Every line is 20px. Written
//! by `trench/z/tools/c10/details_gen.py` on the Atlas hub. The disclosure
//! triangle is not here: the engine draws no list markers yet.

use super::*;

const STYLE: &str = "body{{margin:0;font:16px/20px monospace}} p{{margin:0}} details,summary{{list-style:none}}";

const CASES: &[(&str, &str, &str)] = &[
"""
text = text.replace("{{", "{").replace("}}", "}")
for n, b, w in rows:
    text += f"    ({json.dumps(n)}, {lit(b)}, {json.dumps(w)}),\n"
text += """];

const READ: &str = "(function () { \\
    var top = function (i) { var e = document.getElementById(i); if (!e) return '-'; var r = e.getBoundingClientRect(); return r.height ? Math.round(r.top) : '-'; }; \\
    var d = document.getElementById('d'); \\
    if (!d.hasAttribute('open')) { var s = document.getElementById('s'); return [Math.round(d.getBoundingClientRect().height), s && s.parentElement === d ? top('s') : '-'].join(' '); } \\
    return [Math.round(d.getBoundingClientRect().height), top('s'), top('p'), top('q')].join(' '); })()";

#[test]
fn details_boxes_match_chromium() {
    let mut engine = Engine::new(EngineConfig::default()).expect("engine");
    let view = engine
        .create_headless_view(Bounds::new(0, 0, 800, 600))
        .expect("headless view");
    let mut wrong = Vec::new();
    for (name, body, want) in CASES {
        let html = format!("<!doctype html><style>{STYLE}</style>{body}");
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
print(len(rows), "rows")
