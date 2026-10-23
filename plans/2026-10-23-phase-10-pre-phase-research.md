# Phase 10 pre-phase research (private PDFs/photos and session context)

23 October 2026. Required by the AGENTS.md pre-phase research rule (owner, 23 Oct).
Research proposes; it authorizes nothing. Items marked **owner decision** need an explicit answer
before they are used. Scope: master section 15 plus addendum 23 (conversation context in Phase 10).

## What Phase 10 must deliver (master 15, 23.3)

Opaque server-issued session credential; PDF/JPEG/PNG upload with size/page limits and verified
types; in-memory or bounded `tmpfs` processing; Docling in an isolated, bounded job; extract only
needed facts with OCR uncertainty; student confirms ambiguous/consequential values; facts reach the
router/Prolog as request/session-local data; bytes and temp files deleted after extraction; state
cleared on delete, expiry (proposed 30 min idle), failure and restart. Section 23 adds a
conversation-context store with the same ownership/expiry. Exit: all isolation cases pass and no
persistent personal academic records exist.

## Existing assets to reuse (build faster)

| Asset | Where | Reuse |
| --- | --- | --- |
| Session-local facts already flow to routing/Prolog | `RequestContext.facts` (course_id, state), `GroundedClaim`, `validate_interpretation` conflict checks | Extracted grades become `facts`; no new reasoning path. Unknown vs unmet already kept. |
| OCR bake-off harness and owner decisions Q8-Q16 (4 Oct) | `backend/bintanong_tools/ocr_bench/`, `plans/2026-10-04-prospectus-ocr-measurement.md` | Photo simulator, scorer, strict "supported" criteria (Q11), edition matching (Q8), user-only review (Q12), question-style confirmation. Tasks 4-9 never ran; no engine installed. |
| 39 reviewed curricula on hosted Supabase | research release, `hosted_curricula` | Answer keys for edition matching and for checking that an extracted course code exists in the student's curriculum. |
| Course-code short-form matching (owner, 21 Oct) | runtime catalog | "CC5" -> "CC 5/L" on extracted grade rows; no new alias rules. |
| pypdfium2 5.13.0, Pillow 12.3.0, FastAPI 0.141.1 (locked) | `backend/uv.lock` | Born-digital PDF text, page counting and image decoding need no new dependency. |

## Findings

1. **Born-digital PDFs need no OCR.** Grade reports and prospectus PDFs exported by school systems
   have a text layer; pypdfium2 (installed, used throughout ingestion) reads it in milliseconds with
   positions. OCR is needed only for photos/scans. Expected gain: the common case skips Docling/OCR.
2. **Docling.** Pinned 2.133.0 (3 Oct). Latest 2.142.0 (22 Oct; less than two weeks old). Relevant changes
   since the pin: `document_timeout` honored in reading order (2.140), long-lived threaded model
   workers and progress callbacks (2.139), trusted private artifact origins and validated-address
   downloads (2.141), bounded work on untrusted VLM output and Pillow 13 support (2.142), PP-OCRv6
   language list through RapidOCR (2.137). RapidOCR 3.9.2 is locked but `onnxruntime` is missing
   (ocr plan), so Docling photo OCR cannot run today. **Owner decision:** install `onnxruntime`
   (CPU) or `onnxruntime-gpu` (Q15 asked for CUDA) and whether to move the Docling pin to a version
   at least two weeks old with the timeout fixes (2.140.x) [GitHub releases].
3. **Gemma 4 E4B reads images natively.** The official model card lists Text, Image and Audio for E4B,
   image token budgets of 70-1120 (higher for OCR/documents), "OCR (including multilingual)"
   for the family, and OmniDocBench 1.5 edit distance 0.181 for E4B [Gemma 4 model card].
   llama.cpp serves images through libmtmd with `--mmproj` on the same llama-server
   (`/chat/completions`) [llama.cpp multimodal docs]. This could read a grade photo with the
   model already loaded, without the onnxruntime/torch stack. Risks: no local `mmproj` file (needs
   a download), unmeasured VRAM on 8 GB, a VLM can invent or "correct" values, and the thesis
   names Docling for parsing. **Owner decision:** whether to measure it as a candidate beside
   Docling+RapidOCR in the existing bake-off (Q11 strict criteria, user confirmation always on). Not
   a replacement without that evidence and approval.
4. **Uploads.** Layered checks: stream with a byte cap before buffering; trust neither filename nor
   Content-Type; check signatures (`%PDF-`, PNG, JPEG) in code; count pages with pypdfium2 before
   parsing; open images with `Image.open(..., formats=['JPEG','PNG'])` so other Pillow plugins never
   run (2026 advisories show decompression-bomb bypasses through GD/BDF/PCF/FITS loaders that
   `MAX_IMAGE_PIXELS` does not cover); check dimensions; re-encode before OCR [upload guides;
   Pillow advisories]. Pillow 13.0.0 exists (16 Oct); 12.3.0 has the BDF fix.
5. **Prompt injection through files** is OWASP LLM01:2025 indirect injection. Mitigations that fit the
   current design: never pass raw file text to the router; extract deterministic structured rows
   (course code, grade, term), have the student confirm, then pass only `facts`; the model has no
   tools or write access; adversarial test files in the isolation suite [OWASP LLM01 summaries].
6. **Session store.** One backend process (master 15.2): an in-process store keyed by a
   `secrets.token_urlsafe(32)` credential in an HttpOnly, Secure, SameSite cookie, with idle expiry,
   explicit delete and wipe on restart. No Redis or database (persistence is forbidden for grades).
   Conversation context (section 23) lives in the same store under the same credential.
7. **Isolation of parsing.** Run Docling/OCR in a child process with a wall-clock timeout and memory
   limit, input passed as bytes and output as structured rows; in Docker, a `tmpfs` mount for any
   temp files. A crash or timeout kills only the child and triggers cleanup.

## Recommended Phase 10 order (dependency order, smallest first)

1. Session store + credential + expiry/delete + isolation tests (also serves section 23).
2. Upload validation (caps, signatures, page/pixel limits) with synthetic hostile files.
3. Born-digital PDF grade extraction with pypdfium2 -> candidate rows -> student confirmation ->
   `facts`; reuse short-form course matching; unknown course codes stay unknown.
4. Conversation-context capture and follow-up resolution (section 23 backend).
5. Photo OCR after the owner decides findings 2-3: run the existing bake-off (simulated photos first),
   wire only a configuration that meets Q11.
Faster delivery: steps 1, 2 and 3 have separate files and contracts and can be built by parallel
subagents (TDD each), then integrated; synthetic fixtures only in tracked tests; one counted roster
rerun at the end (the router v15/v16 lessons show prompt changes move other outputs).

## Owner decisions needed before the matching step

- D1 OCR engine install (`onnxruntime` CPU or GPU) and Docling pin.
- D2 Measure Gemma 4 E4B vision (mmproj download) as an OCR candidate: yes/no.
- D3 Confirm 30-minute idle lifetime and cookie-based session credential for the research build.
Steps 1-4 need none of these and can start once Phase 10 begins.

## Sources

- Docling releases: https://github.com/docling-project/docling/releases ; PyPI https://pypi.org/project/docling/
- Gemma 4 model card: https://ai.google.dev/gemma/docs/core/model_card_4
- llama.cpp multimodal: https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md
- OWASP LLM01:2025 summaries: https://www.wiz.io/academy/ai-security/owasp-llm-top-10 ,
  https://www.oligo.security/academy/owasp-top-10-llm-updated-2025-examples-and-mitigation-strategies
- Pillow decompression-bomb advisories: https://osv.dev/GHSA-45hq-cxwh-f6vc ,
  https://securelayer7.net/lab/cve-2026-55379-pillow-bdffontfile-decompression-bomb-bypass
- Upload validation: https://oneuptime.com/blog/post/2026-02-02-fastapi-file-uploads/view ,
  https://docs.vllm.ai/en/latest/api/vllm/entrypoints/speech_to_text/base/utils/
