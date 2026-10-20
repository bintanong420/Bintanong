# Current-thread token usage observation

Owner20October2026 asks why allowance is depleting faster while using xhigh.
Bounded read-only measurement of this parent thread,not a whole harness diagnosis,
billing calculation,quota percentage or comparison against an unmeasured older day.
No configuration,reasoning level,AGENTS or plugin changes were made.

## Measured snapshot

At2026-10-20T13:18:25.692Z,the local current-thread token_count record at line3640
reports75,784,395cumulative input tokens,73,651,968cached input tokens (97.19%),
455,429output tokens including165,535reasoning output tokens. Input minus cached
is2,132,427. These are repeated-request totals across the long thread,not75million
unique context tokens or a dollar/quota charge. Latest request272,394input tokens,
264,064cached;context metadata explicitly recordsgpt-6.1-sol/xhigh. No setting changed.

Source:the local rollout file matching CODEX_SESSION_ID01a1575f-9c50-7671-a1ed-
d7819fd72bd6,verified session_meta line1 and p09cwd. The exact absolute path,
timestamp,line,raw counter fields and arithmetic are in ignored
workspace/audit-evidence/p09-router-understanding-20261020/token-usage-audit.json.
No transcript body was exported or changed. Rejected discovery locations:the
default ~/.codex/sessions had no20October candidate;the actual CODEX_HOME under
Orca's account directory supplied the matching ID. Other recent files were not
treated as this parent thread;child usage is not added or assumed included.

The router implementation segment starts with the owner's continue at transcript
line3107 (10:02:20.387Z);counter boundaries3102..3593 precede the usage question.
That segment reports10,054,417input,9,867,776cached input,65,123output including
29,942reasoning tokens. About846,419tool-output characters were returned during
the segment. These are character counts,not tokenizer estimates. Full-thread
tool output totals6,896,452characters;836Get-Content occurrences in tool inputs
are a reading-overhead indicator,not836unique files or an attribution of cost.
Exact bounded calculations:token-usage-task-range.json and token_usage_audit.py.

## Interpretation and operational response

Measured long input context,repeated file/skill reads,verbose tool output and
reasoning are credible contributors;their exact shares of the owner's allowance
cannot be inferred from these counters. One fresh independent reviewer was used
for this implementation as the executing-plans skill requires;its cost is not
quantified here. Local pytest execution itself does not invoke an OpenAI model;
returned test logs and subsequent agent reasoning enter the conversation.

Official [usage guidance](https://learn.chatgpt.com/docs/pricing) states that model,
context,reasoning,tools,retrieval and caching affect usage,and that extended
sessions carrying more context consume more. Official [reasoning guidance](https://developers.openai.com/api/docs/guides/reasoning)
distinguishes hidden reasoning tokens from visible responses. Neither establishes
this account's actual quota deduction or a new product-wide regression.

Use targeted reads and compact summaries,redirect full test output to ignored
files,and avoid completed-work repetition. Preserve required fresh context evidence,
TDD,one whole-change review,accuracy checks and owner instructions. No additional
diagnostic agents or broad transcript sweep were started. After the verified
checkpoint,a fresh conversation is an available way to start with smaller context;
its savings are not measured here. Do not silently reduce reasoning or safeguards.
