"""CH2.E9 part 2 green: window.ipc into a Rust queue; content thread pushes PageEvent::Ipc."""
root = '/Users/petecopeland/Repos/.worktrees/z-ch2-e9/crates/'


def edit(path, pairs):
    s = open(path).read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old)
        s = s.replace(old, new, 1)
    open(path, 'w').write(s)


edit(root + 'rustkit-bindings/src/lib.rs', [
    ('''    /// Queue of IPC messages from JavaScript
    _ipc_queue: RefCell<Vec<IpcMessage>>,
''', '''    /// What the page posted with `window.ipc.postMessage`, held on the
    /// Rust side (`__rk_ipc_post`), so a drain runs no script.
    ipc_queue: Rc<RefCell<Vec<IpcMessage>>>,
'''),
    ('''            _ipc_queue: RefCell::new(Vec::new()),
''', '''            ipc_queue,
'''),
    ('''        runtime.evaluate_with_host(include_str!("web_animations.js"))?;

        Ok(Self {''', '''        runtime.evaluate_with_host(include_str!("web_animations.js"))?;
        // `window.ipc.postMessage` lands here (CH2.E9).
        let ipc_queue = Rc::new(RefCell::new(Vec::new()));
        let queue = Rc::clone(&ipc_queue);
        runtime.register_host_function(
            "__rk_ipc_post",
            1,
            Box::new(move |args| {
                if let Some(JsValue::String(payload)) = args.first() {
                    queue.borrow_mut().push(IpcMessage { payload: payload.clone() });
                }
                JsValue::Undefined
            }),
        )?;

        Ok(Self {'''),
    ('''            // IPC queue for postMessage calls
            window.__ipcQueue = [];

            // IPC object for browser-to-Rust communication
            window.ipc = {
                postMessage: function(message) {
                    // Store message in queue for Rust to poll
                    window.__ipcQueue.push(message);
                }
            };

            // Helper to drain the IPC queue (called from Rust)
            window.__drainIpcQueue = function() {
                var queue = window.__ipcQueue;
                window.__ipcQueue = [];
                return JSON.stringify(queue);
            };
''', '''            // IPC object for browser-to-Rust communication. The message
            // goes to a queue on the Rust side (`__rk_ipc_post`, installed
            // after the globals); a non-string is sent as its JSON.
            window.ipc = {
                postMessage: function(message) {
                    __rk_ipc_post(typeof message === 'string' ? message : JSON.stringify(message));
                }
            };
'''),
])

s = open(root + 'rustkit-bindings/src/lib.rs').read()
start = s.index('    pub fn drain_ipc_queue(&self) -> Vec<IpcMessage> {')
end = s.index('    /// Add an event listener.', start)
s = s[:start] + '''    pub fn drain_ipc_queue(&self) -> Vec<IpcMessage> {
        std::mem::take(&mut *self.ipc_queue.borrow_mut())
    }

    /// Check if there are pending IPC messages.
    pub fn has_pending_ipc(&self) -> bool {
        !self.ipc_queue.borrow().is_empty()
    }

''' + s[end:]
open(root + 'rustkit-bindings/src/lib.rs', 'w').write(s)

edit(root + 'rustkit-engine/src/lib.rs', [
    ('''    /// Check if any view has pending IPC messages.
    pub fn has_pending_ipc(&self) -> bool {''', '''    /// What `id`'s page posted with `window.ipc.postMessage` since the
    /// last drain.
    pub fn drain_view_ipc(&self, id: EngineViewId) -> Vec<IpcMessage> {
        self.views
            .get(&id)
            .and_then(|view| view.bindings.as_ref())
            .map(|bindings| bindings.drain_ipc_queue())
            .unwrap_or_default()
    }

    /// Check if any view has pending IPC messages.
    pub fn has_pending_ipc(&self) -> bool {'''),
])

edit(root + 'rustkit-engine/src/page_protocol.rs', [
    ('''        self.report_focus();
        self.report_script_navigation();
    }
''', '''        self.report_focus();
        self.report_script_navigation();
        self.report_ipc();
    }

    /// Send the window what the page posted on `window.ipc` (CH2.E9).
    /// Only the content thread reports it; the queue is Rust-side, so an
    /// empty one costs no script.
    fn report_ipc(&mut self) {
        if !self.wake_window {
            return;
        }
        let messages = self.engine.drain_view_ipc(self.view);
        if messages.is_empty() {
            return;
        }
        let nav_id = self.engine.nav_id(self.view).unwrap_or(0);
        for message in messages {
            self.emit(PageEvent::Ipc { payload: message.payload, nav_id });
        }
    }
'''),
])

edit(root + 'hiwave-app/src/webview_rustkit.rs', [
    ('''    /// What the chrome has not been told yet (CH2.E9).
    chrome_updates: RefCell<ChromeUpdates>,
''', '''    /// What the chrome has not been told yet (CH2.E9).
    chrome_updates: RefCell<ChromeUpdates>,
    /// What the page posted on `window.ipc`, in order (CH2.E9).
    ipc_inbox: RefCell<Vec<String>>,
'''),
    ('''            chrome_updates: RefCell::new(ChromeUpdates::default()),
''', '''            chrome_updates: RefCell::new(ChromeUpdates::default()),
            ipc_inbox: RefCell::new(Vec::new()),
'''),
    ('''                PageEvent::Ipc { .. } | PageEvent::Cursor(_) | PageEvent::Unresponsive | PageEvent::Closed => {}''',
     '''                PageEvent::Ipc { payload, .. } => self.ipc_inbox.borrow_mut().push(payload),
                PageEvent::Cursor(_) | PageEvent::Unresponsive | PageEvent::Closed => {}'''),
    ('''    pub fn take_script_navigation(&self) -> Option<(String, bool)> {''', '''    /// The messages the page posted with `window.ipc.postMessage` since
    /// the last call, oldest first (CH2.E9). Content thread only. The app
    /// must hand these to its command handler only for a view showing the
    /// app's own documents (chrome, shelf): a web page can post here too.
    pub fn take_ipc_messages(&self) -> Vec<String> {
        if self.content.is_some() {
            self.harvest();
        }
        std::mem::take(&mut *self.ipc_inbox.borrow_mut())
    }

    pub fn take_script_navigation(&self) -> Option<(String, bool)> {'''),
    ('''    /// A document the app loads itself keeps the address the app gave it.
''', '''    /// CH2.E9: the chrome's `window.ipc.postMessage` reaches the window.
    #[test]
    fn content_thread_the_window_takes_what_the_page_posts_on_window_ipc() {
        let view = content_view();
        view.load_html_internal(
            "<p>chrome</p><script>window.ipc.postMessage(JSON.stringify({cmd: 'navigate', url: 'https://example.com/'}));\\
             window.ipc.postMessage({cmd: 'get_version'});</script>",
        )
        .unwrap();
        let deadline = Instant::now() + Duration::from_secs(10);
        let mut got = Vec::new();
        while got.len() < 2 {
            assert!(Instant::now() < deadline, "the window got {got:?}");
            wake(&view);
            got.extend(view.take_ipc_messages());
            std::thread::sleep(Duration::from_millis(5));
        }
        assert_eq!(
            got,
            vec![
                r#"{"cmd":"navigate","url":"https://example.com/"}"#.to_string(),
                r#"{"cmd":"get_version"}"#.to_string(),
            ]
        );
    }

    /// A document the app loads itself keeps the address the app gave it.
'''),
])
print('ok')
