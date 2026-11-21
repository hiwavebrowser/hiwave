<p align="center">
  <img src="https://raw.githubusercontent.com/hiwavebrowser/hiwave-windows/master/docs/logo.png" alt="HiWave" width="140" />
</p>

<h1 align="center">HiWave</h1>

<p align="center">
  <strong>Focus. Flow. Freedom.</strong><br>
  A privacy-first browser built from scratch in Rust — designed to help you browse less, not more.
</p>

<p align="center">
  <a href="#platform-status">Status</a> •
  <a href="#recent-progress">Progress</a> •
  <a href="#what-is-hiwave">What is HiWave?</a> •
  <a href="#downloads">Downloads</a> •
  <a href="#platforms">Platforms</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#support-the-project">Support</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/engine-RustKit_(original)-orange" alt="Engine: RustKit" />
  <img src="https://img.shields.io/badge/status-alpha-blueviolet" alt="Status: Alpha" />
  <img src="https://img.shields.io/badge/license-AGPL--3.0--or--later-blue" alt="License: AGPL-3.0-or-later" />
</p>

<p align="center">
  <a href="https://github.com/hiwavebrowser/hiwave/actions/workflows/parity-unified.yml">
    <img src="https://github.com/hiwavebrowser/hiwave/actions/workflows/parity-unified.yml/badge.svg" alt="Parity Tests" />
  </a>
</p>

<p align="center">
  <img src="badges/parity-overall.svg" alt="Overall Parity" />
  <img src="badges/perf-score.svg" alt="Performance" />
</p>

---

## Platform Status

| Platform | Build | Parity | Tests | Performance |
|----------|-------|--------|-------|-------------|
| macOS | ![Build](badges/build-macos.svg) | ![Parity](badges/parity-macos.svg) | ![Tests](badges/tests-macos.svg) | ![Perf](badges/perf-macos.svg) |
| Windows | ![Build](badges/build-windows.svg) | ![Parity](badges/parity-windows.svg) | ![Tests](badges/tests-windows.svg) | ![Perf](badges/perf-windows.svg) |
| Linux | ![Build](badges/build-linux.svg) | ![Parity](badges/parity-linux.svg) | ![Tests](badges/tests-linux.svg) | ![Perf](badges/perf-linux.svg) |

**Reading this table honestly:** the three platforms measure different things
today. macOS numbers are visual-parity cases (pixel comparison against Chrome);
Windows and Linux numbers are `cargo test` results from each platform's CI. A
"no data" parity badge means parity has genuinely never been captured on that
platform — it is not inferred from anything else, and a passing build is never
evidence of pixel fidelity. Details in
[How these numbers are produced](#how-these-numbers-are-produced).

The macOS parity badge reads from a metrics feed that has not been refreshed,
so it shows a stale figure. The measured macOS numbers are the ones below.

### V1.6.0 on all three platforms (2026-11-21)

All three platforms ship the same RustKit engine (hiwave-macos `develop` through batch 117). macOS is the reference tree, where engine work lands first. Windows and Linux are synced from it and measured against Chrome for Testing 148 on their own OS.

| | macOS | Linux | Windows |
|---|---|---|---|
| Browser-interface board, rows matching Chrome 148 | 41 / 42 | 42 / 42 | 17 / 42 |
| Mean elements out of place on that board | — | 2.2 | 65 |
| Test suite at the release head | 2,911 headless engine tests passing | 6,528 passing, 33 known failures, 0 unexpected | CI green, 162 native shell tests |
| Release notes | [V1.6.0](https://github.com/hiwavebrowser/hiwave-macos/releases/tag/V1.6.0) | [V1.6.0 (Linux)](https://github.com/hiwavebrowser/hiwave-linux/releases/tag/V1.6.0) | [V1.6.0 (Windows)](https://github.com/hiwavebrowser/hiwave-windows/releases/tag/V1.6.0) |

macOS also measures:
- **Fixed-page campaign:** 26 / 26 cases, 0.405% mean pixel difference from Chrome 148.
- **Real-window interaction checks:** 570 pass, 1 fail, 1 not run, in each of two runs.
- **test262:** 96,520 of 103,352 runs pass (93.39%).

New this release:
- Large scripts run: the per-script limit is 16 MiB, so YouTube's and Netflix's main bundles execute.
- CSS transitions cover many more properties.
- Animation timing runs on one 60 Hz page clock.
- Canvas 2D gains `getImageData` and `putImageData`.
- Floats, box shadows and `<select>` render closer to Chrome.
- Linux text line metrics match Chrome's, which took the Linux board from 22 to 42 of 42 rows matching.

Known gaps:
- youtube.com runs its bundle but stops at a startup error.
- Windows text measurement still trails macOS and Linux.
- JavaScript coverage is partial.
- There is no WebAssembly and no media playback, and same-origin iframes are behind a flag.

**Per-platform engine status** (what actually renders, what is parsed-but-inert,
known gaps): see each platform README —
[Windows](https://github.com/hiwavebrowser/hiwave-windows#readme) · [macOS](https://github.com/hiwavebrowser/hiwave-macos#readme) ·
[Linux](https://github.com/hiwavebrowser/hiwave-linux#readme).

## Recent progress

Status as of 2026-11-16, macOS tree. Details and a source for every number:
[docs/PROGRESS-2026-11.md](docs/PROGRESS-2026-11.md).

- **Releases:** V1.6.0 on all three platforms on 2026-11-21; on macOS, V1.5.0 on 2026-11-14, after V1.4.0 (10-24), V1.3.0 (10-12), V1.2.0 (10-02) and V1.1.0 (09-24).
- **Gated batches:** since 2026-11-02 every change to hiwave-macos lands in a batch. Each pull request is reviewed independently, and the batch merges only after one combined gate on a Mac: unit and integration suites, a 26-page capture campaign, a 42-state board of the browser's own interface, a 19-site A/B run against the previous build, a Web Platform Tests subset, and two passes of 572 real-window interaction checks. Batch numbering reached 95 on 2026-11-16.
- **Tests:** the headless engine suite grew from 1,496 passing tests at batch 1 (2026-11-02) to 2,588 at `develop` `d4455b45` (2026-11-16); script bindings from 428 to 732; layout from 881 to 978.
- **Real window:** 570 of 572 interaction checks pass. Cmd+T and Cmd+W take 157 to 164 ms.
- **Frame pacing:** the real window went from about 52 to 60 frames per second in November. A 3-second probe counts 179 to 181 frames, the same count as Chrome on the same Mac.
- **Browser interface:** 39 of 42 interface states match the Chrome reference, up from 21 of 42 on 2026-11-09.
- **Behind a flag or planned:** same-origin iframes are on `develop` behind a flag, off by default. WebAssembly has an approved plan and has not shipped. A baseline JIT is at the plan stage, with no decision made.
- **Where the engine is behind:** the current priority is the stress suites (Speedometer, MotionMark, JetStream), and RustKit is not at Chrome's level on them. MotionMark now completes end to end; one run scored 52.16 overall, and two of its eight subtests still score at the floor. At V1.5.0 no stress suite produced a score.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="charts/commit-history-dark.svg">
  <img src="charts/commit-history.svg" alt="Weekly non-merge commits and merged pull requests on hiwave-macos, hiwave-windows and hiwave-linux from 29 December 2025 to 16 November 2026, with cumulative commits. The weeks starting 2 and 9 November have 665 and 928 commits and 171 and 219 merged pull requests." />
</picture>

The chart counts non-merge commits reachable from each platform repo's
`develop` branch, by author date, and merged pull requests by merge date, in
Monday-start weeks (UTC). Merge commits and this umbrella repo's automated
commits are not counted. The last bar is an unfinished week. Data fetched
2026-11-16: [`metrics/commit_history.json`](metrics/commit_history.json),
drawn by [`scripts/commit_history_chart.py`](scripts/commit_history_chart.py).

<details>
<summary>Parity Trend (click to expand)</summary>

![Parity Trend](charts/parity-trend.svg)

</details>

<details>
<summary>Performance Trend</summary>

![Performance Trend](charts/perf-trend.svg)

</details>

<details>
<summary>Platform Comparison</summary>

![Platform Comparison](charts/platform-comparison.svg)

</details>

<details>
<summary>Code Churn Analysis</summary>

View the interactive [**Churn Report Dashboard**](churn-reports/dashboard.html) to see:
- File modification frequency across all platforms
- Line range hotspots indicating areas of active development
- Cross-platform file synchronization patterns
- Divergent development patterns

*Updated weekly via GitHub Actions*

</details>

---

## Visual Parity Testing

RustKit is tested against pinned Chrome for Testing baselines (148 on macOS) using **triple verification**:

| Verification | Description | Weight |
|--------------|-------------|--------|
| **Pixel Diff** | Direct pixel comparison | Primary |
| **Layout Rects** | Element positioning accuracy | Secondary |
| **Computed Styles** | CSS property matching | Diagnostic |

### Platform Support

| Platform | Parity capture | Build + unit tests |
|----------|----------------|--------------------|
| macOS | Active — full headless parity testing | Not yet published to the metrics feed |
| Windows | Pending — awaiting headless rendering port | Published from CI (`metrics-history` branch) |
| Linux | Pending — awaiting headless rendering port | Published from CI (`metrics-history` branch) |

Windows and Linux run hundreds of `cargo test` engine tests in CI on every
master merge; those are real and drive the Build/Tests badges above. What they
do **not** yet have is pixel capture, so their parity badges stay "no data"
rather than borrowing a number from anywhere else.

### Test Cases (26 total)

| Category | Count | Cases |
|----------|-------|-------|
| Built-ins | 5 | `new_tab`, `about`, `settings`, `chrome_rustkit`, `shelf` |
| Websuite | 8 | `article-typography`, `card-grid`, `css-selectors`, `flex-positioning`, `form-elements`, `gradient-backgrounds`, `image-gallery`, `sticky-scroll` |
| Micro-tests | 13 | `backgrounds`, `bg-pure`, `bg-solid`, `combinators`, `form-controls`, `gpu-gradient-regression`, `gradient-no-radius`, `gradient-radius-only`, `gradients`, `images-intrinsic`, `pseudo-classes`, `rounded-corners`, `specificity` |

The case list above is taken from the harness's own results file, not
maintained by hand — if it drifts from `parity_test_results.json`, the results
file wins.

### Running Parity Tests

```bash
# Run all tests with 3 iterations (macOS - fully supported)
cd hiwave-macos
python3 scripts/parity_swarm.py --scope all --iterations 3

# Windows/Linux parity tests require parity-capture binary
# which is currently only available on macOS.
# Scripts exist but will fail until headless support is ported.

# Run with Xvfb (Linux - once headless support is ported)
cd hiwave-linux
xvfb-run python3 scripts/parity_swarm.py --scope all
```

*The scheduled [parity workflow](https://github.com/hiwavebrowser/hiwave/actions/workflows/parity-unified.yml) last completed on 2026-11-05; its runs since then were cancelled. Current macOS figures come from the batch gate described in [Recent progress](#recent-progress).*

---

## How these numbers are produced

Every number on this page has a path back to a machine that measured it. If a
number has no such path, it does not get published — "no data" is a valid and
honest state.

| Number | Producer | Where it lives | Consumer |
|--------|----------|----------------|----------|
| macOS parity % | Headless pixel capture vs Chrome baselines (`parity_swarm.py`) | `hiwave-macos` parity artefacts | [`collect_metrics.py`](scripts/collect_metrics.py) |
| Windows build + tests | Windows CI on master merges | [`hiwave-windows@metrics-history`](https://github.com/hiwavebrowser/hiwave-windows/tree/metrics-history) (`metrics/history.csv`, append-only) | same |
| Linux build + tests | Linux CI on master merges | [`hiwave-linux@metrics-history`](https://github.com/hiwavebrowser/hiwave-linux/tree/metrics-history) (`metrics/history.csv`, append-only) | same |
| Badges | [`generate_badges.py`](scripts/generate_badges.py) from `metrics/unified.json` | [`badges/`](badges/) | this README |

The aggregation runs in [`metrics.yml`](.github/workflows/metrics.yml) (daily,
and on dispatch from the platform repos). Rules the pipeline enforces rather
than trusts anyone to remember:

- **Numbers fail closed.** If a feed is unreachable, the platform publishes
  NOT-MEASURED. Nothing is hand-filled, estimated, or carried forward as if
  fresh.
- **Only `master` rows drive public numbers.** A newer measurement from a PR
  branch never wins.
- **Build status is read, never inferred.** A parity number existing is not
  evidence the build passes, and vice versa.
- **Measurements carry their own commit and timestamp.** A number older than
  its badge admits it (`… · Nd stale`) instead of posing as current.
- **Different test ontologies never share a denominator.** macOS parity cases
  and Windows/Linux cargo tests are counted separately, and the overall badge
  names its source when both exist.

---

## What is HiWave?

**HiWave** is a new kind of browser — one that respects your attention and privacy.

While most browsers are designed to keep you scrolling endlessly, HiWave actively helps you:
- 🧹 **Close tabs** with The Shelf — park tabs that fade with age
- 🛡️ **Block trackers** at the engine level — no extensions needed
- 🗃️ **Separate contexts** with Workspaces — work stays work, personal stays personal
- ⌨️ **Navigate fast** with keyboard-first design

### Built Different

Unlike Chrome, Firefox, or Safari, **HiWave runs on RustKit** — our own browser engine written in Rust. HTML, CSS, layout, painting and the web APIs are the project's own code; JavaScript runs on a vendored copy of the open-source Boa engine, also written in Rust.

⚠️ **RustKit Development Status**: RustKit is actively under development and may contain rendering bugs and visual inconsistencies. For the most stable experience, use the WebView/WebKit variants which rely on system rendering engines. RustKit variants are recommended for testing and development purposes.

---

## Downloads

Pre-built binaries are available for all platforms with multiple rendering backend options:

### 📦 [Latest Weekly Build](https://github.com/hiwavebrowser/hiwave/releases/latest) (built every Monday from the pinned platform commits)
### 📦 [Nightly Build](https://github.com/hiwavebrowser/hiwave/releases/tag/nightly) (last built 2026-07-10; the nightly workflow is failing)

Platform releases with full notes are published in each platform repo: [macOS](https://github.com/hiwavebrowser/hiwave-macos/releases), [Linux](https://github.com/hiwavebrowser/hiwave-linux/releases), [Windows](https://github.com/hiwavebrowser/hiwave-windows/releases).

### Build Variants

Each platform offers multiple build variants with different rendering backends:

#### 🪟 Windows
- **`hiwave-windows-rustkit`** — RustKit hybrid mode (RustKit for content, WebView2 for UI) ⚠️ *In Development*
- **`hiwave-windows-webview2`** — WebView2 fallback (uses Edge Chromium for all rendering) ✅ *Stable*
- **`hiwave-windows-native-win32`** — 100% RustKit native Win32 (experimental) 🚧 *Experimental*

#### 🍎 macOS
- **`hiwave-macos-rustkit`** — RustKit renders every page ⚠️ *In Development*. For the state of the browser's own interface, see the [hiwave-macos README](https://github.com/hiwavebrowser/hiwave-macos#readme). The WebKit-for-content fallback was removed in October 2026: on macOS, pages always render in RustKit.

#### 🐧 Linux
- **`hiwave-linux-webview`** — GTK WebKit2 (uses system WebKit for all rendering) ✅ *Stable*
- **`hiwave-linux-rustkit`** — RustKit hybrid mode (experimental) 🚧 *Experimental*
- **`hiwave-linux-native-linux`** — 100% RustKit native (experimental) 🚧 *Experimental*

**Recommendation**: On Windows and Linux, choose the **WebView2/WebKit variants** for daily use. On macOS, RustKit is the only content engine; treat it as alpha. RustKit variants are for testing and development as the engine continues to mature.

### Installation & Usage Instructions

#### 🪟 Windows

1. **Download** the desired `.zip` file from the releases page
2. **Extract** the zip file to a location of your choice (e.g., `C:\Program Files\HiWave\`)
3. **Run** `hiwave.exe`

**Security Warning (First Launch):**
- Windows will likely show a "Windows protected your PC" SmartScreen warning because the binary is not signed with a code signing certificate
- Click **"More info"** → **"Run anyway"** to proceed
- This warning appears only on first launch

**Alternative:** Right-click `hiwave.exe` → **Properties** → **Unblock** checkbox → **Apply** → **OK** (before first run)

**Note:** The `webview2` variant requires Microsoft Edge WebView2 Runtime. Windows 11 includes this by default. For Windows 10, it will be installed automatically on first run if missing.

#### 🍎 macOS

1. **Download** the desired `.zip` file from the releases page
2. **Extract** the zip file (double-click in Finder)
3. **Move** `hiwave.app` (if applicable) to your Applications folder, or run the binary directly

**Security Warning (Required for Unsigned Apps):**
- macOS Gatekeeper will block unsigned applications
- When you first try to open HiWave, you'll see **"HiWave cannot be opened because it is from an unidentified developer"**

**To allow HiWave to run:**

**Option 1 (Recommended):**
1. Open **System Settings** → **Privacy & Security**
2. Scroll down to the **Security** section
3. You should see a message about HiWave being blocked with an **"Open Anyway"** button
4. Click **"Open Anyway"** and confirm with your password

**Option 2 (Command Line):**
```bash
# Remove quarantine attribute
xattr -dr com.apple.quarantine /path/to/hiwave

# Or for the app bundle
xattr -dr com.apple.quarantine /Applications/HiWave.app
```

**Option 3 (Control-Click):**
1. Hold **Control** and click the HiWave application
2. Select **"Open"** from the context menu
3. Click **"Open"** in the confirmation dialog

⚠️ **Note:** These security warnings appear because HiWave is not currently code-signed with an Apple Developer certificate. This is standard for open-source projects distributed as pre-built binaries.

#### 🐧 Linux

1. **Download** the desired `.zip` file from the releases page
2. **Extract** the zip file:
   ```bash
   unzip hiwave-linux-*.zip
   ```
3. **Make executable** (if needed):
   ```bash
   chmod +x hiwave
   ```
4. **Run**:
   ```bash
   ./hiwave
   ```

**Dependencies:**
- The `webview` variant requires GTK 3, WebKit2GTK 4.1, and related libraries
- Install on Ubuntu/Debian:
  ```bash
  sudo apt-get install libgtk-3-0 libwebkit2gtk-4.1-0 libayatana-appindicator3-1
  ```
- Install on Fedora:
  ```bash
  sudo dnf install gtk3 webkit2gtk4.1
  ```
- Install on Arch:
  ```bash
  sudo pacman -S gtk3 webkit2gtk
  ```

**AppImage (Coming Soon):** We plan to provide AppImage builds that bundle all dependencies for easier distribution.

---

## Platforms

This repository is the umbrella project containing all HiWave components:

| Platform | Repository | Status |
|----------|------------|--------|
| 🪟 **Windows** | [hiwave-windows](https://github.com/hiwavebrowser/hiwave-windows) | Alpha — RustKit engine, synced from macOS. **V1.6.0** released 2026-11-21 |
| 🍎 **macOS** | [hiwave-macos](https://github.com/hiwavebrowser/hiwave-macos) | Alpha — RustKit engine; the reference platform. **V1.6.0** released 2026-11-21 |
| 🐧 **Linux** | [hiwave-linux](https://github.com/hiwavebrowser/hiwave-linux) | Alpha — RustKit engine, synced from macOS. **V1.6.0** released 2026-11-21 |

Each platform is a git submodule pinned to that repo's `master`; each repo has its own README with platform-specific build instructions.

---

## Quick Start

### Option 1: Download Pre-built Binary (Recommended)

Download the latest release for your platform from the [Downloads](#downloads) section above. On Windows and Linux, choose a WebView2/WebKit variant for daily use.

### Option 2: Build from Source

#### Clone with Submodules

```bash
git clone --recursive https://github.com/hiwavebrowser/hiwave.git
cd hiwave
```

#### Windows
```powershell
cd hiwave-windows

# Build variants:
cargo build --release --no-default-features --features rustkit          # RustKit hybrid
cargo build --release --no-default-features --features webview-fallback # WebView2 (stable)
cargo build --release --no-default-features --features native-win32     # Native Win32
```

#### macOS
```bash
cd hiwave-macos

# Build variants:
cargo build --release --features rustkit                  # RustKit (the only content engine on macOS)
```

#### Linux
```bash
cd hiwave-linux

# Build variants:
cargo build --release --features webview-fallback              # GTK WebKit (stable)
cargo build --release --no-default-features --features rustkit # RustKit hybrid
cargo build --release --no-default-features --features native-linux # Native
```

See each platform's README for detailed build instructions and development setup.

---

## Contributing

**We'd love your help!** HiWave is an ambitious project and there's plenty to do.

### 🐛 Found a Bug?

[**Open an Issue**](https://github.com/hiwavebrowser/hiwave/issues/new?labels=bug) — Tell us what went wrong. Include:
- What you expected vs. what happened
- Steps to reproduce
- Your OS and HiWave version

### 💡 Have an Idea?

[**Submit a Feature Request**](https://github.com/hiwavebrowser/hiwave/issues/new?labels=enhancement) — We want to hear it! Great ideas come from users.

### 🔧 Want to Code?

1. Fork the repo
2. Check the issues labeled [`good first issue`](https://github.com/hiwavebrowser/hiwave/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
3. Submit a PR!

See [CONTRIBUTING.md](https://github.com/hiwavebrowser/hiwave-windows/blob/master/CONTRIBUTING.md) for development setup and guidelines.

### 📖 Improve the Docs

Documentation PRs are always welcome. If something confused you, it probably confuses others too.

---

## Support the Project

<p align="center">
  <a href="https://ko-fi.com/hiwavebrowser">
    <img src="https://img.shields.io/badge/☕_Buy_me_a_coffee-FF5E5B?style=for-the-badge&logo=ko-fi&logoColor=white" alt="Buy Me a Coffee" height="50" />
  </a>
</p>

**HiWave is free, open source, and ad-free.** We don't track you. We don't sell your data. We never will.

Building a browser from scratch is a massive undertaking. If HiWave helps you focus better or just makes you smile, consider buying us a coffee:

<p align="center">
  <strong>☕ <a href="https://ko-fi.com/hiwavebrowser">ko-fi.com/hiwavebrowser</a></strong>
</p>

Your support helps cover:
- ⏰ Development time (a LOT of it)
- 🖥️ Infrastructure and testing
- 🚀 Future features like HiWave Sync

Every coffee counts. Thank you! 💜

---

## Project Structure

```
hiwave/
├── hiwave-windows/     # Windows app (RustKit engine)
├── hiwave-macos/       # macOS app (RustKit engine)
├── hiwave-linux/       # Linux app (RustKit engine)
├── churn-report/       # Code churn analysis tool (submodule)
├── churn-reports/      # Generated churn analysis reports
├── community/          # Ways to help and collaborate
├── docs/               # Progress pages and design records
├── scripts/, metrics/, badges/, charts/   # Metrics pipeline and its generated output
└── README.md           # You are here
```

---

## License

HiWave is licensed under the [GNU Affero General Public License v3.0 or later](LICENSE) (AGPL-3.0-or-later). The source code is owned by Aleph Null LLC; HiWave is a subsidiary of Aleph Null LLC. See [NOTICE](NOTICE).

- ✅ Free to use, modify, and distribute
- ⚠️ If you distribute HiWave, or a modified version, you must make the complete corresponding source available under AGPL-3.0-or-later
- ⚠️ If you run a modified version for users over a network, you must offer them its source (AGPL section 13)

**Earlier versions:** versions of HiWave published before the move to AGPL-3.0-or-later were released under the Mozilla Public License 2.0 and remain available under it.

**Files under MPL-2.0:** a few files contain code contributed under MPL-2.0 by an outside contributor and stay under MPL-2.0. Each is marked `SPDX-License-Identifier: MPL-2.0`, and each platform repository lists its own in its `NOTICE`. In [hiwave-macos](https://github.com/hiwavebrowser/hiwave-macos): `crates/hiwave-app/src/main.rs`, `crates/hiwave-app/src/ipc/mod.rs`, `crates/hiwave-app/src/ipc/commands.rs`, `crates/hiwave-app/src/platform/macos.rs`, `crates/hiwave-app/src/ui/inspector.html`, `crates/hiwave-app/src/ui/inspector_inject.js`, `crates/hiwave-app/src/ui/console_inject.js`, `crates/hiwave-app/src/ui/context_menu.js`.

For commercial licensing options, see [COMMERCIAL-LICENSE.md](https://github.com/hiwavebrowser/hiwave-windows/blob/master/COMMERCIAL-LICENSE.md).

---

<p align="center">
  <strong>Built with 💜 for people who want to focus.</strong>
</p>

<p align="center">
  <a href="https://www.hiwavebrowser.com">Website</a> •
  <a href="https://github.com/hiwavebrowser/hiwave/issues">Issues</a> •
  <a href="https://ko-fi.com/hiwavebrowser">Support Us</a> •
  <a href="https://twitter.com/hiwavebrowser">Twitter</a>
</p>

