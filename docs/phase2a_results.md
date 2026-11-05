# Phase 2a results: crosswalk, sector map and intensity inputs

Date: 2026-11-05. Plan: `docs/analysis_plan.md` sections 4 and 5. No intensity or financed-emissions figure is computed in this phase. Phase 1b outputs are unchanged (SHA-256 manifest `data/interim/phase1b_outputs_manifest.json`, checked by `tests/test_phase2a.py`). Page references are PDF page indices (1-based) unless stated otherwise.

## Outputs

| File | Content |
|---|---|
| `data/processed/sector_crosswalk.csv` | 234 rows, one per bank and printed label (all labels in `exposures_by_sector.csv`, including "unallocated (printed total residual)"): common sector, rule, sensitivity group, services activity, status (`ok` / `review`), reason, and the label's share of main-specification exposure |
| `data/processed/btr1_nbs_sector_map.csv` | 11 common-sector rows (10 sectors and the economy-wide rule) with BTR1/NID categories, NBS activities and intensity group; 6 rows for inventory categories that no sector takes |
| `data/processed/btr1_emissions_by_category.csv` | BTR1 Table 2.10, all categories, 2019-2022 (kt CO2e), plus NID sub-categories of 1.A.1, 1.A.2, 1.A.4 and 1.B.1 |
| `data/processed/nbs_gdp_by_activity.csv` | NBS GDP at current basic prices, 46 activities, 2019-2024 (=N= million and naira) |
| `data/interim/btr1_checks.csv`, `nbs_gdp_checks.csv`, `sector_map_checks.csv` | 99, 7 and 71 checks, all pass |
| `data/interim/phase0_sources.csv` | 7 rows added (IFRS S2, its 2025 amendments, a copy of IFRS S2 used only as a cross-check, the FRC roadmap, the 2025 GDP search and two NBS files it returned); columns `pages_used` and `licence_note` added; the 97 existing rows are unchanged |

Code: `phase2a_crosswalk.py`, `phase2a_sector_map.py`, `phase2a_btr1.py`, `phase2a_nbs.py`, `phase2a_sources.py`.

## 1. Sector crosswalk

Labels are matched on a letters-only key ("Oil&gas", "Oil & gas" and "OIL AND GAS" are one key; "&" is read as "and"), with bank-specific overrides where a label means different things at different banks. Every label is mapped; 197 rows are `ok` and 37 are `review`. The review rows hold 35.4% of main-specification exposure (2020-2025, all banks), most of it in undivided "Oil and gas" (19.9%) and "General" (5.7%).

Rules applied (plan section 4): general commerce and trade take the services intensity (S3a: economy-wide); "Other", "Others", "General - Others", "Non-interest banking" and the Access 2025 residual take the economy-wide average (S3b: zero; the residual also S3f); individuals, consumer credit and private households take zero (S3c: economy-wide); government and public sector take the services intensity (S3d: zero); finance, insurance and capital-market lending take the services intensity (S3e: zero). Fidelity's "Central Bank balance (restricted)" is not a loan exposure (its loans-column amount is zero in every year).

Two label repairs are recorded in the reasons: Stanbic's "insurance" is the second line of "Financial intermediaries & insurance" (the first line is cut off by the extraction in years other than 2023); Fidelity's "Central Bank balance (restricted )" and "(restricted)" are the same label.

## 2. Common sectors, BTR1 categories and NBS activities

| Common sector | Intensity group | BTR1 / NID categories | NBS activities |
|---|---|---|---|
| Agriculture, forestry and fishing | own | 3 (3.A-3.J); S5 adds 4 | 1-4 |
| Oil and gas, upstream | own | 1.B.2, 1.A.1.c (review) | 5 |
| Oil refining | own | 1.A.1.b | 9 |
| Power | own | 1.A.1.a | 22 |
| Manufacturing | merged | 1.A.2, 2.A, 2.B, 2.C | 10-21 |
| Construction | merged | (in 1.A.2) | 24 |
| Mining and quarrying (non-oil) | merged | (in 1.A.2) | 6-8 |
| Transport and storage | own | 1.A.3 | 27-32 |
| Water, waste and sewerage | own | 5 (5.A-5.E) | 23 |
| Services | own | 1.A.4.a | 25, 26, 33-46 |
| Economy-wide average (rule) | own | total without LULUCF | 1-46 |

Splits used (plan section 5: split only where the NID prints the split for every year): 1.A.1 into public electricity (a), petroleum refining (b) and other energy industries (c) from NID Table 3.9 (p. 64), printed annually; 1.A.4 into commercial/institutional (a), residential (b) and agriculture/forestry/fishing (c) from NID Table 3.41 (p. 90). NID Table 3.18 (p. 70) splits 1.A.2 only into iron and steel, chemicals, non-metallic minerals and "other - non specified": there is no construction or mining sub-category, so manufacturing, construction and non-oil mining are merged into one intensity group, as the plan requires.

Inventory categories that no common sector takes (row type "inventory category not assigned"):

| Category | Share of national emissions without LULUCF, 2019-2022 | Status | Reason |
|---|---|---|---|
| 1.A.4.b Residential | 16.6-17.5% | ok | not attributed (plan, individuals rule) |
| 1.A.4.c Agriculture/forestry/fishing fuel use | under 0.03% | review | not in the plan's agriculture row (3.A-3.H); candidate: agriculture |
| 1.B.1.a Coal mining and handling | under 0.03% | review | not named in the plan; candidate: non-oil mining (merged group) |
| 1.B.1.b Fuel transformation (charcoal production) | 1.5-1.7% | review | not named in the plan; candidates: forestry (agriculture) or manufacturing |
| 4 LULUCF | n/a | ok | sensitivity S5 only |
| 1.A.5, 1.C, 2.D-2.H, 6 | 0 | ok | not estimated (notation keys) |

Assigned categories cover 80.7-81.8% of national emissions without LULUCF in 2019-2022; with residential (not attributed) and the three review categories the shares add to 100% in every year.

## 3. BTR1 emissions by category, 2019-2022

Source: BTR1 Table 2.10, third year-block (PDF pp. 60-62, columns 2017-2022). The top of that block on PDF p. 60 (year header, total net emissions, energy rows 1 to 1.C and the row "2. Industrial processes") is an embedded image, not text. It was read by OCR (Tesseract 5.4, cell by cell after detecting the table grid), and the OCR year header reads 2017-2022. Every OCR value was compared with the rendered image and is covered by the sum checks below; the rest of the block is text.

Checks (all pass, `btr1_checks.csv`): 42 parent/child sums for 2017-2022 (1.A, 1.B, 1, 2, 3, 4, 5); the top-level categories sum to the printed totals with and without LULUCF in every year; the OCR total net emissions equal the printed total with LULUCF; the column years are confirmed by the 2018 reference-year total (310,030.28, p. 57) and the 2022 totals (328,496.23 and 554,095.14, p. 62).

NID sub-categories (2019-2022): Table 3.9 (p. 64), Table 3.18 (p. 70), Table 3.41 (p. 90), Table 3.59 (p. 102). Checks (all pass): children sum to the NID parent within whole-kt rounding, and each NID parent equals the Table 2.10 value within 0.5 kt. Two printing problems were handled: Table 3.18 prints the code of "Other - non specified" as "1.A.1.g.viii" (read as 1.A.2.g.viii); Table 3.59 prints the coal-mining figures inside the label column, so that row is identified by its label word and checked against the NID text (fuel transformation is more than 98% of solid fuels).

Petroleum refining combustion (1.A.1.b) is 0 in 2020 (NID Table 3.9); the refining intensity will be zero for that year.

## 4. NBS GDP by activity, 2019-2024

Source: NBS "Rebasing of GDP: Key Highlights", annex table at current basic prices, PDF p. 7 (=N= million, base year 2019). 46 activities; two are both numbered "34." (Publishing; Motion pictures), recorded with activity_no 34 and 35 and the printed number kept. Checks (all pass): 46 activities read; in each year they sum to the printed GDP at current basic prices within 0.03 million naira.

2025: not located. The Q4 2025 GDP release (27 February 2026) is reported in the press (real growth 4.07% in Q4; 3.87% for 2025; nominal Q4 GDP N122.81 trillion), but no NBS document with 2025 GDP by activity at current basic prices was found. The NBS microdata catalog for the rebased series lists Q1-Q3 2025 only. Two nigerianstat.gov.ng download links returned by the search were opened: they are the Q4 2023 and Q2 2024 GDP reports on the pre-rebasing series, not 2025 data. Under plan section 5, 2025 will use the 2024 intensity, labelled provisional, reported separately and excluded from period totals and the balanced-panel trend.

## 5. IFRS S2 and the FRC roadmap

- IFRS S2 Climate-related Disclosures (June 2023), official HTML from ifrs.org (the ifrs.org PDF returned a registration page to a script). Paragraphs used: 29(a)(i)(3) and 29(a)(vi) with B58-B63 (financed emissions; B62 commercial banking: absolute gross financed emissions by Scope 1, 2 and 3, by industry and asset class), C1 (effective for annual periods beginning on or after 1 January 2024) and C4(b) (first-year relief from Scope 3, including financed emissions). Licence: free for personal non-commercial use; the file is not redistributed.
- Amendments to IFRS S2, December 2025 (ifrs.org PDF): pp. 5-6 (29A-29C: Category 15 may be limited to financed emissions over loans, project finance, bonds, equity and undrawn commitments), pp. 9-10 (B62, B62A: gross exposure for funded amounts is the carrying amount before the loss allowance; industry classification chosen by the entity), p. 13 (effective for periods beginning on or after 1 January 2027).
- FRC Nigeria, Roadmap Report for the Adoption of IFRS Sustainability Disclosure Standards in Nigeria (Amended 2026): PDF p. 19 (printed p. 16) sets the phases (early adopters FY2023; voluntary 2024-2027; mandatory for all entities except government from periods beginning on or after 1 January 2028, all PIEs in 2028 and SMEs in 2030); PDF p. 33 (printed p. 30) defines PIEs to include entities listed on a recognised Nigerian exchange, which covers every bank in the sample.

These are logged for RQ4; the disclosure table is Phase 4 work.

## 6. Plan addition S3f

`docs/analysis_plan.md` section 7 now lists S3f (Access 2025 residual assigned to the common sector of Access's "Oil And Gas - downstream" label) as a recorded addition dated 2026-11-04, with a note stating that no other rule or sensitivity changed. In the crosswalk "Oil And Gas - downstream" is mapped to services under the commerce rule (review), so S3f's target follows whatever that row is finally signed off as.

## Deviations and notes

1. Construction and non-oil mining share the manufacturing intensity group. This follows the plan's own rule (merge where the NID does not print the split) and is recorded here because the plan's table lists them as separate sectors.
2. 1.A.1.c (other energy industries) is assigned to oil and gas upstream under the plan's "if separable" condition; marked review because the NID description of 1.A.1.c also names charcoal production, while its activity data are natural gas only.
3. Three inventory categories (1.A.4.c, 1.B.1.a, 1.B.1.b; together 1.6-1.8% of national emissions) are not named in the plan and are left unassigned pending review.
4. The BTR1 2017-2022 energy rows were read by OCR from an image in the PDF (all values sum-checked and compared with the image).
5. The crosswalk and sector map need author sign-off before section 6 is run (plan section 4).

## Review list

The 37 crosswalk rows marked `review` are in `sector_crosswalk.csv` (status column); the sector map has 4 review rows (1.A.1.c in the upstream group, and 1.A.4.c, 1.B.1.a and 1.B.1.b not assigned).
