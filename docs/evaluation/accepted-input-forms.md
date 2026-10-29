# Accepted student input forms

What Bintanong accepts besides standard spelling, owner-approved 29 October 2026. These forms are expanded or
matched only to understand the question; the student's own words are displayed, and answers keep the printed
course codes, titles and source wording. Evaluation: [benchmark questions](benchmark-questions.md) and the
shorthand probe below; results in [benchmark results](../../plans/2026-10-29-phase12-benchmark-results.md).

## Filipino shorthand (reviewed list)

Source of truth: `backend/bintanong_routing/shorthand.py` (this table is generated from it).

Rules: whole words only; single letters only when typed lowercase; uppercase "PWD" (person with disability) and
course codes stay as typed; a word followed by a hyphen still expands ("mka-graduate" -> "maka-graduate").
Not covered: other dropped-vowel spellings (e.g. "npasa", "ktagal"); the owner left out the ones copied from the
test questions so the probe is not inflated.

| Understood as | Accepted shorthand |
| --- | --- |
| pwede | pwd, pwde, pde, pwdi |
| paano | pno, pano, panu |
| ano | anu |
| bakit | bkt, bket |
| kailan | kelan |
| gaano | gano |
| ilan | ilng |
| magkano | mgkno, mgkano |
| sino | cno, cnu |
| hindi | di, hnd, hndi |
| ako | aq, aku |
| yung | ung |
| kahit | kht, khit |
| mag | mg |
| pag | pg |
| maka | mka |
| para | pra |
| naman | nmn |
| lang | lng |
| na lang | nlng |
| kasi | kc, ksi |
| sana | sna |
| talaga | tlga |
| din | dn |
| rin | rn |
| siguro | cguro, sguro |
| na ba | nb |
| sakin | skn |
| subject | subj |
| prerequisite | prereq |
| prerequisites | prereqs |
| requirement | req |
| requirements | reqs |
| first | 1st |
| second | 2nd |
| third | 3rd |
| fourth | 4th |
| sigarilyo | yosi |
| paninigarilyo | pgyoyosi, pagyoyosi |
| naninigarilyo | nagyoyosi |
| ba | b (lowercase only) |
| sa | s (lowercase only) |
| pa | p (lowercase only) |
| hindi | d (lowercase only) |

## Course names

Within the student's selected curriculum, matching ignores capitalization:

- **Printed code** and its spacing/lab forms (owner, 21 Oct): "CC 5/L", "CC5/L", "CC 5", "CC5".
- **Printed title**, when only one course in the curriculum carries it: "Data Structures and Algorithms".
- **Title initials** (owner, 29 Oct; all 963 proposals approved): first letter of each title word, small words
  (and, of, in, the, for, to, on, with, a, an, at, by, or, sa, ng) skipped unless first, a trailing number or
  roman numeral kept: "DSA" = CC 4/L, "CP2" = Computer Programming 2, "TCW" = The Contemporary World.
  Full list: [course abbreviation review](../../plans/2026-10-29-course-abbreviation-review.md).
- **Two courses fit** (shared initials or a repeated printed code): Bintanong asks which one and lists each with
  its printed code, title, year/semester and units.

## Shorthand probe questions (26)

Owner-approved shorthand versions of the 26 Taglish benchmark questions, scored against the same expectations.

| # | Benchmark id | Shorthand question | Standard wording |
| ---: | --- | --- | --- |
| 1 | drop-subject-taglish | pno mg drop ng subj? | Paano mag-drop ng subject? |
| 2 | shift-program-taglish | pano mg shift ng program? | Paano mag-shift ng program? |
| 3 | change-section-taglish | pwd b ko lumipat ng section? | Pwede ba akong lumipat ng section? |
| 4 | class-card-taglish | pano kmuha ng class card? | Paano kumuha ng class card? |
| 5 | summer-load-taglish | ilang units ung normal load pg summer? | Ilang units ang normal load sa summer? |
| 6 | leave-length-taglish | gano ktagal pwde ang leave of absence? | Gaano katagal pwede ang leave of absence? |
| 7 | substitution-deadline-taglish | kelan ung deadline ng petition for substitution? | Kailan ang deadline ng petition for substitution? |
| 8 | cs6-failed-cc4-taglish | pwd ko b i-take ung CS 6 kht d ko npasa ung CC 4/L? | Pwede ko ba i-take ang CS 6 kung di ko napasa ang CC 4/L? |
| 9 | cc5-failed-cc4-taglish | CS student aq, pwd ko b itake ang CC5 khit failed aq s CC4? | CS student ako: pwede ko bang i-take ang CC5 kahit failed ako sa CC4? |
| 10 | bsit-failed-taglish | pwde ko b kunin ung CC 5/L khit d ko p npapasa ung CC 3/L? | Pwede ko bang kunin ang CC 5/L kahit hindi ko pa naipapasa ang CC 3/L? |
| 11 | bsa-failed-taglish | pwd b kunin AD-3/L kht hnd ko p naipasa AD-2/L? | Pwede ko bang kunin ang AD-3/L kahit hindi ko pa naipapasa ang AD-2/L? |
| 12 | bsn-failed-taglish | pwd ko b kunin NCM 15-116 B khit d ko p npapasa NCM15-115A? | Pwede ko bang kunin ang NCM 15-116 B kahit hindi ko pa naipapasa ang NCM15-115A? |
| 13 | bstm-failed-taglish | pwde b kunin BME 2T kht d p pasado BME 1T? | Pwede ko bang kunin ang BME 2T kahit hindi ko pa naipapasa ang BME 1T? |
| 14 | ds2-taglish | anu prereq ng Discrete Structure 2? | Ano ang pre-requisite ng Discrete Structure 2? |
| 15 | bscrim-list-taglish | ano prereq ng Forensic 4/L? | Ano ang prerequisite ng Forensic 4/L? |
| 16 | grade-1-taglish | anu percentage at rating ng grade 1.0? | Ano ang percentage at rating ng grade 1.0? |
| 17 | probation-taglish | pano mtanggal s probation? | Paano matanggal sa probation? |
| 18 | second-year-taglish | kelan aq considered 2nd year? | Kailan ako considered second year? |
| 19 | honors-residence-taglish | ano residence req pra s honors? | Ano ang residence requirement para sa honors? |
| 20 | grad-residence-taglish | anu residence requirement pra mka-graduate? | Ano ang residence requirement para maka-graduate? |
| 21 | absence-taglish | ano ggwin ko pg umabsent aq? | Ano ang gagawin ko kung umabsent ako? |
| 22 | disc-cheating-taglish | ano parusa pg nahuli nangongopya s exam? | Ano ang parusa kapag nahuling nangongopya sa exam? |
| 23 | disc-uniform-taglish | ano parusa pg mali uniform ko? | Ano ang parusa kapag mali ang uniform ko? |
| 24 | disc-smoking-taglish | anu parusa s pgyoyosi s campus? | Ano ang parusa sa paninigarilyo sa campus? |
| 25 | disc-plagiarism-taglish | ano parusa s plagiarism? | Ano ang parusa sa plagiarism? |
| 26 | disc-bullying-taglish | anu parusa s bullying? | Ano ang parusa sa bullying? |
