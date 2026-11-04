# Dialogue router integration — 4 November 2026

Owner directed implementation of the next stabilization priority: connect the
committed ephemeral ledger, then verify clarification recovery and topic switching,
including shifting-office referrals. Existing audit slices 2–4 govern; no numbered
phase, dependency/model change, durable storage or institutional activation.

Consulted current Git/index/progress, stabilization plan/checkpoint, owner ledger,
master routing architecture, thesis physical 17–18 and 39–44, and runtime routing
PNG on this resume. Undergraduate advisory and source/privacy boundaries remain.

Implementation: one server-owned compiler projects up to four same-scope exchanges
under 16 KiB of dialogue text, including the unresolved origin when retained.
The routing payload marks old user/assistant text as untrusted interpretive context.
Typed semantic acts select an actual owned turn and reviewed course candidate;
the saved operation is checked again. A self-contained topic switch drops course
focus while retaining separately scoped facts. No exact repair-phrase detector,
new feature-specific pending type, assistant-derived grades or old-answer evidence.
The existing router call interprets the act; no additional model call was added.

Chat now passes the actual utterance to routing rather than the pending-check
question rewrite. Existing short-reply fact grounding remains scoped and separate.
Default/separate and combined routing paths support owned dialogue references.

TDD: missing ledger projection, absent prompt history, semantic repair returning
generic clarification, and hidden short-reply reconstruction each reproduced RED.
Focused component gate: **186 passed in 6.99s**, covering projection, raw chat turns,
router/wire/combined contracts, semantic recovery, forged references, old assistant
injection and new shifting-topic routing. This is protocol/host evidence, not model
accuracy or a whole conversation acceptance result.

Live first run: initial BSIT eligibility asks correctly, but follow-up/why/repair
returned insufficient evidence within about one second despite the result being
remembered. Same under compiler OFF/ON. Exact routing trace is being collected;
the student capability is still open. Ignored evidence:
`audit-evidence/stabilization-20261104/dialogue-{live,trace}.{json,log}`.

Next: diagnose the actual live failure; complete bounded generic unresolved-state
retention and document-reference coverage; run model conversations and actual
reviewed shifting evidence/referral checks. Preserve fresh-vs-follow-up comparisons.
