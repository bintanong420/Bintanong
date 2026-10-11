# Review triage

39 distinct PDFs, healthiest first. Confirm clean sections in bulk; spend review time on broken ones.

| n | program | PDF | audit | health | PDF text | sections clean / review / broken | error and warn flags |
|---|---|---|---|---|---|---|---|
| 32 | Bachelor of Science in Biology | BS-Bio-for-student-new-version.pdf | warn | clean | checked | 8 / 0 / 0 | - |
| 04 | Bachelor of Arts in Philippine Studies | ABPhilStud-for-student-new-version.pdf | warn | warnings_only | checked | 6 / 2 / 0 | prereq_order 3, title_not_in_pdf 1 |
| 16 | Bachelor of Science in Business Administration | BSBA-HRM-for-student-new-version.pdf | ok | warnings_only | checked | 7 / 1 / 0 | title_not_in_pdf 1 |
| 36 | Bachelor of Science in Information Technology | IT-for-student-new-version.pdf | warn | warnings_only | checked | 7 / 1 / 0 | title_not_in_pdf 1 |
| 01 | Bachelor of Science in Architecture | BSA-for-student-new-version.pdf | error | mixed | checked | 1 / 8 / 1 | prereq_order 1, title_not_in_pdf 19, unit_total 1 |
| 02 | Bachelor of Arts in Communication | ABComm-for-student-new-version (2).pdf | error | mixed | checked | 6 / 1 / 1 | title_not_in_pdf 2, unit_total 1 |
| 05 | Bachelor of Arts in Political Science | PolSci-for-student-new-version.pdf.pagespeed.ce.nZiNGnw7K5.pdf | error | mixed | checked | 5 / 1 / 2 | duplicate_course 2, title_not_in_pdf 1 |
| 09 | Bachelor of Science in Social Work | BS-Social-Work-for-student-new-version.pdf | error | mixed | checked | 5 / 1 / 2 | audit_anomaly 1, title_not_in_pdf 2, unclaimed_code 1 |
| 11 | Bachelor of Science in Entrepreneurship | BSE-Agribusiness-for-student-new-version.pdf | warn | mixed | checked | 6 / 2 / 1 | prereq_order 3, unclaimed_code 1 |
| 12 | Bachelor of Science in Entrepreneurship | BSE-Franchising-and-Trading-for-student-new-version.pdf | warn | mixed | checked | 6 / 2 / 1 | prereq_order 2, title_not_in_pdf 1, unclaimed_code 2 |
| 14 | Bachelor of Science in Business Administration | BSBA-FM-for-student-new-version.pdf | error | mixed | checked | 6 / 1 / 1 | duplicate_course 2, title_not_in_pdf 1, unit_total 1 |
| 15 | Bachelor of Science in Business Administration - Business Economics | BSBA-Buss-Eco-for-student-new-version.pdf | error | mixed | checked | 5 / 1 / 2 | title_not_in_pdf 1, unit_total 2 |
| 19 | Bachelor of Science in Criminology | BS-in-Criminology-for-student-new-version.pdf | error | mixed | checked | 3 / 4 / 2 | prereq_order 5, title_not_in_pdf 1, unclaimed_code 4, unit_total 1 |
| 20 | Bachelor of Science in Hospitality Management - Culinary Track | BSHM-culinary-for-student-new-version.pdf | error | mixed | checked | 6 / 0 / 2 | unit_total 2 |
| 26 | Bachelor of Science in Nursing | BS-Nursing-for-student-new-version.pdf | error | mixed | checked | 4 / 5 / 1 | code_not_in_pdf 2, title_not_in_pdf 14, unclaimed_code 6 |
| 31 | Bachelor of Science in Marine Biology | BS-Marine-Biology-prospectus-template_07.08.2022-1.pdf | error | mixed | checked | 4 / 3 / 3 | audit_anomaly 1, code_not_in_pdf 2, duplicate_course 2, no_term 6, prereq_order 3, title_not_in_pdf 3, unclaimed_code 3, unit_total 1 |
| 33 | Bachelor of Science in Computer Science | 1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025.pdf | error | mixed | checked | 7 / 0 / 2 | audit_anomaly 1, unclaimed_code 6 |
| 35 | Bachelor of Science in Environmental Science | EnviSci-for-student-new-version.pdf | error | mixed | checked | 4 / 3 / 2 | audit_anomaly 1, code_not_in_pdf 1, title_not_in_pdf 6, unclaimed_code 1, unit_total 1 |
| 37 | Bachelor of Elementary Education | BEEd-for-student-new-version.pdf | error | mixed | checked | 5 / 1 / 3 | audit_anomaly 1, duplicate_course 2, title_not_in_pdf 3, unclaimed_code 2, unit_total 1 |
| 38 | Bachelor of Secondary Education | BSEd-Eng-for-student-new-version.pdf | error | mixed | checked | 2 / 4 / 2 | code_not_in_pdf 3, duplicate_course 2, title_not_in_pdf 10, unclaimed_code 1, unit_total 2 |
| 42 | Bachelor of Secondary Education | BSEd-Science-for-student-new-version.pdf | error | mixed | checked | 6 / 0 / 2 | audit_anomaly 1, title_not_in_pdf 1, unit_total 2 |
| 44 | Bachelor of Secondary Education | BSEd-ValEd-for-student-new-version.pdf | error | mixed | checked | 2 / 3 / 4 | audit_anomaly 1, code_not_in_pdf 1, title_not_in_pdf 3, unit_total 3 |
| 07 | Bachelor of Science in Psychology | BS-Psychology-Clinical-Psych-for-student-new-version.pdf | error | broken | checked | 2 / 2 / 6 | audit_anomaly 4, code_not_in_pdf 4, duplicate_course 2, unclaimed_code 1, unit_total 4 |
| 08 | Bachelor of Science in Psychology | BS-Psychology-Industrial-Track-for-student-new-version.pdf | error | broken | checked | 2 / 2 / 6 | audit_anomaly 2, code_not_in_pdf 7, duplicate_course 7, title_not_in_pdf 3, unclaimed_code 3, unit_total 4 |
| 10 | Bachelor of Science in Accountancy | BS-Accountancy-for-student-new-version.pdf | error | broken | checked | 3 / 0 / 4 | audit_anomaly 2, no_term 6, unclaimed_code 38 |
| 13 | Bachelor of Science in Entrepreneurship | BSE-Innovation-and-Tech-for-student-new-version.pdf | error | broken | checked | 2 / 0 / 1 | unclaimed_code 74 |
| 17 | Bachelor of Science in Business Administration - Marketing Management | BSBA-MM-for-student-new-version.pdf | error | broken | checked | 0 / 0 / 2 | audit_anomaly 6, no_term 34, title_not_in_pdf 1, unclaimed_code 26 |
| 18 | Bachelor of Science in Management Accounting | BS-Management-Accounting-prospectus_students-copy_07.07.2022.pdf | error | broken | checked | 2 / 0 / 1 | audit_anomaly 3, unclaimed_code 47 |
| 22 | Bachelor of Science in Hospitality Management | BSHM-hotel-and-resort-for-student-new-version.pdf | error | broken | checked | 0 / 0 / 4 | audit_anomaly 2, no_term 19, title_not_in_pdf 1, unclaimed_code 16 |
| 23 | Bachelor of Science in Tourism Management | BSTM-for-student-new-version.pdf | error | broken | checked | 2 / 1 / 4 | audit_anomaly 1, no_term 5, prereq_order 1, title_not_in_pdf 3, unclaimed_code 13, unit_total 1 |
| 24 | Bachelor of Science in Midwifery | BS-Midwifery-for-student-new-version (1).pdf | error | broken | checked | 0 / 1 / 3 | audit_anomaly 2, code_not_in_pdf 2, title_not_in_pdf 4, unclaimed_code 16, unit_total 1 |
| 27 | Bachelor of Science in Civil Engineering | BSCE-for-student-new-version.pdf | error | broken | checked | 2 / 0 / 6 | audit_anomaly 10, code_not_in_pdf 4, prereq_order 1, title_not_in_pdf 1, unclaimed_code 3, unit_total 5 |
| 28 | Bachelor of Science in Electrical Engineering | BSEE-for-student-new-version.pdf | error | broken | checked | 3 / 0 / 6 | audit_anomaly 4, banner_leak 2, no_term 1, prereq_order 1, title_not_in_pdf 1, unclaimed_code 19, unit_total 1 |
| 29 | Bachelor of Science in Mechanical Engineering | BSME-for-student-new-version.pdf | error | broken | checked | 0 / 0 / 11 | audit_anomaly 8, code_not_in_pdf 2, duplicate_course 2, title_not_in_pdf 7, unclaimed_code 5, unit_total 9 |
| 30 | Bachelor of Science Petroleum Engineering | BSPE-for-student-new-version.pdf | error | broken | checked | 0 / 1 / 10 | audit_anomaly 8, code_not_in_pdf 5, duplicate_course 4, no_term 14, title_not_in_pdf 3, unclaimed_code 1, unit_total 5 |
| 34 | Bachelor of Science in Computer Science | ComSci-for-student-new-version.pdf | error | broken | checked | 3 / 0 / 5 | code_not_in_pdf 1, title_not_in_pdf 3, unit_total 5 |
| 39 | Bachelor of Secondary Education | BSEd-Fil-for-student-new-version.pdf | error | broken | checked | 1 / 2 / 6 | audit_anomaly 2, code_not_in_pdf 2, duplicate_course 2, title_not_in_pdf 4, unclaimed_code 3, unit_total 4 |
| 40 | Bachelor of Secondary Education | BSEd-Math-for-student-new-version (1).pdf | error | broken | checked | 1 / 2 / 5 | audit_anomaly 2, code_not_in_pdf 2, duplicate_course 2, prereq_order 1, title_not_in_pdf 5, unclaimed_code 3, unit_total 3 |
| 43 | Bachelor of Secondary Education | BSEd-social-studies-for-student-new-version.pdf | error | broken | checked | 2 / 0 / 7 | audit_anomaly 2, banner_leak 1, title_not_in_pdf 7, unclaimed_code 2, unit_total 6 |

Skipped duplicates: 03 (same PDF as 02), 06 (same PDF as 05), 21 (same PDF as 20), 25 (same PDF as 24), 41 (same PDF as 40)
