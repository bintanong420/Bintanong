# Recorded focused probe outputs

Executed from this scratch directory during independent Spec review. These are focused read-only implementation probes, not a gate rerun or browser pass. Python ran with `-B`; probes and this evidence file are external to Git.

Command: `& 'C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe' -B .\spec-d11-probe.py`
Exit: 0.

```json
{"prior_field":"prerequisites_raw","prior_disposition":"unresolved","bulk_written_fields_for_same_course":["row"],"bulk_written_dispositions":["accepted"]}
```

Command: `node .\spec-twin-probe.cjs`
Exit: 0. Executes the actual renderTwin source in a VM with minimal cell stubs.

```json
{"kind":"prerequisite","asked":["code-cell"],"scrolled":["code-cell"]}
```

Command: `& 'C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe' -B .\spec-section-pdf-probe.py`
Exit: 0. Uses a renderer stub reporting an available 10-page PDF; no candidate, PDF or ledger file is created.

```json
{"kind":"section_confirm","question_pages":[1],"pdf":{"available":true,"name":"read-only-renderer-stub.pdf","pages":10},"boxes_page_keys":[],"renderPdf_hides_image":true}
```
