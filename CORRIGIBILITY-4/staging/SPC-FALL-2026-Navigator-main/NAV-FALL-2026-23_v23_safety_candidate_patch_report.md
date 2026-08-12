# NAV-FALL-2026-23 — Safety Architecture, AI-Control Lock, and Release-Gate Baseline

## Release status

This build is a **safety candidate**, not yet a final Fall release. It preserves the Fall 2026 local-first course workflow while adding the minimum safety and AI-governance architecture required for controlled testing.

## Implemented

- Persistent **Need Support?** access in the top bar and as a floating control.
- Support modal with 911, 988 call/text/chat, SPC Counseling Services, and Pinellas Mobile Crisis links.
- Explicit statement that Navigator is not monitored and that instructors, counselors, and emergency services are not automatically notified.
- Minor-aware wording for SPC students who may be under 18.
- Safety reminders in the Twin, Living Threads, Field Scan, Phenomenology First, first-time orientation, and Help.
- A local first-use AI processing notice that must be accepted before content is sent to an AI-assisted feature.
- Locked production AI endpoint; students can no longer redirect reflection data in Settings.
- Configurable safe-degraded mode through `NAV_CONFIG.aiFeaturesEnabled`.
- Direct first-person imminent-risk interruption before Twin content is transmitted.
- Stronger Twin system instructions for immediate-danger language.
- Copy cleanup for installation, legacy-workspace language, Coherence Check terminology, and sensitive stance wording.
- Start Here glossary shortened to prevent full duplication.
- Seven-signal rationale added to Help.
- PWA cache advanced to `navigator-fall-2026-v23-safety-candidate`.

## Important limitations

- Keyword-based interruption is a supplementary guardrail and cannot reliably identify every crisis or distinguish every academic discussion from lived disclosure.
- No external security, privacy, accessibility, or institutional legal review has yet been completed.
- The production backend still requires end-to-end verification for response integrity, failure behavior, logging, retention, and provider data use.
- The build is not ready to be designated RC1 until the launch-gate matrix passes on the deployed GitHub Pages URL and representative student devices.

## Safe-degraded mode

Set `NAV_CONFIG.aiFeaturesEnabled` to `false` in `index.html` to disable the Twin and AI-assisted coach functions while preserving local Daily Practice, Coherence Check, Living Threads, Field Scans, Moves, exports, Canvas checkpoints, and backups.

## Verification completed

- JavaScript and service-worker syntax passed.
- Manifest JSON passed parsing.
- No duplicate IDs were found.
- 18/18 controlled browser-harness checks passed.
- Desktop and mobile safety/consent views were visually reviewed.
- Live-backend, deployed-PWA, accessibility, device, and institutional gates remain open.
