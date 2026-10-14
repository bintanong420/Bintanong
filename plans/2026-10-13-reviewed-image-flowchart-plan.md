# Reviewed original-image flowchart mappings

Bounded Phase05 continuation from clean4bceb87. Execute inline under TDD with
final independent review; source/applicability/retrieval gates remain open.
Context thesisphysical17–18/36, runtime routingPNG/master10 and scope/sourcegap/
service-association policies reconsulted. Saved handbook62/63images inspected;
fresh scale2renders match original image hashes exactly (936x1224px,468x612pt).

## Mapping contract

Add `document_ingest/reviewed_image_spans.py` with pure
`map_reviewed_image_spans(bundle, *, sources, review_events, source_versions,
image_pages, read_page_image)`. Recheck original byte/event/preparation core and
pending source versions. `image_pages[(source_sha256,physical_page)]` supplies
captured image SHA256, image_size, page_size, scale, rotation0 and cropNone.
Trusted `read_page_image(source_bytes,physical_page)` returns those dimensions,
rotation/crop and image_bytes from a full original-page render. Check exact image
hash and descriptor before converting any field region; errors are per-field.

Map only declared undergraduate review rows and accepted/corrected scalar fields
whose preserved original evidence names the field, exact proposed wording and
TOPLEFT_pixels region. Convert declared full-page pixel positions to PDF points
using the validated scale, with explicit TOPLEFT origin. Preserve complete field
regions as reviewed image regions, not exact glyph boxes or native char ranges.
SourceSpan text_item namespace `image-region:p<page>:<field>:<pixel-box>` and
extraction `original_pdf_image`/`owner_transcribed_region` identify the evidence.
Keep original field proposal, event digest, image hash, pixel and PDF boxes in a
mapping sidecar. Refuse unconfirmed/image-hash/source/size/scale/crop/rotation/text/
field/region mismatches and out-of-page/nonfinite geometry. Blanks acquire no glyph
bounds or defaults. Other native/image/structured evidence stays unavailable to
this mapper rather than being guessed. Unknown applicability may be mapped
technically but the pending adapter continues withholding it.

Add `bind_reviewed_flowchart(mapping, *, arrow_reading_id, row_reading_ids,
edge_regions, terminal_region)`. The mapping's copied preparation supplies the
actual accepted arrow field and hash-bound event. Require row IDs from the same
source/version/page, each with complete mapped scalar fields; match exact ordered
from/label/to edge values and row endpoint IDs. Reject dangling/changed directions,
missing row fields and partially reviewed arrows. Edge/terminal pixel regions
are explicit original-layout inspection evidence converted against the validated
page descriptor. Return ordered nodes/field associations and edge label spans,
route regions and terminal END evidence, with inactive flags. Keep arrows separate
from scalar field_spans; do not stringify the array or create executable rules.
This is a trusted caller geometry/mapping contract, not source or policy authority.

## Tasks

1. Commit plan/checkpoint/progress resume. Preserve original datasets and previous
   seals; do not repeat completed native mapping or human page comparisons.
2. Focused `tests/test_reviewed_image_spans.py` synthetic source/event/reader RED,
   implement minimal image-region mapper/flowchart binding GREEN. Cover exact
   render identity and scale, source/page/geometry/text mismatch, unconfirmed and
   excluded audiences, blanks/non-scalar values, complete row associations,
   directional edges/terminal integrity, reader failures and input invariance.
   Related native/preparation/chunk/source/governance regressions; verified commit.
3. New ignored packet `audit-evidence/p05-reviewed-image-flowcharts-20261013/`:
   recheck prior seals/source/history, map24scalar fields in eight confirmed rows,
   bindfourconfirmededges/twoterminals with original image/geometry evidence.
   Reuse45native grading spans/nineblanks from the last sealed packet. Actual
   pending adapter still0chunks/66unknownapplicabilitywithheld; missing scalar
   mappings180to156. Independently compare saved fields/graphs/scale to original
   pages/events and prior hashes, seal results, final review/report/index/checkpoint/
   progress and curated commit. No runtime/authority/activation/Phase06 claim.

No installs/downloads/dependency locks, OCR/full conversion, canonical overwrite,
database/API/Docker/runtime/model/Prolog execution, push or source acquisition.
SystemPython3.13.7 and existing approved Python3.13 environment, no pytest cache,
workspace audit-evidence TEMP/TMP/basetemp. Exact model paths remain inMODELS.

## Delivered increment

Implementation `03d02c2` and the
[delivery report](2026-10-13-reviewed-image-flowchart-report.md) record all three
bounded tasks, including 24 field mappings, four selected edges, original-render
verification, preservation, tests and independent review. Graduation field
corrections are the next bounded mapping; formal Phase05 remains blocked.
