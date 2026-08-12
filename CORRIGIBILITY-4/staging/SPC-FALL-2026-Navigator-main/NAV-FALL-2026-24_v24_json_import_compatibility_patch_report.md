# NAV-FALL-2026-24 — JSON Import Compatibility Repair

Build: `navigator-fall-2026-v24-import-compatibility-candidate`
Mode: course-configured AI safety candidate

## Repairs
- Restored the missing `isPhenomenologicalPulseJSON` classifier and `importPhenomenologicalPulseFile` importer.
- Added direct PRF-22 / Gateway profile recognition without replacing existing Navigator memories.
- Added an Examined full-twin adapter for `chatHistory`, `archive`, `coherenceHistory`, profile prose, assembly history, and PRF scores.
- Preserved source provenance in converted records.
- Mapped Examined's six coherence signals to the corresponding six Navigator signals; Beauty / Awe / Meaning is explicitly marked as an unobserved neutral compatibility placeholder.
- Added stable compatibility IDs to prevent repeated imports from silently duplicating records.
- Applied the same format adapters to Restore, Merge, PRF import, and one-time sync merge/replace paths.

## Claim and privacy limits
- Compatibility conversion does not make the two applications' schemas identical.
- A placeholder value is not an observation or assessment.
- PRF raw source values and source prose are retained locally where present.
- The patch does not upload JSON files; import and conversion occur in the browser.
