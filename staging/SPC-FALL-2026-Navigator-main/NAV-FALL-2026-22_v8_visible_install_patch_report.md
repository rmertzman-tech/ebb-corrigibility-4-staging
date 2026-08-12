# NAV-FALL-2026-22 — v8 Visible Install Button Patch Report

Source: `index_fall2026_mvp_v7_final_polish.html`

Output: `index_fall2026_mvp_v8_visible_install.html`

## JavaScript Syntax Check

PASS

## Implemented Changes

- OK: meta navigator-build v8 (1 replacement(s))
- NOT FOUND: remaining v7 marker
- OK: APP_VERSION v8 (1 replacement(s))
- OK: make PWA install buttons always visible (1 replacement(s))
- OK: visible install button fallback text (1 replacement(s))
- OK: add visible install button to Daily Practice secondary row (1 replacement(s))
- OK: Daily workspace install note (1 replacement(s))
- NOT FOUND: topbar install button visible and clearer
- OK: clearer Chrome/Edge install help (1 replacement(s))
- OK: clearer iOS install help (1 replacement(s))
- OK: added v8 marker comment

## Reason for v8

The v6/v7 install button was technically correct but intentionally hidden until the browser fired `beforeinstallprompt`. That meant the button did not appear on the Daily Practice home screen when the browser had not yet decided the app was installable. This v8 patch makes the button visible all the time and uses it as either:

1. a real install prompt when `beforeinstallprompt` is available, or
2. a simple Add to Home Screen instruction helper when the browser does not expose the prompt.

## Key Phrase Counts

- `Add to Home Screen`: 5
- `Install App`: 1
- `pwa-install-btn { display: inline-flex; }`: 1
- `beforeinstallprompt`: 2
- `promptInstallNavigator`: 5
- `navigator-fall-2026-mvp-v8-visible-install`: 1
- `const ENABLE_PWA = true`: 1
- `serviceWorker.register('./sw.js')`: 1
- `NAV-PULSE`: 0
- `ENABLE_PWA = false`: 0
- `sw navigator-fall-2026-mvp-v8`: 1

## Repo Upload Contents

```text
index.html
manifest.json
sw.js
favicon.ico
icons/
  icon-180.png
  icon-192.png
  icon-512.png
```
