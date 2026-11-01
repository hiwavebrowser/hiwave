#!/usr/bin/env python3
"""Make finding 5's page one where the inset acts."""
P = "/Users/petecopeland/Repos/.worktrees/z-c2d-rework/crates/rustkit-engine/src/sticky_scroll_tests.rs"
s = open(P).read()
for old, new in [
    (
        """    "#wf{position:fixed;left:400px;top:100px;width:200px;height:200px}",
    "#wfs{position:sticky;top:10px;width:100px;height:50px}",
    "</style><body><div id=sp></div><div id=ws><div id=wf><div id=wfs></div></div></div></body>",
""",
        """    "#wf{position:fixed;left:400px;top:0;width:200px;height:200px}",
    "#wfs{position:sticky;top:10px;width:100px;height:50px}",
    "</style><body><div id=sp></div><div id=ws><div id=wf><div id=wfs></div></div></div></body>",
""",
    ),
    (
        """        "[0, 500, 1000].map(function (y) { window.scrollTo(0, y); return at('wfs') + ':' + hit(410, 110); }).join(' ')",
        "400,100:wfs 400,100:wfs 400,100:wfs",
""",
        """        "[0, 500, 1000].map(function (y) { window.scrollTo(0, y); return at('wfs') + ':' + hit(410, 55) + ':' + hit(410, 5); }).join(' ')",
        "400,10:wfs:wf 400,10:wfs:wf 400,10:wfs:wf",
""",
    ),
]:
    assert s.count(old) == 1, old
    s = s.replace(old, new)
open(P, "w").write(s)
print("ok")
