# Phase 2 Task 2: read-only inspection of the originals (draft)

Status: draft on branch `draft/phase-02-code`, not the formal Phase 2 start. Nothing here is institutional approval; reports are candidates for the owner.

## Tool
`py -3.13 -m backend.bintanong_tools.document_ingest.inspection --root ORIGINALS --out NEW_OR_EMPTY_FOLDER`. Files are read as bytes only. Standard library, pypdfium2 and Pillow; no Docling, python-pptx or pypdf.

## Rules as built
- `--out` is refused when non-empty, inside the root, or when it or any parent holds a `.git` file or folder. Output files: `inspection_report.json`, `source_manifest.json`, then `manifest.json` last (no manifest means an incomplete run). A source file changed between the before and after manifests fails the run with no manifest.
- Exit codes: 0 clean; 1 for `path_unreachable`, a per-PDF invariant violation, or a changed source; 2 for a refusal.
- Page class by stripped text-layer characters: native at 100 or more, scanned below 20 with an image object, blank below 20 without, else unknown. Document class: native or scanned if every non-blank page is, mixed if both occur, else unknown (also unknown when every page is blank).
- Language is `undetermined` except PPTX `dc:language`, which is `observed`. PDF table count `not_determined`; printed folio `undetermined`; PDF page labels kept only when the file declares any.
- Pilot candidates are filename-keyword lists marked `candidates_for_owner_not_selected`.
- Path length is measured as root length plus the relative path, so `path_unreachable` depends on where the tree sits. The in-repo copy of the originals is deeper than the E: location and reports one file over 260.

## Deviations from the plan text found while building
- pdfium refuses a valid zero-page PDF with error code 0, so `zero_pages` is mapped from that code, not from a page count of 0.
- The first real run classed a native-plus-scanned document that also had an in-between page as `unknown`; the plan's order (mixed if both occur) is now followed, with a regression test.

## Not run
Docker and Linux behavior; tables, language of scanned files and printed folios stay pending. Real-run numbers are kept outside Git.
