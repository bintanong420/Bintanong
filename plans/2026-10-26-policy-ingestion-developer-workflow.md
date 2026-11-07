# Two-Developer Phase 11 Workflow

## 1. Establish the shared baseline

The responsibilities are clear. Shared interfaces still exist, so zero conflicts cannot be guaranteed—but we can give each shared area one owner.

You finish the planned Handbook/Charter verification first. Commit the review records and identify a fixed, verified source/package snapshot. This does not imply whole-document approval.

Then:

- You: continue on feat/p11-backend-api.
- Other developer: create feat/p11-policy-ingestion-review from that verified commit.
- Use separate worktrees and separate generated-output directories.
- Preserve the baseline snapshot unchanged for repeatable testing.

## 2. Divide ownership

| Area | Owner |
|---|---|
| Current Handbook/Charter review decisions and active knowledge | You |
| Student chatbot frontend and API integration | You |
| Router, orchestration, answer generation and runtime fixes | You |
| New ingestion workflow and local researcher review UI | Other developer |
| Locally generated candidate chunks and ingestion-specific tests | Other developer |
| Hosted Supabase, active release and runtime pin | You |
| Existing shared contracts, storage interfaces, parsers and dependency files | You coordinate changes |

The developer should add their workflow/UI in separate modules and reuse existing interfaces. If an existing shared module needs modification, agree on the change first and have one person implement that shared change.

You maintain the central Phase 11 progress/checkpoint. The developer maintains a dedicated ingestion task record and supplies updates for consolidation.

## 3. Work concurrently

Your workflow

1. Integrate the chatbot frontend.
2. Run student queries.
3. Fix routing, API or answer behavior through regression tests.
4. Commit changes in small units.
5. Notify the developer when a change affects ingestion output requirements.

Other developer’s workflow

1. Build the reusable ingestion commands and separate local review UI.
2. Use copies of the existing PDFs, reviewed decisions and chunks as test evidence.
3. Generate new candidate chunks locally when needed.
4. Compare results against the reviewed baseline and explain differences.
5. Test persistence, staging, publication and rollback against disposable local databases.
6. Keep all generated candidates inactive and isolated from your runtime package.

Their environment must target local databases explicitly. A separate worktree alone does not prevent copied configuration from pointing at hosted Supabase.

No hosted writes from their workstream, including staging, review RPCs, release activation or migrations.

Coordinate resource-heavy embedding runs so they do not distort your chatbot latency measurements.

## 4. Coordinate shared-interface changes

Before changing chunk/source schemas, topic or claim metadata, release formats or storage interfaces:

1. Identify the affected interface.
2. Agree on its resulting behavior and compatibility.
3. Have the designated owner implement it once.
4. Merge that update into the developer’s branch.
5. Run both ingestion and runtime compatibility tests.

Ordinary router-prompt or frontend-layout changes generally require no ingestion changes.

## 5. Integrate the completed tooling

The developer submits the feature branch back into your Phase 11 branch.

Before merging:

- Review code and resolve documentation overlap.
- Run ingestion tests, chatbot regressions and the relevant full suite.
- Confirm generated packages remain compatible with the current runtime.
- Preserve your active source decisions, hosted release and runtime pin.

Merging the tooling does not publish its generated chunks. Any future hosted update remains a separate, explicitly authorized operation under your control.