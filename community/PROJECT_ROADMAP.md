# HiWave Project Roadmap

> **Status note, 2026-11-16.** This page was written in January 2026. Its parity percentages, phase labels and dates describe the project at that time and have not been re-measured. For current, sourced figures see [Recent progress](https://github.com/hiwavebrowser/hiwave/blob/master/docs/PROGRESS-2026-11.md). Two rows are known to be out of date: page JavaScript already runs (on a vendored copy of the Boa engine), and an Inspector with Elements and Console panels shipped in hiwave-macos V1.4.0. Links to the `hiwavebrowser/community` Discussions do not currently resolve.

A technical roadmap for building a complete, independent browser — one "impossible" component at a time.

---

## The Big Picture

Modern browsers have several major components, each considered a massive engineering undertaking:

| Component | Chrome's Implementation | Their Engineers | Status in HiWave |
|-----------|------------------------|-----------------|------------------|
| Rendering Engine | Blink | 500+ | **In Progress** (RustKit) |
| JavaScript Engine | V8 | 300+ | Up for Vote |
| Networking Stack | Chromium Net | 100+ | Up for Vote |
| DevTools | Chrome DevTools | 100+ | Up for Vote |
| Extension System | Chrome Extensions API | 50+ | Up for Vote |
| Security Sandbox | Chrome Sandbox | 50+ | Up for Vote |
| Media Stack | Chromium Media | 50+ | Up for Vote |

Each of these has been called "impossible" to build from scratch. We're proving them wrong, one component at a time.

---

## How This Roadmap Works

**Phase 1 (Rendering Engine) is the current focus.** Everything else is up to the community.

Once we hit 99%+ pixel parity, the community will vote on what comes next. This is *your* browser — you decide what matters.

### Voting Process

1. **Propose**: Anyone can propose a new phase or modify an existing one
2. **Discuss**: Community discusses pros, cons, and implementation approaches
3. **Vote**: When Phase 1 completes, we'll hold a community vote for Phase 2
4. **Build**: Top-voted phase becomes the next focus

### Why Community-Driven?

Different people want different things:
- Some want extension support to use their favorite tools
- Some want a JS engine for true independence from Google
- Some want DevTools to use HiWave for web development
- Some want maximum privacy and minimal features

There's no "right" answer. The community decides.

**[Vote on Future Phases](https://github.com/hiwavebrowser/community/discussions/categories/roadmap-voting)** (opens after Phase 1)

---

## Phase 1: Rendering Engine (Current)

### Goal: 99%+ Pixel Parity with Chrome

**Status: 59% in January 2026** (not re-measured on this scale; see the status note above)

The rendering engine (RustKit) is the foundation. It takes HTML, CSS, and assets and turns them into pixels on screen.

#### Milestones

| Milestone | Target | Status |
|-----------|--------|--------|
| Core layout (block, inline) | 80% | Done |
| Flexbox | 80% | In Progress |
| CSS Grid | 80% | In Progress |
| Text rendering | 90% | In Progress |
| Images & replaced elements | 80% | In Progress |
| Forms & inputs | 80% | Planned |
| Transforms & animations | 70% | Planned |
| **Overall parity** | **80%** | **59%** |
| Polish & edge cases | 95% | Planned |
| Production ready | 99% | Planned |

#### What "Done" Looks Like
- Render the top 10,000 websites indistinguishably from Chrome
- Pass 95%+ of the CSS test suite
- Handle edge cases gracefully (no crashes, reasonable fallbacks)

---

## Candidate Phases (Community Vote)

The following are potential future directions. After Phase 1, the community will vote on priorities. These may be built in any order, combined, or skipped entirely based on what the community wants.

---

## Candidate: JavaScript Engine

### Goal: Build a Fast, Modern JS Engine from Scratch

**Status: Awaiting Community Vote**

This is what everyone says is truly impossible. Let's look at the competition:

| Engine | Browser | Engineers | Key Features |
|--------|---------|-----------|--------------|
| V8 | Chrome | 300+ | JIT, TurboFan, Ignition |
| SpiderMonkey | Firefox | 150+ | JIT, Warp, IonMonkey |
| JavaScriptCore | Safari | 100+ | JIT, FTL, B3 |

These engines have:
- Multiple JIT compilation tiers
- Sophisticated garbage collectors
- Billions of dollars of investment

**Our approach: Start simple, get correct, then get fast.**

#### Phase 2a: Interpreter (WaveScript Core)

Build a correct, spec-compliant JavaScript interpreter first:

| Component | Description | Complexity |
|-----------|-------------|------------|
| Lexer/Parser | ES2024+ syntax support | Medium |
| AST | Abstract syntax tree representation | Medium |
| Bytecode compiler | Convert AST to bytecode | Medium |
| Bytecode interpreter | Execute bytecode | Medium |
| Built-in objects | Array, Object, String, etc. | High |
| Standard library | Math, JSON, Date, etc. | Medium |
| Garbage collector | Mark-and-sweep to start | High |
| ES6+ features | Classes, modules, async/await, etc. | High |

**Target: Run jQuery, Lodash, and simple web apps**

#### Phase 2b: Baseline JIT

Add a simple JIT compiler for hot code paths:

| Component | Description | Complexity |
|-----------|-------------|------------|
| Type profiling | Track variable types at runtime | Medium |
| Baseline compiler | Fast, simple machine code generation | High |
| OSR | On-stack replacement (interpreter → JIT) | High |
| Deoptimization | Fall back when assumptions fail | High |

**Target: 10-50x speedup over interpreter for hot loops**

#### Phase 2c: Optimizing JIT

Build a sophisticated optimizing compiler:

| Component | Description | Complexity |
|-----------|-------------|------------|
| IR | Intermediate representation | High |
| Type inference | Speculative type optimization | Very High |
| Inlining | Function inlining | High |
| Escape analysis | Stack allocation for objects | Very High |
| Loop optimizations | LICM, unrolling, vectorization | Very High |
| Code generation | Architecture-specific backends | Very High |

**Target: Competitive with V8 on benchmarks**

#### Phase 2d: Advanced Features

| Component | Description | Complexity |
|-----------|-------------|------------|
| WebAssembly | WASM execution | Very High |
| Concurrent GC | Minimize pause times | Very High |
| Tiered compilation | Multiple optimization levels | High |
| Debugging support | Source maps, breakpoints | High |

#### What "Done" Looks Like
- Run React, Vue, Angular applications
- Score within 2x of V8 on major benchmarks
- Handle real-world websites without issues
- WebAssembly support for games and apps

---

## Candidate: Networking Stack

### Goal: Modern, Secure, Fast Networking

**Status: Awaiting Community Vote**

Currently using system networking. Building our own enables:
- Better performance (connection pooling, prioritization)
- Privacy features (built-in tracker blocking)
- Modern protocols (HTTP/3, QUIC)

#### Components

| Component | Description | Priority |
|-----------|-------------|----------|
| HTTP/1.1 | Legacy support | P0 |
| HTTP/2 | Multiplexing, header compression | P0 |
| HTTP/3 / QUIC | UDP-based, faster connections | P1 |
| TLS 1.3 | Modern encryption | P0 |
| DNS over HTTPS | Private DNS resolution | P1 |
| Certificate handling | Trust store, verification | P0 |
| Cookie management | Secure, privacy-focused | P0 |
| Caching | Intelligent cache strategies | P1 |
| Service Workers | Offline support, push | P2 |

---

## Candidate: Developer Tools

### Goal: World-Class Debugging Experience

**Status: Awaiting Community Vote**

Developers need great tools. Chrome DevTools sets the bar high.

#### Components

| Component | Description | Priority |
|-----------|-------------|----------|
| Elements panel | DOM tree, styles inspection | P0 |
| Console | JavaScript REPL, logging | P0 |
| Network panel | Request/response inspection | P0 |
| Sources panel | Debugger, breakpoints | P1 |
| Performance panel | Profiling, flame graphs | P1 |
| Memory panel | Heap snapshots, leak detection | P2 |
| Application panel | Storage, service workers | P2 |
| Accessibility panel | A11y tree, audits | P2 |

---

## Candidate: Extension System

### Goal: Chrome Extension Compatibility

**Status: Awaiting Community Vote**

The Chrome extension ecosystem is massive. Compatibility means instant access to thousands of extensions.

#### Approach

| Option | Pros | Cons |
|--------|------|------|
| Chrome API compatibility | Existing extensions work | Complex, large API surface |
| WebExtensions (subset) | Cross-browser, simpler | Some extensions won't work |
| Custom API | Optimized for HiWave | No existing extensions |

**Recommended: WebExtensions core + Chrome API shims for popular extensions**

#### Key APIs

| API | Extensions Using It | Priority |
|-----|---------------------|----------|
| tabs | Almost all | P0 |
| storage | Almost all | P0 |
| webRequest | Ad blockers | P0 |
| cookies | Privacy tools | P1 |
| bookmarks | Bookmark managers | P1 |
| history | History tools | P2 |
| declarativeNetRequest | Manifest V3 blockers | P0 |

#### Target Extensions
- uBlock Origin
- Bitwarden / 1Password
- Dark Reader
- React/Vue DevTools

---

## Candidate: Security Sandbox

### Goal: Multi-Process Architecture with Site Isolation

**Status: Awaiting Community Vote**

Modern browsers isolate websites in separate processes to contain exploits.

#### Components

| Component | Description | Priority |
|-----------|-------------|----------|
| Process architecture | Separate renderer processes | P0 |
| Site isolation | One process per site | P0 |
| Sandbox | OS-level process restrictions | P0 |
| IPC | Secure inter-process communication | P0 |
| Permissions | Granular site permissions | P1 |

---

## Candidate: Media Stack

### Goal: Full Media Playback Support

**Status: Partial (using system codecs) — Awaiting Community Vote for expansion**

Video and audio playback is essential for the modern web.

#### Components

| Component | Description | Priority |
|-----------|-------------|----------|
| Video codecs | H.264, VP9, AV1 | P0 |
| Audio codecs | AAC, Opus, MP3 | P0 |
| MSE | Media Source Extensions | P0 |
| EME / DRM | Widevine, FairPlay | P1 |
| WebRTC | Real-time communication | P1 |
| WebCodecs | Low-level codec access | P2 |

---

---

## Propose Your Own

Don't see what you want? Propose a new candidate phase:

1. Open a [Discussion](https://github.com/hiwavebrowser/community/discussions/categories/roadmap-voting)
2. Describe the component and why it matters
3. Outline what "done" would look like
4. Rally community support

The roadmap isn't set in stone. If enough people want something, we'll build it.

---

## FAQ

### Why is everything after Phase 1 "up for vote"?

Because this is a community project. Different users have different priorities:
- Power users might want extensions
- Developers might want DevTools
- Privacy advocates might want a custom networking stack
- Minimalists might want *none* of these

Rather than guess, we let you decide.

### What if I want something that doesn't win the vote?

Losing candidates aren't rejected forever — they go back in the pool for future votes. Popular runners-up often become the next phase.

### Can multiple candidates be worked on in parallel?

If we have enough contributors, yes. The vote determines *priority*, not exclusivity.

### Why not just use V8/SpiderMonkey?

- **Independence**: Relying on Google's or Mozilla's engine means relying on their priorities
- **Innovation**: Our own engine lets us try new approaches (Rust safety, novel optimizations)
- **Learning**: Understanding every layer makes us better engineers
- **Proof**: If we can build a JS engine, we can build anything

### Isn't this too ambitious?

Probably. But so was building a rendering engine in a few weeks on $300. The best way to predict the future is to build it.

### How can I help right now?

- **Phase 1**: Help with parity testing — this is the current focus
- **Future phases**: Vote, discuss, and share your expertise when voting opens
- **All phases**: Testing, documentation, feedback

See [CONTRIBUTING.md](./CONTRIBUTING.md) to get started.

---

## Following Along

- **Blog**: Technical deep-dives on each component
- **Discord**: Real-time development discussion
- **GitHub**: Watch the repos for updates

---

*"The best way to predict the future is to build it."*
