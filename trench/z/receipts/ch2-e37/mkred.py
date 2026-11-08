"""Build the red-commit version of rustkit-engine/src/lib.rs: develop's file
plus the CH2.E37 tests and stubs that keep develop's behaviour."""
import subprocess, sys

wt = sys.argv[1]
path = "crates/rustkit-engine/src/lib.rs"
base = subprocess.run(["git", "-C", wt, "show", "HEAD:" + path], capture_output=True, text=True, check=True).stdout
cur = open(f"{wt}/{path}").read()

# Tests: from the CH2.E37 comment to the end of the textarea test.
start = cur.index("    // CH2.E37 (hiwave-macos#990)")
end_marker = "js_string(\"\\\"a\\\\nb\\\\n\\\\n\\\"\")\n        );\n    }\n"
end = cur.index(end_marker, start) + len(end_marker)
tests = cur[start:end]

anchor = """        assert_eq!(engine.submit_focused_form(id), None);
        assert_eq!(js(&mut engine, id, "log.join(' ')"), js_string("keydown:Enter:q:true"));
    }
"""
assert base.count(anchor) == 1
red = base.replace(anchor, anchor + "\n" + tests)

stub_anchor = """    pub fn submit_focused_form(&mut self, id: EngineViewId) -> Option<String> {
        let _hold = wgate::hold("submit");"""
stub = """    pub fn submit_focused_form(&mut self, id: EngineViewId) -> Option<String> {
        self.submit_focused_form_with(id, false, false, false)
    }

    /// CH2.E37 red stub: the modifiers are still dropped.
    pub fn submit_focused_form_with(&mut self, id: EngineViewId, _ctrl: bool, _shift: bool, _alt: bool) -> Option<String> {
        let _hold = wgate::hold("submit");"""
assert red.count(stub_anchor) == 1
red = red.replace(stub_anchor, stub)

pend_anchor = "    /// Fire `keydown` or `keyup` for a key at `node`"
pend = """    /// CH2.E37 red stub: nothing records the submit step's keydown.
    pub(crate) fn enter_keydown_pending(&self, _id: EngineViewId) -> bool {
        false
    }

"""
assert red.count(pend_anchor) == 1
red = red.replace(pend_anchor, pend + pend_anchor)
open(sys.argv[2], "w").write(red)
print("ok", len(red))
