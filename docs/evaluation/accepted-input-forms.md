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

## Filipino words for printed penalty rows (reviewed list)

Owner-approved 30 October 2026 ("use it but uniporme we dont really use this but the rest definitely yes"; kopya
forms: kopya, pangongopya, kumopya, kumukopya). Source of truth: `backend/bintanong_routing/filipino_terms.py`;
`tests/test_routing_filipino_terms_doc.py` keeps this table equal to it.

These words let the router find the English row printed in the Handbook sanctions table ("cheating in
examinations", "Smoking", "Bullying"); the student's words are displayed and answers keep the printed English.
Whole words only ("malaking" never reads as "alak"). Filipino affixes change the root ("kumopya",
"nangongopya"), so each accepted form is listed; a form not listed is left to the model's choice. A row is chosen
only when it names more of the question's words than any other row. "uniporme" is not used by students and is
left out; words that point to several offenses (e.g. "away", "suntok") are left out on purpose.

| Printed English term | Accepted Filipino words |
| --- | --- |
| cheating | kopya, kumopya, kumukopya, kinopya, nangopya, nangongopya, mangopya, pangongopya, pagkopya, nagkopya |
| examination | pagsusulit |
| smoking | yosi, nagyosi, magyosi, nagyoyosi, pagyoyosi, sigarilyo, paninigarilyo, naninigarilyo, nagsisigarilyo |
| bullying | bully, nambully, nambubully, binully, binubully, mambully |
| drinking | alak, lasing, nalasing, naglalasing, paglalasing |
| gambling | sugal, nagsusugal, sumugal, pagsusugal, pustahan, pumusta, nagpupusta |
| littering | kalat, nagkalat, magkalat, pagkakalat, basura |

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

## Robustness results (separate from the main 50)

All on the same code (`cb82c53`), one run each, same expectations as the standard wording. Scores for shorthand are
optimistic: the shortcut list was written after seeing these questions.

| Input set | Passed | Standard-wording twins | Reply language |
| --- | ---: | ---: | --- |
| Pure Tagalog (26) | 19/26 | Taglish twins 19/26 | Taglish 26/26 |
| Shorthand Taglish (26), before the shortcut list (`d5e638a`) | 8/26 | 20/26 | Taglish |
| Shorthand Taglish (26), with the shortcut list | 15/26 | 20/26 | Taglish 26/26 |
| Broken English (4) | 2/4 | 4/4 | English |

Broken English questions: "how to drop subject" (pass), "how to get class card" (pass), "can i take cc5 if i fail cc4
im cs student" (clarification instead of the check), "what penalty if caught cheating exam" (clarification).

## Research basis (for the study)

Gathered 29 October 2026 when designing the shorthand handling. Details marked "verify" came from search summaries,
not the full papers; check the full text and complete author lists before citing.

| Source | What it supports | Link |
| --- | --- | --- |
| NormAPI: An API for Normalizing Filipino Shortcut Texts (De La Salle University; IALP 2014; thesis version in the DLSU Animo Repository) | Filipino shortcut styles (shortenings, consonant skeletons/vowel omission, clippings, initialisms, acronyms); dictionary substitution vs statistical MT vs hybrid (best BLEU about 0.81). English-only normalizers do not cover Filipino shortcut styles. | [repository](https://animorepository.dlsu.edu.ph/etd_bachelors/11826), [paper](https://www.academia.edu/15029837/NormAPI_An_API_for_Normalizing_Filipino_Shortcut_Texts) |
| TagNorm, Tagalog text normalizer (IEEE HNICEM 2021) — verify title/authors | Informal Tagalog categories: alphanumeric abbreviation, phonetic/stylistic variation, combined words, misspellings/typos, vowel omission; SVM slang detection. | (as summarized via Flores & Radev 2022) |
| Flores, L. & Radev, D. (2022). "Look Ma, Only 400 Samples! Revisiting the Effectiveness of Automatic N-Gram Rule Generation for Spelling Normalization in Filipino." SustaiNLP 2022. | Filipino spelling normalization from about 300–400 examples with n-gram rules plus Damerau-Levenshtein distance, outperforming deep-learning baselines; supports a small reviewed list as a practical approach. | [arXiv 2210.02675](https://arxiv.org/abs/2210.02675) |
| Liu, Zhao, Altinger, Schütze & Hedderich (Oct 2025). MulTypo: evaluating LLM robustness to typographical noise — verify title | 18 open LLMs: typos hurt generation and reasoning most; low-resource languages less robust; instruction tuning can increase brittleness. Motivates testing shorthand separately. | [arXiv 2510.09536](https://arxiv.org/html/2510.09536v1) |
| Okewunmi, James & Fajemila (2025). Evaluating Robustness of LLMs to Typographical Noise in Yorùbá QA. AfricaNLP 2025. | Character noise causes sharper drops in a low-resource language than in English. | [ACL Anthology](https://aclanthology.org/2025.africanlp-1.29) |
| Exploring Robustness of Multilingual LLMs on Real-World Noisy Data (Jan 2025) — verify authors | All tested models degrade on real-world typos (WikiTypo dictionary). | [arXiv 2501.08322](https://arxiv.org/html/2501.08322v1) |
| Kaiwa, "Filipino texting shortcuts guide 2026" (commercial blog, lower reliability) | Example everyday shortcuts: d/di/hnd (hindi), bat (bakit), pano (paano), san (saan), nmn (naman), nlng (na lang). | [blog](https://trykaiwa.com/blog/filipino-texting-shortcuts-guide-2026) |

How it shaped Bintanong: a small owner-reviewed list (dictionary substitution, NormAPI/Flores & Radev) applied
before understanding, keeping the student's wording; ambiguous forms limited (uppercase "PWD", single letters only
lowercase); shorthand measured as a separate robustness result (MulTypo, Yorùbá QA). Open-vocabulary dropped-vowel
spellings remain uncovered (would need an edit-distance or model-based normalizer).
