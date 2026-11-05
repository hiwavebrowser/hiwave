"""CH3.A2: add the a2_chrome_boots check to tools/real_window/driver.py."""
p = '/Users/petecopeland/Repos/.worktrees/z-ch3-a2/tools/real_window/driver.py'
s = open(p).read()


def sub(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new, 1)


sub('''    CHECKS = ["h1", "h1_slow", "h2", "h3", "h4", "h4_slow", "h6", "h6_extent", "h8", "h16_click_nav", "h19_spin",
              "i0a_script", "i0a_layout", "i0a_nav", "i0a_close", "e9_redirect"]
''', '''    def a2_chrome_boots(self):
        """CH3.A2: with HIWAVE_RUSTKIT_CHROME=1 the chrome is a RustKit view whose script reaches the app."""
        c = "a2_chrome_boots"
        if not self.open_page(c, "e9_final.html", env={"HIWAVE_RUSTKIT_CHROME": "1"}):
            return
        m = self.app.wait_log(r"the chrome is a RustKit view", 10)
        self.expect(c, "the app built the chrome as a RustKit view", bool(m))
        # The chrome asks for its tabs and workspaces when its document loads.
        tabs = self.app.wait_log(r'Chrome IPC: \\{"cmd":"get_tabs"', 20)
        self.expect(c, "the chrome's script posted get_tabs and the app's handler took it", bool(tabs),
                    tabs.group(0) if tabs else "")
        spaces = self.app.wait_log(r'Chrome IPC: \\{"cmd":"get_workspaces"', 5)
        self.expect(c, "the chrome's script posted get_workspaces", bool(spaces))
        time.sleep(3)
        self.expect(c, "the app is still running 3 s later", self.app.alive())
        self.expect(c, "the page did not take the chrome's document",
                    "E9 final" in self.app.state_file.read_text() or not re.search(r"Navigating content to: data:", self.app.log_text()))

    CHECKS = ["h1", "h1_slow", "h2", "h3", "h4", "h4_slow", "h6", "h6_extent", "h8", "h16_click_nav", "h19_spin",
              "i0a_script", "i0a_layout", "i0a_nav", "i0a_close", "e9_redirect", "a2_chrome_boots"]
''')
open(p, 'w').write(s)
print('ok')
