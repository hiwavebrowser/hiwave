"""CH2.E9: add the e9_redirect check to tools/real_window/driver.py."""
p = '/Users/petecopeland/Repos/.worktrees/z-ch2-e9/tools/real_window/driver.py'
s = open(p).read()


def sub(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new, 1)


sub('''                if url.path == "/slow":
''', '''                if url.path == "/e9_start":
                    # CH2.E9: the tab is restored here and lands on e9_final.
                    self.send_response(302)
                    self.send_header("Location", "/e9_final.html")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                if url.path == "/slow":
''')

sub('''    CHECKS = ["h1", "h1_slow", "h2", "h3", "h4", "h4_slow", "h6", "h6_extent", "h8", "h16_click_nav", "h19_spin",
              "i0a_script", "i0a_layout", "i0a_nav", "i0a_close"]
''', '''    def e9_redirect(self):
        """CH2.E9: after a redirect the tab (which feeds the address bar) holds the committed URL and the title."""
        c = "e9_redirect"
        if not self.open_page(c, "e9_start"):
            return
        self.expect(c, "the app followed the redirect", self.fixture.wait("/e9_final.html", 15, self.since))
        start = "%s/e9_start" % self.fixture.base
        final = "%s/e9_final.html" % self.fixture.base
        urls, text = [], ""
        end = time.time() + 15
        while time.time() < end:
            try:
                text = self.app.state_file.read_text()
                urls = tab_urls(json.loads(text))
            except (FileNotFoundError, ValueError):
                urls = []
            if final in urls and "E9 final" in text:
                break
            time.sleep(0.2)
        self.expect(c, "the saved tab holds the committed URL, not the one restored",
                    final in urls and start not in urls, "tab urls %s" % urls)
        self.expect(c, "the saved tab holds the page's title", "E9 final" in text)

    CHECKS = ["h1", "h1_slow", "h2", "h3", "h4", "h4_slow", "h6", "h6_extent", "h8", "h16_click_nav", "h19_spin",
              "i0a_script", "i0a_layout", "i0a_nav", "i0a_close", "e9_redirect"]
''')

sub('''def set_tab_urls(node, url):''', '''def tab_urls(node):
    """Every `url` string in the saved state."""
    found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "url" and isinstance(value, str):
                found.append(value)
            else:
                found.extend(tab_urls(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(tab_urls(value))
    return found


def set_tab_urls(node, url):''')
open(p, 'w').write(s)
print('ok')
