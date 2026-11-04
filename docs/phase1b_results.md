# Phase 1b results: extraction of loans to customers by sector

Date: 2026-11-04. Plan: `docs/analysis_plan.md` (Phase 1a). Page references are PDF page indices (1-based) unless stated otherwise. No intensity or emissions figure is computed in this phase; the sector crosswalk is left to Phase 2, as the plan sets out.

## Outputs

| File | Content |
|---|---|
| `data/processed/exposures_by_sector.csv` | 1,924 rows: one per bank, year, level, basis and printed category (fields of plan section 3). 1,911 rows are extracted from the reporting year's own filing; 12 rows are Stanbic's 2023 figures taken from the FY2024 report's comparative; 1 row is the computed Access 2025 residual. `source_role` says which; `main_spec` marks the 1,075 main-specification rows. |
| `data/processed/sample.csv` | One row per bank-year (13 banks including ETI, 2020-2025): status, reason, main level and basis, entity behind the level, units applied, deviations. |
| `data/interim/extraction_validation.csv` | Every check: internal sums, external totals, evidence for basis and units decisions, the Jaiz 2024 OCR rule, and the re-read summary. |
| `data/interim/extraction_reread_sample.csv` | The 275 re-read values (plan section 8.1). |
| `data/interim/phase1b_total_matches.csv` | Every place in each report where a sector-table total is printed again. |
| `data/interim/jaiz2024_ocr_check.csv` | Value-by-value recheck of the Jaiz 2024 OCR. |
| `data/processed/loans_by_sector.csv`, `loans_totals.csv`, `data/interim/phase1b_extract_log.csv` | Raw extraction (as printed, before the step 1 decisions). |

Code: `phase1b_config.py` (table specifications and every decision with its evidence page), `tables.py` (parser), `phase1b_extract.py` (extraction), `phase1b_validate.py` (external matches), `phase1b_ocr.py` (Jaiz 2024), `phase1b_build.py` (decisions, outputs, re-read). Run `python -m bank_emissions.phase1b_extract` then `python -m bank_emissions.phase1b_build`.

## Sample

| Status | Bank-years |
|---|---|
| Included | 58 |
| Included, flagged | 7: ACCESSCORP 2024; ZENITHBANK 2022; UBA 2022, 2024; FIDELITYBK 2023; STANBIC 2025; JAIZBANK 2023 |
| Included, with a recorded deviation | 4: FIDELITYBK 2020-2022 (bank level); STANBIC 2023 (comparative source) |
| Included, flagged, with a recorded deviation | 1: ACCESSCORP 2025 (residual row) |
| Excluded by the plan | 8: ETI 2020-2025; UNITYBNK 2024-2025 |

Jaiz 2024 passed the OCR rule and is included. The main specification covers 12 banks in 2020-2023 and 11 in 2024 and 2025.

Main level and basis by bank (from `sample.csv`): group/gross for ACCESSCORP, ZENITHBANK, FCMB, STERLINGNG, WEMABANK and STANBIC; group/carrying for GTCO and UBA; FIRSTHOLDCO group/carrying 2020-2021 and group/gross 2022-2025; FIDELITYBK bank/gross 2020-2022 and group/gross 2023-2025; UNITYBNK and JAIZBANK bank/gross (no group table).

## Extraction

All 79 bank-year table specifications extract (log: 72 ok, 7 ok with a recorded printed inconsistency), plus Jaiz 2024 by OCR. Method: pdfplumber word positions with numbers assigned to columns by position. camelot was not needed. A table counts as extracted only if its sector rows sum to its printed total within the section 8.2 tolerance (half a printed unit per row); the 8 tables that do not (7 bank-years; Wema 2023 has a Group and a Bank table) were each read on the rendered page and the discrepancy is in the printed figures, not the parse. They are kept as printed and flagged:

| Table | What is printed |
|---|---|
| ACCESSCORP 2025 group gross (p. 199) | The "Oil And Gas - downstream" row is omitted; rows are 249,219 short of the total. The 2024 comparative column is short by 403,684, the downstream row in the FY2024 report (403,683). |
| UBA 2022 group carrying (p. 63) | "Corporates - Others" row: cells 11,012 against a row total of 10,891 (121). |
| UBA 2024 group carrying (p. 70) | "Corporates - Term loans" row: cells sum to 5,664,102 against a row total of 5,367,529 (296,573). |
| ZENITHBANK 2022 group carrying (p. 82) | Carrying rows sum to 4,013,713; printed total 4,013,705, which is the figure in the statement of financial position (p. 39) and loans note (p. 72). |
| WEMABANK 2023 group and bank carrying (p. 156) | The GENERAL row's carrying amount (105,200,312) is not its gross less impairment (104,833,990). |
| WEMABANK 2025 group carrying (p. 201) | One cell printed clipped as "7,178,47"; left empty, not filled in. |
| UNITYBNK 2023 carrying (p. 54) | The printed ECL total omits the Transportation ECL (1,233). |

In the main specification these affect only ACCESSCORP 2025 (the downstream exposure is missing from the sector rows; carried as a residual row, see below) and UBA 2022 and 2024 (sector cells, not the printed row totals, are used). The others are on the carrying basis used only in sensitivity S2, or are differences of 8.

## Step 1: loans-note check (plan sections 3 and 8.3)

For each table the printed total was looked for on every other page of the same report (any printed number within the rounding tolerance). 114 of 124 text-layer tables match a figure printed elsewhere; 10 are flagged with the reason recorded in `EXTERNAL_FLAGS` (`phase1b_config.py`). Each decision below names its evidence page and the figure printed there, and `phase1b_build` re-checks that the figure is on that page (29 basis checks and 5 unit checks, all pass).

### Units: Wema 2020-2024

The sector-table page prints "In millions of Naira" in every year 2020-2024. Decision: thousands of naira. Evidence, in every one of the five years: the sector totals (gross and carrying) equal exactly the loans note ("Gross loans and receivables", "Net loans and advances to customers") and the statement of financial position ("Loans and advances to customers"), and both of those pages print "In thousands of Nigerian Naira" (pages: 2020 pp. 34 and 70; 2021 pp. 77 and 128; 2022 p. 123; 2023 pp. 72 and 123; 2024 pp. 72 and 119). A millions reading would put Wema's loan book above 300 trillion naira. The FY2025 sector page prints thousands, consistent with the corrected series. No conflicting evidence was found, so the series was not stopped. The one Wema difference found is on the carrying basis in 2022: the sector carrying total (521,197,356) is 233,340 below net loans in the loans note (521,430,696), while gross matches; flagged.

### Basis

- STERLINGNG 2020-2025, printed "not stated": **gross**. The sector total equals the loans-note total of loans to corporates and individuals printed before "Less: Impairment" (pp. 82, 78, 181, 198, 229, 170).
- JAIZBANK 2020-2025, printed "not stated": **gross**. The sector total equals gross financing, Stage 1 + 2 + 3 before impairment (2020 p. 48, 2021 p. 72, 2022 p. 91, 2023 p. 110, 2025 p. 98). 2023: the staging total is 223,075,150, 499 below the sector total; flagged. 2024: see the OCR section.
- STANBIC: the total row is labelled "Carrying amount", but every year's total equals "Gross loans and advances to customers" in the loans note (pp. 73, 73, 72, 80, 91). Resolved to **gross**. 2025: loans-note gross 2,460,336 vs sector total 2,459,736 (600); flagged.
- FIRSTHOLDCO: **carrying** in 2020 and 2021 (the sector total equals net loans after ECL, pp. 124 and 125; gross was 2,291,545 and 3,004,177), **gross** from 2022 (equals the gross column before ECL in the loans note, pp. 109, 121, 135, 246). The basis of the printed sector tables changes in FY2022; the change is recorded in `exposures_by_sector.csv` and `sample.csv`.
- GTCO: configured as gross, found to be **carrying**. Every year's total equals "Loans and advances to customers" in the statement of financial position (pp. 78, 83, 84, 89, 127, 125). The FY2023 categorisation note (pp. 154, 156) prints total loans of 2,614,624,821 gross and 2,480,250,303 net, the latter including 66,935 of loans to banks.
- Confirmed as configured: ACCESSCORP gross (2020-2023 loans note; 2024-2025 flagged, no gross figure printed elsewhere, total above net loans by an ECL-sized margin), ZENITHBANK gross and carrying, UBA carrying, FCMB gross (2025 p. 140), FIDELITYBK gross (2023 Group flagged: the FY2024 report prints 2023 Group gross as 3,236,389, 43 above), WEMABANK gross and carrying, UNITYBNK gross and carrying.

### Stanbic 2023: comparative used (author decision 2026-11-04)

The FY2023 sector table (p. 158) totals 4,182,275 in the loans column, twice the loans-note gross of 2,091,138 (p. 82). Reading the page against the FY2024 report's 2023 comparative (p. 159): from "Hotels, restaurants and tourism" down the printed labels are one row out of step with the figures, and the last row ("Wholesale & retail trade", 2,091,138) carries the loan-book total. The comparative prints the column without a Hotels row; its 12 rows sum to 2,091,137, equal to its printed total and within 1 of the FY2023 loans-note gross (check `replacement_source` in `extraction_validation.csv`). The comparative is used in the main specification (gross, group). The FY2023 rows are kept as printed with `main_spec` false. Recorded as deviation 3.

### Access 2025: residual row (author decision 2026-11-04)

The FY2025 table omits the "Oil And Gas - downstream" row. The printed total less the 22 printed rows (249,219 million naira) is carried as one row, "unallocated (printed total residual)", computed in `phase1b_build` from the printed figures (`source_role` "computed residual"), so the main-specification total for Access 2025 equals the printed total, 13,694,446 million naira. Phase 2 rule: the plan's "Other" rule (economy-wide average intensity). Sensitivity to add in Phase 2/3: assign the residual to oil and gas downstream. Recorded as deviation 8.

### Other external differences (flagged, not resolved)

UBA 2022 Bank: sector total 2,133,989 vs Bank loans in the statement of financial position 2,123,097 (p. 31); 10,892. Bank level is used only in sensitivity S1.

## Step 2: Jaiz 2024 by OCR (plan section 2)

Tesseract 5.4.0 (`C:\Program Files\Tesseract-OCR\tesseract.exe`; not on PATH) on p. 122 rendered at about 288 dpi; the page was located by OCR of pp. 95-135. Thousands separators come back as spaces or are dropped, so digit groups are re-joined from the word boxes.

- Sum rule: the 13 sector rows sum to 289,311,931 against a printed total of 289,311,930 (tolerance 6.5). Pass.
- Loans-note rule: OCR of pp. 60-143 finds the total once more, on p. 109, as the total of the collateral analysis of customer financing (not individually impaired 277,021,465 plus individually impaired 12,290,465). This is a gross customer-financing figure in the same filing. No staging (Stage 1/2/3) table total was found by OCR. Pass, on that basis.
- Full recheck: all 13 values and the total equal the FY2025 filing's 2024 comparative column (text layer, p. 114); the 2023 column equals the FY2023 filing in all 14 values; every value was also read on the rendered page.

Jaiz 2024 is included at bank level, gross.

## Step 3: re-read sample (plan section 8.1)

Seed 20261104. 95 values drawn at random (5% of the 1,898 text-layer values) plus one complete table per bank drawn with the same seed (12 tables), 275 values in all (14.5%). Each value was re-read from the page with a second text engine (pypdfium2 page text, independent of the pdfplumber word positions used for extraction): a single printed cell must follow its row label on the page; a value that is the sum of printed cells (GTCO, UBA and First HoldCo layouts) must have every component cell printed on the page. Result: 269 pass, 6 zero cells (printed as dashes, not checkable by text search), 0 failures, so no table needed a full manual re-check. Error rate found: 0 of 269 checkable values. The OCR values are checked in full (step 2).

## Deviations from the plan

Recorded 2026-11-04.

1. Fidelity Bank level (plan section 3, main specification at group level). The FY2020-FY2022 filings print only one sector table, for Fidelity Bank Plc; Group tables are printed from FY2023. The main specification is therefore bank level for 2020-2022 and group level for 2023-2025. The level is recorded on every row and in `sample.csv` (`deviation` column); the two levels are not combined in any one series without that field. The FY2023-FY2025 Bank tables are also extracted, so a bank-level Fidelity series for 2020-2025 is available for sensitivity S1.
2. Wema units (plan section 3, units recorded as printed "not by inference"). For 2020-2024 the units applied (thousands) differ from the units printed on the sector page (millions). The decision rests on the units printed on the loans note and statement of financial position of the same report, whose totals the sector table matches exactly; `units_as_printed` keeps the printed heading and `units_applied` the decision.
3. Stanbic 2023 source (plan section 3: "Restated comparatives in the following year's report are recorded alongside but not used in the main specification"). The FY2024 report's 2023 comparative replaces the FY2023 table in the main specification because the FY2023 table is misaligned (labels one row out of step with the figures from "Hotels, restaurants and tourism" down, and a total twice the loan book). Author decision, 2026-11-04. Recorded in `sample.csv` (`deviation`) and on the rows (`source_role`, `note`).
4. Re-read method (plan section 8.1, "recomputed by reading the PDF page"). The 275 sampled values were re-read with a second text engine, not by eye. Values were read by eye on the rendered page for the 8 printed-inconsistency tables, Stanbic 2023 and the Jaiz 2024 OCR.
5. Sample size (plan section 8.1, at least 5% and one table per bank): 14.5% was re-read because the complete tables were added to the 5% random draw.
6. `printed_page` is left empty: PDF page indices are recorded for every row, and printed page numbers were not read reliably across reports (plan: "printed page where legible").
7. Flagged bank-years remain in the main specification with the flag on every row (8 bank-years above); none is dropped. Plan section 8.3 allows either explaining the difference or flagging.
8. Access 2025 residual row (plan sections 3 and 4 list printed categories only). The printed total less the printed rows is carried as "unallocated (printed total residual)", to take the "Other" rule in Phase 2, with a sensitivity assigning it to oil and gas downstream (to be added to the section 7 list as S3f). Author decision, 2026-11-04. Recorded in `sample.csv` (`deviation`).

## Limitations

- GTCO and UBA enter the main specification on a carrying basis (net of impairment), as the plan's order of preference gives when gross is not printed by sector (accepted by the author, 2026-11-04). Their exposures are lower than gross by the impairment allowance, so their estimates are not on the same basis as the gross-basis banks. GTCO was configured as gross and found to be carrying in step 1. First HoldCo is also carrying in 2020-2021 (gross from 2022), so its series changes basis in 2022.
- Fidelity changes level in 2023 (deviation 1); Stanbic 2023 comes from the following year's comparative (deviation 3); Access 2025 includes one computed residual row (deviation 8).
- Ten tables differ from figures elsewhere in their reports by amounts that could not be explained (`EXTERNAL_FLAGS`); they are kept and flagged.
- The Jaiz 2024 total was matched in the same filing only to the collateral analysis of customer financing, not to a staging table.
- The re-read check (step 3) used a second text engine rather than reading by eye.
