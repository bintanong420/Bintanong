# Phase 2 Task 1: ingest.py hardening (draft)

Status: draft on branch `draft/phase-02-code`. Owner decision 2 (harden or retire) is open; this implements the labelled default, harden. Nothing here is institutional approval.

## Preserved
- Module path `backend/bintanong_tools/ingest.py`, `parse_document`, `--help`, one Typer command (`ingest PATH`), `-o/--output`, result keys `title`, `text`, `num_pages`, `metadata`, `format` = `docling_markdown`.

## Changed
- The regex and `errors="ignore"` fallback is removed. `text_extracted`, a forced `num_pages` of 1 and a missing digest can no longer be returned.
- PDF only, suffix check case-insensitive. Refusals, one named class each: `FileNotFoundError` (missing path), `UnsupportedDocument` (directory or non-PDF suffix), `DoclingUnavailable` (Docling missing, from `docling_env`), `ConversionFailed` (Docling error, e.g. garbage bytes), `EmptyDocument` (zero pages or empty text).
- Converter is `docling_env.get_shared_converter()` with `identity.conversion_settings()` (OCR off), imported lazily so `--help` works without Docling; relative imports only.
- Result adds `sha256` and `conversion_identity`; `metadata.source` is the plain file name. `InputSnapshot.verify_unchanged` runs after conversion.
- A retained conversion result is checked before Markdown export: reported errors or an explicit status other than `success` raise `ConversionFailed`, including partial conversions with surviving text/pages. Status-absent legacy converter doubles remain supported; an explicit unknown or null status is refused. Refusal messages omit raw Docling error details. The CLI emits no JSON and preserves any existing output on refusal.
- CLI: conversion output goes to stderr (`docling_env` prints to stdout; `prospectus_extractor` is not edited), so stdout is JSON only. Refusals print `ClassName: message` on stderr and exit 1. The "Output saved to" message with `-o` moved from stdout to stderr.

## Callers and tests
- Importers checked: `tests/test_tools_contract.py`, `tests/test_scaffold_contract.py`, `compose.yaml` and `docker/ingest.Dockerfile` (help only). None edited; both test files pass unchanged.
- New: `tests/test_ingest_hardening.py`.

## Not run
- Compose run of the `ingest` service, Docker and Linux behavior. Owner ruling on harden vs retire is pending.
