# Institutional documents in the researcher UI

27 October 2026. Owner requested real institutional grounding, understandable GUI
language, and `antislop-human`, `antislop-code`, `antislop-ui` during the work.
This is the local ingestion workstream; no hosted service or student runtime was accessed.

## Source boundary

Frozen root:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p11-two-developer-baseline-20261026/comparison-baseline-78/comparison-baseline-78/`.
Manifest SHA-256: `bfd2a4993ece9212e297a0ee47592fe8debcf6f9435a908ba2ec8103811cc011`.
All11listed file hashes/7seals rechecked unchanged after preparing the UI workspace.
Handbook394pages and Charter117pages retain their exact original bytes.

The UI prepares **72 editable local candidates**:66Handbook/6Charter, with12records
carrying known source limitations. This is the selected existing package, not an
all-page corpus/review or the later89-group expansion. Six other snapshot records
refer to three absent JPG originals and are outside this UI selection.
Original PDFs can contain excluded audiences on shared pages: only the explicitly
undergraduate selected records enter this queue. Complete original files stay intact.

Every imported field retains its value, spans, physical pages, blanks, companions,
source limits and complete prior chunk. All298fields start pending; audience starts
unresolved. The baseline values are review inputs, not a fresh raw conversion.
Reviewers can accept/correct/hold, decide audience independently, add source gaps,
edit companions, save/reopen, inspect history and export candidate decisions.
The frozen baseline and its copied reference chunks never acquire those edits.
Export includes the full prior chunk alongside new decisions, preserving the old
graph/group metadata and source limitations. It does not create a release package.
Older reference-only packets remain readable and explicitly read-only.
Neither the old pin nor stored source paths are used as hosted configuration.

The owner corrected the earlier read-only implementation after rereading the two
developer notes. Antislop changes should improve language/accessibility while
preserving the specified review workflow. The earlier viewer was a scope regression,
not an owner-approved replacement. This correction restores the functional reviewer at `89b51d9`.

## Local operation

Manifest/packet/logs under workspace
`audit-evidence/p11-policy-ingestion/institutional-candidate-ui-20261027/`.
Run from this worktree using system Python3.13:

```powershell
py -3.13 -m backend.bintanong_tools.knowledge_update prepare C:/Coding-projects/bintanong_workspace/audit-evidence/p11-policy-ingestion/institutional-candidate-ui-20261027/manifest.json --out C:/Coding-projects/bintanong_workspace/audit-evidence/p11-policy-ingestion/institutional-candidate-ui-20261027/packet
py -3.13 -u -m backend.bintanong_tools.knowledge_update review C:/Coding-projects/bintanong_workspace/audit-evidence/p11-policy-ingestion/institutional-candidate-ui-20261027/packet --reviewer Researcher --no-open
```

UI127.0.0.1:3001;API127.0.0.1:8765. Use the current terminal's launch link; tokens
change on restart and are not committed. Terminal `Institutional document review`,
handle `term_31c5fa83-8f97-411f-b476-961de6f49b4e`;Ctrl+C stops both local servers.
The synthetic preview was closed. Regular browser open requested successfully.
Installed Node22.22.3 differs from target24.21.0; no install/download/lockfile change.

## GUI and design decisions

Design read: institutional evidence comparison for researchers, using the approved
Bintanong colors/controls. ENERGY1/RHYTHM1/MOTION1: calm, predictable, no added motion.
- Original page beside the source fields keeps the comparison decision visible.
- Actual document titles/editions and PDF pages identify evidence without internal IDs.
- Prior evidence, new local decisions and known source problems stay distinguishable.
- Plain choices such as “Matches the document” and “Needs clarification” explain review actions.
- Queue filters cover unchecked, held, checked, excluded and known-source-problem records.
- Flowchart connections use From/Branch label/To controls rather than requiring JSON editing.
- New source-problem forms use normal fields/checkboxes; JSON stays in Technical details.
- Native history dialog provides keyboard dismissal/focus handling; a skip link reaches evidence.
- Stronger control edges,44px targets and selected-row outlines make controls findable.
- Neutral existing palette leaves the amber source-region/issue cues as the useful accent.
- Existing system-font fallback and compact spacing suit long source text; no remote assets.
- Grid rows size to their real content; the72-row queue no longer compresses labels.
- PDF scrolling targets the recorded highlight; shared-page headings do not replace its field location.
No decorative assets/icons, fabricated activity or ornamental comments were added.

## Verification and limits

- RED: the corrected snapshot regression reproduced read-only save refusal; the
  queue regression reproduced missing review-state filters. Synthetic tracked fixtures.
- GREEN:257tests/80subtests,57.03s. Command: system Python3.13 `-m pytest -q
  -p no:cacheprovider`,eight knowledge-update test files including snapshot intake,
  plus reviewed-policy preparation/chunks,service steps and review GUI client;
  basetemp:workspace `audit-evidence/p11-policy-ingestion/restore-review-regressions`.
- Six snapshot tests pass separately,18.88s,including older reference-packet compatibility,
  save/reopen/correction/export, unchanged original bytes and no inherited approval.
- Five Node state tests pass; TypeScript exits0; Next16.4.3 production build/start pass.
- Synthetic browser rehearsal: correction/save/reload/history/Escape/export download
  all pass, using a separate9-record synthetic packet. No institutional decisions saved.
- Real-record browser checks exposed a form crash when changing field schemas between
  documents. Selection now resets its draft atomically; rerun verifies Charter fields,
  five companions and the two flowchart connections/four companions.
- Tracked browser regression passes2.61s against the real packet: switch between
  different document field schemas and back,retaining audience/content/save controls.
  Command: `BINTANONG_REVIEW_TEST_LAUNCH` set to the current ignored launch-url.txt;
  `node --experimental-strip-types --test researcher/tests/document-switch.test.mjs`.
  Without that explicit local session input,the integration test skips. No content writes.
- Real Chrome checks:72records/298fields/revision0,Charter102/117 with6fields/5companions,
  Handbook flowchart62/394 with2connection controls/4companions. Both PDFs load.
  Dark/light computed appearance switches pass;390px and720px zoom-equivalent layouts
  have no horizontal overflow. Grid tracks were constrained after a long companion
  option caused720px overflow. Zero captured runtime exceptions in the passing checks.
- Browser harness fixes selected the actual page rather than Chrome's background
  extension target,used the current token after server restart,and normalized the
  Windows download directory. Those harness failures did not require application changes.
- Declared palette checks via the antislop-human contrast helper pass: text minimum
  5.88:1 for measured pairs; control boundaries minimum4.00:1. This is static-token
  calculation, not a completed browser-computed contrast sweep.
- Orca browser automation remains unresponsive. A separate headless Chrome profile
  uses built-in CDP/Node tools, without installing dependencies or using a personal profile.
- Raw browser scripts/reports/screenshots stay ignored under workspace
  `audit-evidence/p11-policy-ingestion/restore-browser-rehearsal/`.
- Full keyboard/assistive-technology acceptance,computed contrast for every state,
  full repository suite,actual database roles and publish/rollback rehearsal not run.
  No embeddings/model calls, content-policy changes, new approval, release activation,
  hosted access, phase closure or whole-corpus accuracy claim.

## Next action

Finish the remaining T4/T5 disposable-local lifecycle tooling/rehearsal and operator
delivery. The seven-command specification remains in scope;stage/publish/rollback
are not implemented yet. Real legacy-package rebuilding still requires explicit
reviewed authoring/bindings/membership; this UI correction does not clear that gate.
Source-content interpretations and held fields stay unchanged.
