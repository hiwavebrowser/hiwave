# Parity Test Contributions

> **Status note, 2026-11-16.** This page was written in January 2026. Its parity percentages, phase labels and dates describe the project at that time and have not been re-measured. For current, sourced figures see [Recent progress](https://github.com/hiwavebrowser/hiwave/blob/master/docs/PROGRESS-2026-11.md).

Help HiWave achieve pixel-perfect web rendering by contributing test cases that expose rendering differences.

## Why This Matters

HiWave uses a custom rendering engine (RustKit). To ensure websites look the same as in Chrome, we need extensive test coverage. Each test you contribute helps us:

1. **Identify** specific rendering bugs
2. **Prioritize** fixes based on real-world impact
3. **Verify** our fixes actually work
4. **Prevent** regressions in future releases

## Current Parity Status

| Category | Parity | Priority | Tests Needed |
|----------|--------|----------|--------------|
| CSS Selectors | 40% | P0 | 50+ |
| Image Layout | 46% | P0 | 30+ |
| Sticky/Scroll | 47% | P0 | 20+ |
| Form Controls | 48% | P1 | 25+ |
| Flexbox | 55% | P1 | 40+ |
| Grid | 53% | P1 | 35+ |
| Typography | 50% | P1 | 30+ |
| Gradients | 82% | P2 | 10+ |

## Quick Start

### 1. Find a Rendering Difference

Open any webpage in both HiWave and Chrome. Look for:
- Layout shifts
- Missing/wrong colors
- Text positioning issues
- Image sizing problems
- Form control differences

### 2. Isolate the Issue

Create the smallest possible HTML that shows the same problem:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=800, height=600">
  <title>Test: [Feature] - [Issue]</title>
  <style>
    /* Minimal CSS */
  </style>
</head>
<body>
  <!-- Minimal HTML -->
</body>
</html>
```

### 3. Capture Chrome Baseline

```bash
# Using Chrome DevTools:
# 1. Open your HTML file
# 2. Open DevTools (Cmd+Option+I)
# 3. Cmd+Shift+P → "Capture full size screenshot"
# 4. Save as expected.png
```

### 4. Create metadata.json

```json
{
  "title": "Short descriptive title",
  "description": "What should render and how it differs",
  "css_features": ["feature1", "feature2"],
  "author": "github-username",
  "viewport": {"width": 800, "height": 600},
  "chrome_version": "130.0.6723.91",
  "date_created": "2026-01-07",
  "severity": "major"
}
```

### 5. Submit

```bash
# Fork and clone
git clone https://github.com/YOUR-USERNAME/community.git
cd community

# Create test folder
mkdir -p parity-tests/submissions/your-test-name
cd parity-tests/submissions/your-test-name

# Add files
# - index.html
# - expected.png
# - metadata.json

# Commit and push
git add .
git commit -m "[Parity Test] your-test-name"
git push origin main

# Open PR on GitHub
```

## Directory Structure

```
parity-tests/
├── submissions/          # New tests (PRs land here)
│   └── your-test/
│       ├── index.html
│       ├── expected.png
│       └── metadata.json
├── approved/             # Verified and merged tests
│   ├── selectors/
│   ├── flexbox/
│   ├── grid/
│   ├── images/
│   ├── positioning/
│   ├── forms/
│   └── typography/
├── templates/            # Starter templates
└── WANTED.md             # Specific tests we need
```

## Test Quality Guidelines

### DO

- Test ONE specific behavior per file
- Use inline styles (no external CSS)
- Use standard fonts (system-ui, sans-serif)
- Include visible output (colored boxes, text, borders)
- Set explicit viewport dimensions
- Use high-contrast colors for easy diff detection

### DON'T

- Include JavaScript (unless testing JS-related rendering)
- Use external resources (images, fonts, APIs)
- Test multiple unrelated features
- Use animations or transitions
- Include comments explaining the bug (that goes in metadata)
- Use browser-specific prefixes

## Severity Levels

| Level | Definition | Example |
|-------|------------|---------|
| **critical** | Page unusable | Entire layout broken |
| **major** | Significant visual difference | Wrong element positions |
| **minor** | Noticeable but functional | Slight color difference |
| **trivial** | Barely noticeable | 1-2 pixel difference |

## CSS Feature Tags

Use these tags in `css_features` for categorization:

### Selectors
`selector-class`, `selector-id`, `selector-attribute`, `selector-pseudo-class`, `selector-pseudo-element`, `selector-combinator`, `selector-specificity`

### Layout
`flexbox`, `grid`, `float`, `position-relative`, `position-absolute`, `position-fixed`, `position-sticky`, `display-block`, `display-inline`, `display-inline-block`

### Box Model
`margin`, `padding`, `border`, `width`, `height`, `box-sizing`, `overflow`

### Typography
`font-size`, `font-weight`, `font-family`, `line-height`, `text-align`, `text-decoration`, `white-space`, `word-break`

### Visual
`background`, `gradient`, `border-radius`, `box-shadow`, `opacity`, `transform`, `filter`

### Images
`object-fit`, `object-position`, `aspect-ratio`, `image-rendering`

### Forms
`input-text`, `input-checkbox`, `input-radio`, `button`, `select`, `textarea`

## Validation

Before submitting, your test is automatically validated:

1. **Structure Check** - Required files present
2. **JSON Validation** - metadata.json is valid
3. **HTML Validation** - No syntax errors
4. **Screenshot Check** - expected.png dimensions match viewport
5. **Isolation Check** - No external resources

## After Submission

1. **Auto-validation** runs in ~2 minutes
2. **Maintainer review** within 48-72 hours
3. **Feedback** if changes needed
4. **Merge** to `approved/` when accepted
5. **Integration** into CI test suite

## Credit

All contributors are credited:
- In the test's metadata
- On our [contributors page](https://hiwave.browser/contributors)
- In release notes when your test catches a bug

## Examples

See `approved/` for examples of high-quality tests:

- [`approved/flexbox/justify-content-space-between/`](./approved/flexbox/justify-content-space-between/)
- [`approved/selectors/nth-child-complex/`](./approved/selectors/nth-child-complex/)
- [`approved/images/object-fit-cover/`](./approved/images/object-fit-cover/)

## Questions?

- Check the [FAQ](../docs/faq/parity-tests.md)
- Ask in [Discord #parity-tests](https://discord.gg/hiwave)
- Open a [Discussion](https://github.com/hiwavebrowser/community/discussions)
