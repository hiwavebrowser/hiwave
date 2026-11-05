"""CH3.A2 step 3a: HIWAVE_RUSTKIT_CHROME=1 builds the chrome as a RustKitView."""
root = '/Users/petecopeland/Repos/.worktrees/z-ch3-a2/crates/'


def edit(path, pairs):
    s = open(path).read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:80])
        s = s.replace(old, new, 1)
    open(path, 'w').write(s)


edit(root + 'rustkit-engine/src/presenter.rs', [
    ('''    pub fn raw_view(&self) -> isize {
        self.presenter.raw_view(self.viewhost_id)
    }
''', '''    pub fn raw_view(&self) -> isize {
        self.presenter.raw_view(self.viewhost_id)
    }

    /// The host view's id, which tags the input its NSView records.
    pub fn viewhost_id(&self) -> ViewId {
        self.viewhost_id
    }
'''),
])

edit(root + 'hiwave-app/src/webview_rustkit.rs', [
    ('''    pub fn take_ipc_messages(&self) -> Vec<String> {''', '''    /// The viewhost id the input of this view's NSView is tagged with.
    /// Content thread only (the flag-off engine owns its host view).
    pub fn input_view(&self) -> Option<rustkit_viewhost::ViewId> {
        self.surface.as_ref().map(|surface| surface.borrow().viewhost_id())
    }

    pub fn take_ipc_messages(&self) -> Vec<String> {'''),
])

p = root + 'hiwave-app/src/main.rs'
edit(p, [
    # The enum and its ChromeUi impl, after the Arc impl.
    ('''impl<T: ChromeUi + ?Sized> ChromeUi for Arc<T> {''', '''/// The chrome's view as built: WebKit, or RustKit with
/// `HIWAVE_RUSTKIT_CHROME=1` (macOS, content thread on; CH3.A2).
enum ChromeView {
    WebKit(WebView),
    #[cfg(all(target_os = "macos", feature = "rustkit"))]
    RustKit(webview_rustkit::RustKitView),
}

impl ChromeUi for ChromeView {
    fn eval(&self, js: &str) -> Result<(), String> {
        match self {
            ChromeView::WebKit(view) => view.eval(js),
            #[cfg(all(target_os = "macos", feature = "rustkit"))]
            ChromeView::RustKit(view) => view.wry_evaluate_script(js),
        }
    }

    fn place(&self, rect: Rect) {
        match self {
            ChromeView::WebKit(view) => view.place(rect),
            #[cfg(all(target_os = "macos", feature = "rustkit"))]
            ChromeView::RustKit(view) => {
                let _ = view.wry_set_bounds(rect);
            }
        }
    }
}

/// `HIWAVE_RUSTKIT_CHROME=1`: the chrome is a RustKit view (CH3.A2). Needs
/// the content thread, which is where a RustKit view's IPC arrives from.
fn rustkit_chrome_enabled() -> bool {
    cfg!(all(target_os = "macos", feature = "rustkit"))
        && std::env::var("HIWAVE_RUSTKIT_CHROME").map(|v| v == "1").unwrap_or(false)
        && rustkit_engine::content_thread_enabled()
}

/// The chrome document for a RustKit view: `JS_BRIDGE` (the WebKit view
/// runs it as an initialization script) as the head's first script.
fn chrome_html_with_bridge() -> String {
    let script = format!("<script>{}</script>", JS_BRIDGE);
    match CHROME_HTML.find("<head>") {
        Some(at) => {
            let at = at + "<head>".len();
            format!("{}{}{}", &CHROME_HTML[..at], script, &CHROME_HTML[at..])
        }
        None => format!("{}{}", script, CHROME_HTML),
    }
}

impl<T: ChromeUi + ?Sized> ChromeUi for Arc<T> {'''),
    # Build either view.
    ('''    let chrome_webview = WebViewBuilder::new()
        .with_html(CHROME_HTML)''', '''    #[cfg(all(target_os = "macos", feature = "rustkit"))]
    let rustkit_chrome = if rustkit_chrome_enabled() {
        info!("HIWAVE_RUSTKIT_CHROME=1: the chrome is a RustKit view");
        let bounds = rustkit_viewhost::Bounds::new(
            chrome_bounds.position.to_logical::<f64>(1.0).x as i32,
            chrome_bounds.position.to_logical::<f64>(1.0).y as i32,
            chrome_bounds.size.to_logical::<f64>(1.0).width as u32,
            chrome_bounds.size.to_logical::<f64>(1.0).height as u32,
        );
        let view = webview_rustkit::RustKitView::new(&window, bounds)
            .expect("Failed to create the RustKit chrome view");
        view.load_html_internal(&chrome_html_with_bridge())
            .expect("Failed to load the chrome into RustKit");
        Some(ChromeView::RustKit(view))
    } else {
        None
    };
    #[cfg(not(all(target_os = "macos", feature = "rustkit")))]
    let rustkit_chrome: Option<ChromeView> = None;
    let chrome_ipc_proxy = proxy.clone();
    let chrome_ipc_state = Arc::clone(&state);

    let chrome_webview = if let Some(view) = rustkit_chrome { view } else { ChromeView::WebKit(WebViewBuilder::new()
        .with_html(CHROME_HTML)'''),
    ('''        .build_as_child(&window)
        .expect("Failed to create HiWave WebView");
''', '''        .build_as_child(&window)
        .expect("Failed to create HiWave WebView")) };
'''),
    # Drive the chrome view each turn, and keep its input from the content view.
    ('''            Event::MainEventsCleared => {
                // Process RustKit events and render
''', '''            Event::MainEventsCleared => {
                // The RustKit chrome (CH3.A2): its page's messages go to the
                // chrome's command handler, as the WebKit view's do.
                let chrome_input = if let ChromeView::RustKit(ref chrome) = *chrome_for_events {
                    chrome.process_events();
                    for body in chrome.take_ipc_messages() {
                        handle_chrome_ipc(&body, &chrome_ipc_proxy, &chrome_ipc_state);
                    }
                    chrome.render();
                    chrome.input_view()
                } else {
                    None
                };
                // Process RustKit events and render
'''),
    ('''                        for event in rustkit_viewhost::drain_input() {
''', '''                        for event in rustkit_viewhost::drain_input() {
                            // Input on the RustKit chrome's view is not the
                            // page's. Not routed to the chrome yet (CH3.A2
                            // step 3b): dropped, never sent to the page.
                            if chrome_input == Some(event.view) {
                                continue;
                            }
'''),
])
print('ok')
