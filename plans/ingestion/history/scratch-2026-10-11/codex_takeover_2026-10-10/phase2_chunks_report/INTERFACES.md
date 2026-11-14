# Task 5 consumer interfaces

PolicyChunkResult build_policy_chunks(PolicyCandidates | ProcedureCandidates, *, token_cap=480)
- Frozen result:version_id,byte_sha256,token_cap,chunks,item_coverage,table_coverage,rejections.
- ChunkCoverage:candidate_id,chunk_ids. ChunkRejection:candidate_id,reason.
- as_dict exports actual Phase1 Chunk JSON and coverage/rejection records.
- policy chunker:palsu-policy-chunker-v1; estimate-v1 only. Cap480, adjustable lower only.
- Every unsupported/unanchored clause or table rejected; never source/rule/approval promotion.

build_ingestion_report(candidates, result, *, conversion_metadata=None) -> dict
- Reparse/check chunks then deterministic source/result equality, exact item/table accounting.
- accounting_complete describes accounting only, source/content review pending,approval_id null.
- Full rejections/omissions/raw evidence,page map,counts,metadata/settings/versions,review gaps.
- Standalone metadata absence is reported as review gap; source mismatch refused.

run_ingestion(snapshot, register, *, input_root, out, classification, converter=None, printed_page_labels=None) -> report dict
- Preflight register + snapshot + external/new-empty folder before conversion.
- Shared extract_procedure route preserves text+tables from same captured conversion bytes.
- Explicit classifications:policy_candidate,procedure_candidate,charter_candidate,form,curriculum_proposal_candidate.
- policy_candidate PDF only, procedure fields empty; other classification behavior preserved.
- out/conversion:{raw_docling.json,raw_docling.meta.json,procedure_candidates.json,manifest.json}
- out:{source_register.json,chunks.json,ingestion_report.json,manifest.json}
- Verify conversion manifest/digests/metadata identity/settings and candidate content against raw bytes.
- InputSnapshot.verify_unchanged immediately before root completion last.
- Root manifest complete is required for bundle consumption; nested conversion manifest alone is insufficient.
- Failed runs leave no active/root-complete bundle; retry in a new external folder.

CLI:
py -3.13 -B -m backend.bintanong_tools.document_ingest SOURCE.pdf --root ORIGINALS_ROOT --out NEW_EXTERNAL_FOLDER --locator shelf:handbook-copy --classification policy_candidate

Imports package variants as established:tests backend.bintanong_tools...; production bintanong_tools... relative imports.
No generic ingest.py/PhaseF change, no new schema/dependency, no embedding/database/vector/rule activation.
