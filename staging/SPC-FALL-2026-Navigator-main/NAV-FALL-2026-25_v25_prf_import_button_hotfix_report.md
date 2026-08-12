# NAV-FALL-2026-25 — PRF-22 Import Button Hotfix

## Defect repaired

The visible **Import PRF-22 / Gateway JSON** button called `triggerImportPrf22Profile()`, but the function was not defined in the v24 assembled page. Browsers therefore raised a `ReferenceError` before the hidden file input could open.

## Repair

- Added `triggerImportPrf22Profile()`.
- Exposed it as `window.triggerImportPrf22Profile` for the inline button handler.
- The function finds `#import-prf22-file`, clears any prior selection, and opens the native file chooser synchronously inside the user click.
- Added a controlled error message if the file input is unexpectedly absent.
- Preserved the v24 PRF-22, Examined, Daily Practice, Phenomenology First, Restore, and Merge adapters without changing their data semantics.
- Bumped the service-worker cache and manifest/build labels so browsers do not continue serving the broken v24 shell.

## Claim boundary

This is a narrow UI-entry-point repair. It does not establish live backend readiness, cross-device sync privacy, or full device/browser certification. Those launch gates remain open.
