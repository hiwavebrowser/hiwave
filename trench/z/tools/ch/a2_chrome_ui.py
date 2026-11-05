"""CH3.A2 step 1: the chrome view behind a ChromeUi trait (eval + place)."""
import re

p = '/Users/petecopeland/Repos/.worktrees/z-ch3-a2/crates/hiwave-app/src/main.rs'
s = open(p).read()
n0 = len(re.findall(r'wry::WebView::(evaluate_script|set_bounds)\(', s))

s, a = re.subn(r'wry::WebView::evaluate_script\(chrome,\s*', 'chrome.eval(', s)
s, b = re.subn(r'wry::WebView::evaluate_script\(&chrome_for_events,\s*', 'chrome_for_events.eval(', s)
s, c = re.subn(r'wry::WebView::evaluate_script\(&chrome_webview,\s*', 'chrome_webview.eval(', s)
s, d = re.subn(r'wry::WebView::set_bounds\(chrome, chrome_rect\)', 'chrome.place(chrome_rect)', s)
s, e = re.subn(r'(fn sync_[a-z_]+_to_chrome\(state: &Arc<Mutex<AppState>>, chrome: )&WebView', r'\1&impl ChromeUi', s)
old = '''fn apply_layout(
    window: &tao::window::Window,
    chrome: &WebView,'''
assert s.count(old) == 1
s = s.replace(old, '''fn apply_layout(
    window: &tao::window::Window,
    chrome: &impl ChromeUi,''')
n1 = len(re.findall(r'wry::WebView::(evaluate_script|set_bounds)\(', s))
print('replaced', a, b, c, d, 'sigs', e, 'wry calls left', n0, '->', n1)

anchor = 'fn apply_layout(\n'
assert s.count(anchor) == 1
s = s.replace(anchor, '''/// The browser chrome's view: the WebKit view today; a RustKit view behind
/// `HIWAVE_RUSTKIT_CHROME` (CH3.A2). The app only runs script in it and
/// places it.
trait ChromeUi {
    /// Run `js` in the chrome's document, without waiting for its value.
    fn eval(&self, js: &str) -> Result<(), String>;
    /// Move and size the chrome view.
    fn place(&self, rect: Rect);
}

impl ChromeUi for WebView {
    fn eval(&self, js: &str) -> Result<(), String> {
        wry::WebView::evaluate_script(self, js).map_err(|e| e.to_string())
    }

    fn place(&self, rect: Rect) {
        let _ = wry::WebView::set_bounds(self, rect);
    }
}

impl<T: ChromeUi + ?Sized> ChromeUi for Arc<T> {
    fn eval(&self, js: &str) -> Result<(), String> {
        (**self).eval(js)
    }

    fn place(&self, rect: Rect) {
        (**self).place(rect)
    }
}

''' + anchor, 1)
open(p, 'w').write(s)
