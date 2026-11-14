# Original native PDF field mapping

13 October 2026. Continue the
[native-field plan](../../plans/2026-10-13-reviewed-native-field-spans-plan.md)
with `document_ingest/reviewed_native_spans.py`. A pure mapper rebuilds the
preparation core against source/event bytes, checks matching pending registers,
and reads each retained native character range through an injected original reader.
It preserves the preparation and raw association diagnostics without mutation.

Nonblank field evidence must name its field, exact reviewed/native/proposed text,
one physical page, end-exclusive character range, original PDF point box, declared
coordinate order/origin and retained page size. The original reader receives exact
verified source bytes; observed range text, union character box and dimensions
must match. SourceSpan geometry is converted explicitly to left/top/right/bottom.
Image pixel coordinates, invalid ranges/geometry, duplicate ranges, partial review
or missing evidence are withheld instead of guessed. Only declared undergraduate
review audiences are mapped; institutional applicability may stay unknown.

Supported text_item locators use `native-pdf:p<page>:chars<start>-<end>`. They name
original PDF native characters, not Docling text/table IDs. Extraction explicitly
records native PDF resolution with a hash-bound original mapping evidence ID.
No new locator kind, SourceSpan contract schema or privileged review metadata is
needed. Literal source blanks map to empty span lists and blank evidence; no glyph
geometry or zero/default percentage is invented.

The caller's original reader is trusted for byte-to-native-range extraction;
hashes and these technical checks establish evidence consistency, not institutional
approval. Native technical mapping does not resolve authority, effectivity,
applicability or scope. The existing pending adapter continues withholding the
actual bundle's 66 unknown applicability declarations and all source-gap readings.

Actual preparation uses installed pypdfium2 5.14.0 on the retained handbook bytes.
Context7 official documentation confirms get_charbox returns left/bottom/right/top
in PDF canvas units and get_text_range takes start/count against the internal
character array; returned string length need not equal count. We retain original
indices and reread the exact range, with no guessed Python string indexing.
Reference: [official text-page API](https://pypdfium2.readthedocs.io/en/stable/_modules/pypdfium2/_helpers/textpage.html).

Initial 14 synthetic tests fail on the absent mapper then pass. Negative audience
mapping adds a focused RED (excluded audiences were mapped); explicit intended
audience/exclusion guard yields final15GREEN0.070s. Original-source mapping has
45 exact text/geometry reads and nine blank mappings from 18 undergraduate grading
rows. The pending adapter still emits zero actual chunks; missing scalar mappings
decrease225to180. Original corpus/raw/review/candidate/source states remain intact.
Final relevant native/preparation/chunk/source/governance/docs suite:
1008 passed, one existing Windows symlink skip, 51 subtests, 29.38s.

Independent review reproduced a native-reader reliability gap: installed
pypdfium2.PdfiumError derives from RuntimeError, which escaped the field failure
handler. A focused synthetic RuntimeError regression fails before adding that
exception category, then all16focusedtests pass0.066s. Reader data failures now
produce native_reader_failure while retaining other mapped fields. Successful
original-source mappings and the sealed actual output are unchanged.
Final relevant suite1010passed/1skip/51subtests21.11s; independent reviewer
reproduces actual PDFium data-format handling successfully and reports no residual
findings,16focusedtests0.065s pass.
