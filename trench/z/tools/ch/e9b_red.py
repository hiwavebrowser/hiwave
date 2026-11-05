"""CH2.E9 part 2 red: PageEvent::Ipc variant (not produced) + content-thread test."""
root = '/Users/petecopeland/Repos/.worktrees/z-ch2-e9/crates/'


def sub(s, old, new):
    assert s.count(old) == 1, old
    return s.replace(old, new, 1)


p = root + 'rustkit-engine/src/page_protocol.rs'
s = open(p).read()
s = sub(s, '''    Focused(bool),
    /// Not produced on this PR. The variant is the protocol's.
    #[allow(dead_code)]
    Cursor(String),''', '''    Focused(bool),
    /// A message the page posted with `window.ipc.postMessage` (CH2.E9),
    /// pushed to the window as it arrives; nothing polls the page for it.
    Ipc {
        payload: String,
        nav_id: u64,
    },
    /// Not produced on this PR. The variant is the protocol's.
    #[allow(dead_code)]
    Cursor(String),''')
open(p, 'w').write(s)

p = root + 'rustkit-engine/src/content_thread.rs'
s = open(p).read()
s = sub(s, '''    #[test]
    fn a_superseded_navigation_drops_the_late_result() {''', '''    /// The `Ipc` payloads seen within `budget`.
    fn ipc_payloads(page: &ContentThread, budget: Duration) -> Vec<String> {
        let deadline = Instant::now() + budget;
        let mut seen = Vec::new();
        while Instant::now() < deadline {
            for event in page.poll() {
                if let PageEvent::Ipc { payload, .. } = event {
                    seen.push(payload);
                }
            }
            std::thread::sleep(Duration::from_millis(10));
        }
        seen
    }

    #[test]
    fn the_window_is_sent_what_the_page_posts_on_window_ipc() {
        // CH2.E9: `window.ipc.postMessage` filled a queue only a poll of
        // the engine could read, and nothing polled it: the chrome's
        // messages from a RustKit view went nowhere.
        let page = page();
        let mut loaded = page.load_html("<p>chrome</p>");
        assert!(wait_recv(&mut loaded, Duration::from_secs(10)).unwrap().is_ok());
        let _ = page.poll();
        let mut posted = page.eval(r#"window.ipc.postMessage('{"cmd":"navigate","url":"https://example.com/"}'); 1"#);
        assert!(wait_recv(&mut posted, Duration::from_secs(5)).is_some());
        assert_eq!(
            ipc_payloads(&page, Duration::from_millis(300)),
            vec![r#"{"cmd":"navigate","url":"https://example.com/"}"#.to_string()],
            "a message from a script was not sent to the window"
        );
        let mut timer = page.eval("setTimeout(function () { window.ipc.postMessage('later'); }, 20); 1");
        assert!(wait_recv(&mut timer, Duration::from_secs(5)).is_some());
        assert_eq!(
            ipc_payloads(&page, Duration::from_millis(500)),
            vec!["later".to_string()],
            "a message from a timer was not sent to the window"
        );
    }

    #[test]
    fn a_superseded_navigation_drops_the_late_result() {''')
open(p, 'w').write(s)
print('ok')
