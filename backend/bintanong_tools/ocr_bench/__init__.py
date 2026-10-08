"""OCR measurement harness: simulate photographed pages, score OCR output against the born-digital reference.

Standalone from the extractor pipeline (plans/2026-10-04-prospectus-ocr-measurement.md). Needs only
the `tools` extra (pypdfium2, numpy, opencv, Pillow); no OCR engine is imported here.
"""
