# NAV-FALL-2026 PWA Ready Package

This package contains clean PWA support files for the SPC Fall 2026 Navigator repository.

Upload these files/folders to the repository root:

```text
index.html
manifest.json
sw.js
icons/
  icon-180.png
  icon-192.png
  icon-512.png
```

The manifest now references the icons:

```json
"icons": [
  { "src": "./icons/icon-180.png", "sizes": "180x180", "type": "image/png", "purpose": "any" },
  { "src": "./icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable" },
  { "src": "./icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
]
```

The service worker cache name has been bumped to:

```js
navigator-fall-2026-mvp-v2
```

Bump this again whenever you update `index.html` and want students' browsers to pick up the new build quickly.
