"""CH2.E9 red step: ChromeUpdates type, stub take_chrome_updates, tests."""
p = '/Users/petecopeland/Repos/.worktrees/z-ch2-e9/crates/hiwave-app/src/webview_rustkit.rs'
s = open(p).read()

anchor = "pub struct RustKitView {"
assert s.count(anchor) == 1
s = s.replace(anchor, '''/// What the browser chrome has not been told yet about the page on
/// screen (CH2.E9): the committed URL (after any redirect), the title, and
/// load start and end. Taken by [`RustKitView::take_chrome_updates`].
#[derive(Debug, Default, Clone, PartialEq, Eq)]
pub struct ChromeUpdates {
    /// The URL the page committed, when it changed. Only web and file
    /// URLs: a document the app loads itself (New Tab, about) keeps the
    /// address the app gave it.
    pub url: Option<String>,
    /// The document title, when it changed.
    pub title: Option<String>,
    /// A load started since the last take.
    pub started: bool,
    /// The load state now, when it changed: `Some(false)` once it ended.
    pub loading: Option<bool>,
    /// The URL of a load that completed since the last take (history).
    pub finished: Option<String>,
}

''' + anchor, 1)

anchor2 = "    pub fn take_script_navigation(&self) -> Option<(String, bool)> {"
assert s.count(anchor2) == 1
s = s.replace(anchor2, '''    /// What the chrome must be told since the last call (CH2.E9).
    pub fn take_chrome_updates(&self) -> ChromeUpdates {
        ChromeUpdates::default()
    }

''' + anchor2, 1)

anchor3 = "    /// Answers every request with `body` at once and logs its path and\n"
assert s.count(anchor3) == 1
s = s.replace(anchor3, r'''    /// `/start` redirects (302) to `/final`, which has a title.
    fn redirect_server() -> String {
        use std::io::{Read, Write};
        let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        let port = listener.local_addr().unwrap().port();
        std::thread::spawn(move || {
            for stream in listener.incoming() {
                let Ok(mut stream) = stream else { continue };
                std::thread::spawn(move || {
                    let mut request = Vec::new();
                    let mut buf = [0u8; 2048];
                    while !request.windows(4).any(|w| w == b"\r\n\r\n") {
                        match stream.read(&mut buf) {
                            Ok(0) | Err(_) => return,
                            Ok(n) => request.extend_from_slice(&buf[..n]),
                        }
                    }
                    let path = String::from_utf8_lossy(&request)
                        .split_whitespace()
                        .nth(1)
                        .unwrap_or("")
                        .to_string();
                    if path == "/start" {
                        let _ = write!(
                            stream,
                            "HTTP/1.1 302 Found\r\nLocation: /final\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
                        );
                        return;
                    }
                    let body = "<title>final</title><p>here</p>";
                    let _ = write!(
                        stream,
                        "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                        body.len(),
                        body
                    );
                });
            }
        });
        format!("http://127.0.0.1:{port}/")
    }

    /// CH2.E9: on macOS nothing read the page's URL, title or load events,
    /// so the address bar kept the typed URL after a redirect and the tab
    /// never learned its title or that the load had ended.
    #[test]
    fn content_thread_the_chrome_is_told_the_committed_url_title_and_load_end() {
        let view = content_view();
        let base = redirect_server();
        load_and_settle(&view, &format!("{base}start"));
        let updates = view.take_chrome_updates();
        let committed = format!("{base}final");
        assert_eq!(updates.url.as_deref(), Some(committed.as_str()), "{updates:?}");
        assert_eq!(updates.title.as_deref(), Some("final"), "{updates:?}");
        assert!(updates.started, "{updates:?}");
        assert_eq!(updates.loading, Some(false), "{updates:?}");
        assert_eq!(updates.finished.as_deref(), Some(committed.as_str()), "{updates:?}");
        assert_eq!(view.take_chrome_updates(), ChromeUpdates::default(), "reported twice");
    }

    /// A document the app loads itself keeps the address the app gave it.
    #[test]
    fn content_thread_an_app_document_reports_no_url() {
        let view = content_view();
        view.load_html_internal("<title>New Tab</title><p>x</p>").unwrap();
        let deadline = Instant::now() + Duration::from_secs(10);
        while view.latest_commit.borrow().is_none() {
            assert!(Instant::now() < deadline, "the document never committed");
            wake(&view);
            std::thread::sleep(Duration::from_millis(5));
        }
        let updates = view.take_chrome_updates();
        assert_eq!(updates.url, None, "{updates:?}");
        assert_eq!(updates.title.as_deref(), Some("New Tab"), "{updates:?}");
    }

''' + anchor3, 1)
open(p, 'w').write(s)
print('ok')
