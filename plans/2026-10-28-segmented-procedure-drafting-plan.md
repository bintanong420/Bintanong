# Segmented drafting for long procedures

**Owner28Oct:** "lets do that split u recommend, as long as the accuracy is still high and a good
response latency is kept." Keeps the 8192 window,768 output,8-claim answer cap and all review/
coverage guards. Follows [559answer results](2026-10-28-559-answer-checks-results.md) finding4.

## Evidence (diagnostic,not a fix)

Single-part good-moral probe (saved real integration,one part,two runs): 10 required records,
answer cap8claims. The model writes one claim per record,stops at8,so steps6–7/totals are never
cited -> `missing_procedure_record_coverage` twice -> abstain (79–115s). Output itself fit (~2.8k
chars). Run2 also showed two same-subject parts (whole service + totals facet) each requiring the
same10records:the procedure had to be written twice in4claims per part -> `truncated_output`.
Evidence:workspace/audit-evidence/p11-procedure-split-20261028/.

## Design

1. **Shared coverage for nested same-subject parts.** If one answered part's required record set
   is a subset of another answered part's set for the same subject,its records count as covered by
   the covering part's claims. Its own claims still answer its ask (e.g. the total fee) and remain
   reviewed. Prompt tells the model which part carries the full procedure. Coverage is never
   dropped:every required record is still cited somewhere in the final answer.
2. **Segmented drafting.** When the model-explained document work reduces to one covering part
   whose required records exceed6,the host splits those records in source order into consecutive
   segments of at most5,and drafts each segment in its own short call (same cached evidence prefix,
   segment instruction last). Claims per segment = model claim budget // segments (>=1). Segment
   outputs merge in order into one explanation;existing to_draft/coverage/order/disjunction/style
   validation and the single per-part review run unchanged on the merged draft. A failing merged
   draft repairs by redrafting all segments with the errors. Other request shapes keep today's path.

No source,budget,window,claim-cap,model or default-profile change. Accuracy guards unchanged.

## Tasks (TDD,synthetic fixtures)

1. RED/GREEN shared coverage in `record_coverage_errors` + prompt note;regressions for disjoint
   parts and non-nested sets still requiring their own coverage.
2. RED/GREEN segment planning (pure function:order,<=5records,claim budget) and generator
   segmented path:calls per segment,merged claims order,one review,repair redrafts all segments,
   overflow/timeout behaviour unchanged,short references decode per segment.
3. Focused generation/orchestration suites;full suite.
4. Live re-check once each:good-moral-en,discipline-en,entrance-health-fil,leave-en,cross-enroll-en,
   plus three regressions. Record answer quality and warm latency vs the 28Oct run. Not a sweep.

Stop rule:if segmented answers lose accuracy (wrong step/office/time association) or latency grows
materially beyond the single-call run,keep it opt-in/off and report;do not tune prompts in a loop.
