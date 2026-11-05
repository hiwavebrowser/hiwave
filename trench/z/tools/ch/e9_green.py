"""CH2.E9 green step: harvest fills ChromeUpdates; macOS loop sends them."""
root = '/Users/petecopeland/Repos/.worktrees/z-ch2-e9/crates/hiwave-app/src/'


def sub(s, old, new):
    assert s.count(old) == 1, old
    return s.replace(old, new, 1)


p = root + 'webview_rustkit.rs'
s = open(p).read()
s = sub(s, '''    /// Current title (cached).
    current_title: RefCell<Option<String>>,
''', '''    /// Current title (cached).
    current_title: RefCell<Option<String>>,
    /// What the chrome has not been told yet (CH2.E9).
    chrome_updates: RefCell<ChromeUpdates>,
''')
s = sub(s, '''            current_title: RefCell::new(None),
''', '''            current_title: RefCell::new(None),
            chrome_updates: RefCell::new(ChromeUpdates::default()),
''')
s = sub(s, '''    pub fn take_chrome_updates(&self) -> ChromeUpdates {
        ChromeUpdates::default()
    }
''', '''    /// Filled from the content thread's events, so only with the page on
    /// its own thread (the default); flag off the events are dropped.
    pub fn take_chrome_updates(&self) -> ChromeUpdates {
        if self.content.is_some() {
            self.harvest();
        }
        std::mem::take(&mut *self.chrome_updates.borrow_mut())
    }
''')
s = sub(s, '''                PageEvent::Title { text, .. } => {
                    *self.current_title.borrow_mut() = Some(text);
                }
                PageEvent::Url { url, .. } => {
                    *self.current_url.borrow_mut() = Some(url.to_string());
                }
                PageEvent::LoadState { state, .. } => {
                    *self.loading.borrow_mut() = matches!(state, LoadState::Started);
                }
''', '''                PageEvent::Title { text, .. } => {
                    self.chrome_updates.borrow_mut().title = Some(text.clone());
                    *self.current_title.borrow_mut() = Some(text);
                }
                PageEvent::Url { url, .. } => {
                    if shown_in_address_bar(&url) {
                        self.chrome_updates.borrow_mut().url = Some(url.to_string());
                    }
                    *self.current_url.borrow_mut() = Some(url.to_string());
                }
                PageEvent::LoadState { state, .. } => {
                    let mut updates = self.chrome_updates.borrow_mut();
                    match &state {
                        LoadState::Started => {
                            updates.started = true;
                            updates.loading = Some(true);
                        }
                        LoadState::Complete => {
                            updates.loading = Some(false);
                            let url = self.current_url.borrow().clone();
                            if let Some(url) = url.filter(|u| Url::parse(u).is_ok_and(|u| shown_in_address_bar(&u))) {
                                updates.finished = Some(url);
                            }
                        }
                        LoadState::Failed { .. } => updates.loading = Some(false),
                    }
                    *self.loading.borrow_mut() = matches!(state, LoadState::Started);
                }
''')
s = sub(s, '''fn stale(accepted: u64, event: &PageEvent) -> bool {''', '''/// A URL the address bar and the tab model take from the page. Documents
/// the app loads itself (New Tab, about, report) commit as `about:` or
/// `data:` URLs, and their tab keeps the address the app gave it.
fn shown_in_address_bar(url: &Url) -> bool {
    matches!(url.scheme(), "http" | "https" | "file")
}

fn stale(accepted: u64, event: &PageEvent) -> bool {''')
open(p, 'w').write(s)

p = root + 'main.rs'
s = open(p).read()
s = sub(s, '''                            let _ = click_proxy.send_event(UserEvent::Navigate(url));
                        }
                        // The page's console lines, and a new tree after it
''', '''                            let _ = click_proxy.send_event(UserEvent::Navigate(url));
                        }
                        // CH2.E9: what the page committed, as the WebKit
                        // content view's handlers report it off macOS. Until
                        // 2026-11-05 nothing read these on macOS: the address
                        // bar kept the typed URL after a redirect, and the tab
                        // never got its title, its spinner's end or a visit.
                        {
                            use crate::webview::IWebContent as _;
                            let updates = view.take_chrome_updates();
                            if let Some(url) = updates.url {
                                let _ = click_proxy.send_event(UserEvent::UpdateUrl(url.clone()));
                                let _ = click_proxy.send_event(UserEvent::UpdateActiveTabUrl(url));
                                let _ = click_proxy.send_event(UserEvent::NavigationStateChanged {
                                    can_go_back: view.can_go_back(),
                                    can_go_forward: view.can_go_forward(),
                                });
                            }
                            if let Some(title) = updates.title {
                                let _ = click_proxy.send_event(UserEvent::UpdateTitle(title));
                            }
                            if updates.started {
                                let _ = click_proxy.send_event(UserEvent::SetLoading(true));
                            }
                            if updates.loading == Some(false) {
                                let _ = click_proxy.send_event(UserEvent::SetLoading(false));
                                let _ = click_proxy.send_event(UserEvent::SyncShieldStats);
                            }
                            if let Some(url) = updates.finished {
                                let _ = click_proxy.send_event(UserEvent::RecordVisit { url });
                            }
                        }
                        // The page's console lines, and a new tree after it
''')
# The WebKit helpers are injected at load end off macOS only: on macOS the
# content view is RustKit and these scripts were never run there.
s = sub(s, '''                        // Inject context menu handler and audio detector when page finishes loading
                        if !loading {''', '''                        // Inject context menu handler and audio detector when page finishes loading.
                        // Not on macOS: the content view is RustKit, which never
                        // ran these WebKit helpers (no SetLoading was sent there
                        // before CH2.E9), and they post to the WebKit IPC.
                        #[cfg(not(target_os = "macos"))]
                        if !loading {''')
open(p, 'w').write(s)
print('ok')
