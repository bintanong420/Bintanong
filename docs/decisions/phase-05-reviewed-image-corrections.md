# Phase05 reviewed image correction binding

13October2026; inactive ingestion preparation. This extends the original-image
mapper without changing preserved proposals, review events or canonical candidates.

`correction_rows` explicitly associates a reading ID with a row ID inside its
hash-bound review event. Changed corrected scalar fields require one matching event
row and one field, exact source/page/render hash, original proposal, reviewed value,
decision and region evidence. The event must contain an actual corrected field
review; a supplied alias alone cannot approve a new value. The alias is a trusted
caller association that the independent original/event comparison checks.

The consolidated evidence adds `recorded_decision: corrected` to preserved proposal
evidence. Compare all original event evidence exactly while separately requiring
that optional annotation to equal corrected. No other extra or changed evidence is
ignored. Keep both the full annotated original evidence and the exact event field
in the resulting sidecar; never replace the earlier proposed text with a correction.

The graduation64 application maps27 visible fields, including row8's diploma cover.
Row6's clipped but owner-readable label is still annotated; row9 ends at during and
retains its source-cutoff gap. Geometry is a broad human-transcription region, not
native glyph/OCR confidence. No graph, END or complete process is inferred.
Combined96 nonblank spans/nine native blank mappings remain inactive; all66 actual
applicability declarations stay unknown and seven gap groups stay preserved.

Synthetic regressions cover missing/ambiguous/mismatched event fields, transform
identity, annotation versus original evidence, input invariance and gap withholding.
No source authority, currentness, activation or runtime gap enforcement follows from
technical mapping. Structured/gap context propagation remains a later requirement.
