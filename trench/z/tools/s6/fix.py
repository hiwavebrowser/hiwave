#!/usr/bin/env python3
"""S6 fix: a sheet still loading at the subresource budget keeps loading as a live future and is
inserted at its document-order slot when it arrives, then the page is restyled."""
import sys
p = sys.argv[1] + '/crates/rustkit-engine/src/lib.rs'; s = open(p).read()


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, (s.count(a), a[:80])
    s = s.replace(a, b)


# 1. View fields.
rep("""    live_images: Vec<script_net::LiveFuture<FetchedImages>>,
""", """    live_images: Vec<script_net::LiveFuture<FetchedImages>>,
    /// External stylesheets still loading when the load's subresource
    /// budget ran out (Z row S6). Each keeps loading and lands at its
    /// document-order slot (the `usize`) on a live turn.
    live_sheets: Vec<script_net::LiveFuture<(usize, Option<Stylesheet>)>>,
    /// The document-order index of each entry of `external_stylesheets`,
    /// so a late sheet is inserted where the cascade expects it.
    external_sheet_slots: Vec<usize>,
""")
rep("""            live_images: Vec::new(),
""", """            live_images: Vec::new(),
            live_sheets: Vec::new(),
            external_sheet_slots: Vec::new(),
""", 3)
rep("""        self.live_images.clear();
        // The previous document's inserted scripts must not run here.""",
    """        self.live_images.clear();
        self.live_sheets.clear();
        self.external_sheet_slots.clear();
        // The previous document's inserted scripts must not run here.""")

# 2. Fetch: per-sheet futures own what they use, so a late one can outlive the load.
old_start = """    /// Load external stylesheets asynchronously.
    pub async fn load_external_stylesheets(
        &mut self,
        id: EngineViewId,
    ) -> Result<Vec<Stylesheet>, EngineError> {"""
old_end = """        Ok(fetched.into_iter().flatten().collect())
    }
"""
i = s.index(old_start); j = s.index(old_end, i) + len(old_end)
new = '''    /// Load external stylesheets asynchronously.
    pub async fn load_external_stylesheets(
        &mut self,
        id: EngineViewId,
    ) -> Result<Vec<Stylesheet>, EngineError> {
        let (sheets, _late) = self.load_external_stylesheets_slotted(id).await?;
        Ok(sheets.into_iter().map(|(_, sheet)| sheet).collect())
    }

    /// The external stylesheets that arrived within the subresource budget,
    /// each with its document-order index, and the fetches still out at the
    /// budget, which keep going (Z row S6: they used to be dropped, and a
    /// page whose sheets came late stayed unstyled).
    async fn load_external_stylesheets_slotted(
        &mut self,
        id: EngineViewId,
    ) -> Result<LoadedSheets, EngineError> {
        let view = self.views.get(&id).ok_or(EngineError::ViewNotFound(id))?;

        let Some(document) = &view.document else {
            return Ok((Vec::new(), Vec::new()));
        };

        let base_url = view.url.as_ref();
        let urls = self.discover_external_stylesheets(document.as_ref(), base_url);

        // Fetch concurrently, but keep DOCUMENT ORDER in the result: the
        // cascade depends on stylesheet order, so `buffered` (ordered) is
        // load-bearing here where images use `buffer_unordered`.
        use futures::stream::StreamExt;
        const MAX_CONCURRENT_CSS_LOADS: usize = 6;

        let deadline = self.subresource_deadline();
        let referrer = self.subresource_referrer(id);
        let fetches: Vec<_> = urls
            .into_iter()
            .enumerate()
            .map(|(index, url)| {
                let mut fetch: script_net::LiveFuture<Option<Stylesheet>> = Box::pin(Self::fetch_stylesheet(
                    self.loader.clone(),
                    view.inspector.clone(),
                    referrer.get_for(url.clone(), RequestDestination::Style),
                    url.clone(),
                    deadline,
                ));
                async move {
                    match tokio::time::timeout_at(deadline, &mut fetch).await {
                        Ok(sheet) => (index, Ok(sheet)),
                        Err(_) => {
                            warn!(%url, "Stylesheet over the subresource budget; it is applied when it arrives");
                            (index, Err(fetch))
                        }
                    }
                }
            })
            .collect();
        let fetched: Vec<_> = futures::stream::iter(fetches)
            .buffered(MAX_CONCURRENT_CSS_LOADS)
            .collect()
            .await;

        let mut sheets = Vec::new();
        let mut late = Vec::new();
        for (index, outcome) in fetched {
            match outcome {
                Ok(Some(sheet)) => sheets.push((index, sheet)),
                Ok(None) => {}
                Err(fetch) => late.push(Box::pin(async move { (index, fetch.await) })
                    as script_net::LiveFuture<(usize, Option<Stylesheet>)>),
            }
        }
        Ok((sheets, late))
    }

    /// Fetch and parse one external stylesheet. Owns what it uses, so a
    /// fetch still out at the load's budget can finish on a live turn.
    async fn fetch_stylesheet(
        loader: Arc<ResourceLoader>,
        inspector: Arc<Inspector>,
        request: Request,
        url: Url,
        deadline: tokio::time::Instant,
    ) -> Option<Stylesheet> {
        info!(%url, "Loading external stylesheet");
        // A sheet still loading at the deadline is recorded over budget.
        let guard = inspector
            .begin_request(&url, "GET", ResourceType::Stylesheet, Some("parser"))
            .map(|g| g.over_budget_at(deadline, "subresource budget spent"));
        match loader.fetch(request).await {
            Ok(response) => {
                let received = guard.map(|g| g.received(&response));
                if response.ok() {
                    let text = response.text().await;
                    if let Some(received) = received {
                        match &text {
                            Ok(css_text) => received.read(css_text.len()),
                            Err(_) => received.fail(FailureStage::Decode, "body is not UTF-8"),
                        }
                    }
                    match text {
                        Ok(css_text) => match {
                            let _style = wgate::bucket(wgate::HoldBucket::Style);
                            Stylesheet::parse(&absolutize_css_urls(&css_text, &url))
                        } {
                            Ok(stylesheet) => {
                                debug!(rules = stylesheet.rules.len(), %url, "Parsed external stylesheet");
                                Some(stylesheet)
                            }
                            Err(e) => {
                                warn!(?e, %url, "Failed to parse external stylesheet");
                                None
                            }
                        },
                        Err(e) => {
                            warn!(?e, %url, "Failed to read stylesheet body");
                            None
                        }
                    }
                } else {
                    if let Some(received) = received {
                        received.unread();
                    }
                    warn!(status = %response.status, %url, "Failed to fetch stylesheet");
                    None
                }
            }
            Err(e) => {
                inspector::fail_net(guard, &e);
                warn!(?e, %url, "Failed to fetch stylesheet");
                None
            }
        }
    }
'''
s = s[:i] + new + s[j:]

# 3. The load keeps the slots and parks the late fetches on the view.
rep("""        let Some(external_stylesheets) =
            nav_cancel::unless_cancelled(watch, self.load_external_stylesheets(id)).await
        else {
            return Ok(());
        };
        drop(sheets);
        let external_stylesheets = external_stylesheets?;
        let count = external_stylesheets.len();""",
    """        let Some(external_stylesheets) =
            nav_cancel::unless_cancelled(watch, self.load_external_stylesheets_slotted(id)).await
        else {
            return Ok(());
        };
        drop(sheets);
        let (external_stylesheets, late_sheets) = external_stylesheets?;
        let (slots, external_stylesheets): (Vec<usize>, Vec<Stylesheet>) = external_stylesheets.into_iter().unzip();
        let count = external_stylesheets.len();""")
rep("""            view.external_stylesheets = Rc::new(external_stylesheets);
            // Read, not taken:""",
    """            view.external_stylesheets = Rc::new(external_stylesheets);
            view.external_sheet_slots = slots;
            view.live_sheets = late_sheets;
            // Read, not taken:""")

# 4. Live turn: settle late sheets, insert in document order, restyle.
rep("""        let fetched = match self.views.get_mut(&id) {
            Some(view) => script_net::settle_live(&mut view.live_images, LIVE_NETWORK_SLICE).await,
            None => Vec::new(),
        };""",
    """        // External stylesheets that missed the load's budget (Z row S6):
        // each goes in at its document-order place, then the page restyles.
        let late_sheets = match self.views.get_mut(&id) {
            Some(view) => script_net::settle_live(&mut view.live_sheets, LIVE_NETWORK_SLICE).await,
            None => Vec::new(),
        };
        let mut sheets_arrived = 0;
        if let Some(view) = self.views.get_mut(&id) {
            for (index, sheet) in late_sheets {
                let Some(sheet) = sheet else { continue };
                let at = view.external_sheet_slots.partition_point(|&slot| slot < index);
                view.external_sheet_slots.insert(at, index);
                Rc::make_mut(&mut view.external_stylesheets).insert(at, sheet);
                sheets_arrived += 1;
            }
        }
        if sheets_arrived > 0 {
            info!(count = sheets_arrived, "Applied external stylesheets that arrived after the load");
            let fonts = self.load_local_web_fonts(id);
            if fonts > 0 {
                debug!(count = fonts, "Loaded web fonts from late stylesheets");
            }
            match self.relayout_for(id, RelayoutCause::StylesheetLoaded) {
                Ok(()) => out.relaid_out = true,
                Err(e) => debug!(?id, error = %e, "relayout after late stylesheets failed"),
            }
        }
        let fetched = match self.views.get_mut(&id) {
            Some(view) => script_net::settle_live(&mut view.live_images, LIVE_NETWORK_SLICE).await,
            None => Vec::new(),
        };""")
rep("""            out.in_flight += view.live_images.len();
        }
        if out.timers_ran > 0 || out.requests > 0 {""",
    """            out.in_flight += view.live_images.len() + view.live_sheets.len();
        }
        if out.timers_ran > 0 || out.requests > 0 {""")

# 5. Type alias near FetchedImages.
k = s.index("struct FetchedImages {")
k = s.rindex("\n\n", 0, k) + 2
s = s[:k] + """/// External stylesheets that arrived within the load's budget, each with its
/// document-order index, and the fetches still out at the budget.
type LoadedSheets = (
    Vec<(usize, Stylesheet)>,
    Vec<script_net::LiveFuture<(usize, Option<Stylesheet>)>>,
);

""" + s[k:]
open(p, 'w').write(s)
print('ok')
