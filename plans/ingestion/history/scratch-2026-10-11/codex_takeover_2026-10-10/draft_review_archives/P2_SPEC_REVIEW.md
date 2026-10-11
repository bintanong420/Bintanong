# Independent P2 Spec review — 2026-10-10

SPEC FAIL. Separate run /root/p2_spec_review on immutable ef0cdbff9dca3af7a9f80fdd3036a701c61c2a3c archive, base adf5d5192396dd18e58174add83773f2a0ce4aaa; bounded Tasks1–2.

High — backend/bintanong_tools/ingest.py:86–87: output can destroy input. Actual candidate CLI on external synthetic PDF: ingest source.pdf -o source.pdf exits0, replaces PDF with JSON whose digest describes destroyed original. Expected refuse alias/preserve source bytes. Retained baseline write path still violates draft read-only originals constraint. Acceptance: identical path and filesystem aliases fail before writing; original bytes unchanged.

Medium — backend/bintanong_tools/document_ingest/inspection.py:276: after-manifest omits new files. inspect_file wrapper adds b.pdf while inspecting a.pdf. Actual exit0, complete=true, one reported file although tree contains two. Expected fail with no completion manifest when membership changes. Acceptance: fresh after-walk; addition reproducer nonzero without manifest.json.

Independent evidence49passed,4warnings: test_ingest_hardening.py/test_tools_contract.py/test_scaffold_contract.py/test_document_inspection.py. Candidate import assertions passed; systemPython3.13/offline models/no-bytecode/no-cache/external basetemp. Initial unrelated E:\WpSystem collection permissions error resolved by explicit --rootdir/--confcutdir. All348archive hashes matched before/after, including actual CLI reproduction; exactrange seven Task1–2files. No sourcearchive/repository writes.

Broad gates, institutional inspection, mutation-history verification, Standards: NOT RUN. Tasks3–7/formal start/institutional approval remain gated.