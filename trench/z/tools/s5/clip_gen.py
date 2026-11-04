#!/usr/bin/env python3
"""clip_gen.py <playwright dir> <out .rs> [skip names file]: writes the engine test module for S5
(visually hidden boxes) from the Chromium probe clip_probe.mjs. Skip-file rows are left out."""
import json, os, subprocess, sys

here = os.path.dirname(os.path.abspath(__file__))
out = subprocess.run(["node", os.path.join(here, "clip_probe.mjs"), sys.argv[1]],
                     capture_output=True, text=True, check=True).stdout
lines = out.splitlines()
ver = lines[0].lstrip("/ ")
skip, skipped_doc = set(), ""
if len(sys.argv) > 3:
    for l in open(sys.argv[3]):
        l = l.strip()
        if not l:
            continue
        if l.startswith("#"):
            skipped_doc += "//! " + l.lstrip("# ") + "\n"
        else:
            skip.add(l)
            skipped_doc += "//! - " + l + "\n"
rows = [json.loads(l) for l in lines[1:]]
rows = [r for r in rows if r[0] not in skip]


def lit(s):
    return 'r##"' + s + '"##'


text = f"""//! Visually hidden ("screen-reader-only") boxes (Z row S5): the legacy
//! `clip: rect()` property and `clip-path: inset(50%)` on a 1x1 absolute box.
//! Before this row `clip` was not parsed at all, so eBay's `.clipped` header
//! labels ("expand Cart") and Bootstrap's `.visually-hidden` text painted.
//!
//! Each row is Chromium {ver}'s ink for the hand-made body: the number of
//! pixels that are not pure white in a 400x300 frame. The hidden box is red
//! with red 20px text, so anything that leaks is ink. Written by
//! `trench/z/tools/s5/clip_gen.py` on the Atlas hub (probe `clip_probe.mjs`).
{{SKIPPED}}
use super::*;

const WIDTH: u32 = 400;
const HEIGHT: u32 = 300;

const CASES: &[(&str, &str, usize)] = &[
"""
for n, b, w in rows:
    text += f"    ({json.dumps(n)}, {lit(b)}, {w}),\n"
text = text.replace("{SKIPPED}", ("//!\n//! Left out:\n" + skipped_doc) if skipped_doc else "")
text += """];

fn ink(engine: &mut Engine, view: EngineViewId) -> usize {
    engine.render_view(view).expect("render");
    let path = std::env::temp_dir().join(format!(
        "rustkit-s5-clip-{}-{:?}.ppm",
        std::process::id(),
        std::thread::current().id()
    ));
    engine
        .capture_frame(view, path.to_str().unwrap())
        .expect("capture");
    let ppm = std::fs::read(&path).expect("frame");
    let _ = std::fs::remove_file(&path);
    ppm[ppm.len() - WIDTH as usize * HEIGHT as usize * 3..]
        .chunks_exact(3)
        .filter(|p| *p != [255, 255, 255])
        .count()
}

#[test]
#[cfg(all(target_os = "macos", feature = "headless"))]
fn visually_hidden_boxes_paint_as_chromium() {
    let mut wrong = Vec::new();
    for (name, body, want) in CASES {
        let mut engine = Engine::new(EngineConfig::default()).expect("engine");
        let view = engine
            .create_headless_view(Bounds::new(0, 0, WIDTH, HEIGHT))
            .expect("headless view");
        let html = format!(
            "<!doctype html><style>html,body{{margin:0;background:#fff}}div{{box-sizing:border-box}}</style>{body}"
        );
        engine.load_html(view, &html).expect("load_html");
        let got = ink(&mut engine, view);
        if got != *want {
            wrong.push(format!("{name}: ink {got}, Chromium {want}"));
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
