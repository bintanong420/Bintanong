# Projected curriculum rows retain source cell identity

Date: 2026-10-12. Phase 05 extraction recovery.

Saved original-source conversion evidence showed one course's code, title and
units cells spanning several grid rows while its prerequisite occupied separate
cells. Comparing projected text made the parser emit separate courses when the
prerequisite changed, inflating the unit total. The same comparison also collapsed
separate source rows whose text happened to match.

Continue a pending course across adjacent projected rows only when the code,
title and unit values and their source cell identities match. Require a nonempty
code identity. Missing fields may match other missing fields; this preserves
incomplete candidate data without manufacturing a title or units. Absorb newly
encountered prerequisite evidence once, preserving its source cells. Distinct
source cells retain distinct courses even when their text is identical.

This handles projections of the same source row. It does not resolve separate
rows sharing an ambiguous continuation, fused course cells, or source errors.
Existing structural audits and source/content/applicability approval gates still
apply. A passing extraction audit does not approve a curriculum or activate it.

Synthetic regressions cover fragmented and repeated prerequisites, distinct
identical rows, and missing titles. The saved 39-source comparison changes only
Financial Management: one six-unit placement row replaces two projected rows;
the computed total agrees with the printed 146. Other 38 course collections and
audit results are unchanged. Detailed source evidence remains ignored in the
workspace; see the Phase 05 readiness report for final execution verification.
