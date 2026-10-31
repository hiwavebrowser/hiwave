"""C2(c) second splice: the location.hash setter, and window-x expectations."""
W = '/Users/petecopeland/Repos/.worktrees/z-c2c/crates/'


def sub(path, a, b, n=1):
    p = W + path
    s = open(p, newline='').read()
    assert s.count(a) == n, (a[:50], s.count(a))
    open(p, 'w', newline='').write(s.replace(a, b))


sub('rustkit-bindings/src/web_history.js', '''    // Location's stringifier is its href (HTML §7.3).''', '''    // The hash setter (HTML §7.2.4) is the fragment navigation. Script could
    // assign `location.hash` and nothing happened until 2026-10-31.
    var hashValue = loc.hash || '';
    Object.defineProperty(loc, 'hash', {
        get: function () { return hashValue; },
        set: function (v) {
            if (syncing) { hashValue = String(v); return; }
            var target;
            try { target = new URL(hrefValue.split('#')[0] + '#' + String(v).replace(/^#/, '')); } catch (e) { return; }
            go(target);
        },
        enumerable: true, configurable: true
    });
    g.__rustkit_location_hash_sync = function (hash) { hashValue = hash; };
    // Location's stringifier is its href (HTML §7.3).''')
sub('rustkit-bindings/src/lib.rs', '''            window.location.hash = {:?};
            window.location.origin = {:?};
            document.URL = {:?};
            if (window.__rustkit_history_reset)''', '''            if (window.__rustkit_location_hash_sync) window.__rustkit_location_hash_sync({:?});
            window.location.origin = {:?};
            document.URL = {:?};
            if (window.__rustkit_history_reset)''')
t = 'rustkit-engine/src/scroll_into_view_tests.rs'
sub(t, '''"in=400,307 out=0,324 win=12,1081");
}''', '''"in=400,307 out=0,324 win=0,1081");
}''')
sub(t, '''#[test]
fn the_default_scrolls_every_scroller_and_the_window() {''', '''// The window has no horizontal extent (`max_scroll_offset.0` is always 0), so
// where Chromium also moves the window across, these expect its x to stay 0:
// start/start 12, `ab2` 170, `big` 400. Everything else is Chromium's.

#[test]
fn the_default_scrolls_every_scroller_and_the_window() {''')
sub(t, '''"rel=0,200 win=170,50"''', '''"rel=0,200 win=0,50"''')
sub(t, '''"big-s=0,50 win=400,0"''', '''"big-s=0,50 win=0,0"''', 2)
sub(t, '''"big-s=0,100 win=400,0"''', '''"big-s=0,100 win=0,0"''')
sub(t, '''"big-s=0,250 win=400,0"''', '''"big-s=0,250 win=0,0"''')
