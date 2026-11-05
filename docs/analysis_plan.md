# Analysis plan (Phase 1a)

## Purpose and status

This plan fixes the research questions, sample, data treatment, calculation, sensitivities and validation rules before any sector table is extracted or any intensity is computed. It is written after Phase 0 and draws only on the files listed below. No estimate is produced in this step, and nothing here anticipates the size or direction of results.

Inputs read for this plan: `README.md`, `docs/phase0_plan.md`, `docs/phase0_results.md`, `data/interim/phase0_intensity_notes.md`, `data/interim/phase0_failure_notes.md`, `data/interim/phase0_manual_checks.csv` and, for extraction difficulties, `data/interim/extraction_test_notes.md`. Page references are PDF page indices (1-based) unless stated otherwise, following the convention in `docs/phase0_results.md`.

Any departure from this plan in later phases is recorded in a "Deviations" section of the relevant results document, with the date and the reason.

## 1. Research questions

RQ1. What are the estimated financed emissions (tCO2e) attributable to loans and advances to customers of each NGX-listed bank in the sample, for each year 2020-2025, and in total?

Reason: bank climate disclosures in Phase 0 cover mostly Scope 1 and 2 (Phase 0 table c and manual checks), and only two banks printed a financed-emissions figure in the documents opened. An outside-in estimate from audited sector notes gives a figure for every bank on a common method.

RQ2. Which sectors account for the largest share of the estimated financed emissions, by bank and in total, and how did the sector composition change over 2020-2025?

Reason: the sector notes are the only exposure detail common to all sampled banks, and the sector dimension is where the estimate carries information (the intensity is a sector average, so differences between banks arise from portfolio mix and size).

RQ3. How do the estimates compare with the financed-emissions figures the banks have published, and why may they differ?

The published figures available from Phase 0, quoted as printed in `data/interim/phase0_manual_checks.csv`:

- Fidelity Bank, 2023 sustainability report (`data/raw/sustainability/FIDELITYBK_2023_sustainability.pdf`, PDF p. 27, printed pp. 52-53): Scope 3 Category 15 financed emissions 682,299.78 tCO2e.
- UBA, 2024 sustainability report (`data/raw/sustainability/UBA_2024_sustainability.pdf`, PDF p. 33, SASB table): absolute gross financed emissions 2023 Scope 1&2 2,258,646 tCO2e and Scope 3 804,727 tCO2e; 2024 Scope 1&2 602,146 tCO2e and Scope 3 378,879.66 tCO2e; percentage of gross exposure included 90% (2023) and 52% (2024). The page's cross-references to methodology pages (48, 24) point to unrelated content.
- Fidelity Bank, 2025 annual report (`data/raw/annual_reports/FIDELITYBK_2025_ir.pdf`): the manual check records PDF p. 99 with Category 15 financed emissions of 5,704,317.97 (2025), 4,606,362.05 (2024) and 682,299.78 (2023), and a methodology section on PDF p. 100 that refers to PCAF. The printed page number and the unit as printed are to be confirmed and recorded before the figure is used.

Reason: the comparison is the only external check on the order of magnitude available for this study. It is a comparison of two different methods, not a validation of either, and section 8 sets how differences are treated.

RQ4. What does each sampled bank currently disclose on Scope 1, Scope 2, Scope 3, financed emissions and PCAF, and how does this compare with what IFRS S2 will require?

Reason: the disclosure gap is the policy context of the study. The bank-side evidence is Phase 0 table c (automated "q"/"m" page search) and the manual verification table. The IFRS S2 requirements and the Nigerian adoption timeline were not opened in Phase 0; they will be quoted from the IFRS S2 text and the Financial Reporting Council of Nigeria adoption documents, opened and logged in `data/interim/phase0_sources.csv` (or a successor log) before RQ4 is written up. Automated "q" readings are not reported as disclosures unless confirmed by reading the page.

## 2. Sample

The sample is 12 banks: ACCESSCORP, ZENITHBANK, GTCO, UBA, FIRSTHOLDCO, FIDELITYBK, FCMB, STANBIC, STERLINGNG, WEMABANK, UNITYBNK and JAIZBANK. The NGX directory check found no issuer in the "Banking" sub-sector outside the candidate list (Phase 0 table a).

### Exclusion: Ecobank Transnational Incorporated (ETI)

ETI is excluded for all years. Reason: the NGX filings for 2020-2025 are 47-52-page condensed consolidated statements without a credit-concentration-by-sector note (Phase 0 table b and failure notes). The ecobank.com annual-reports page lists documents through JavaScript and timed out on later requests; the full 2023 report seen on a share registrar's site is not an official ETI or NGX source and was not opened. ETI is also incorporated in Togo (ETI FY2025 statements, PDF p. 22), so Nigerian sector intensities would apply poorly to its loan book in any case. The exclusion and its reason are recorded in the sample table produced in the extraction phase. ETI remains in the RQ4 disclosure table, where the Phase 0 scan found no Scope 1-3 or financed-emissions content in its 2025 NGX filing.

### Unity Bank: 2020-2023 only

Unity Bank is included for 2020-2023. Reason: the latest audited statements on NGX are for FY2023 (posted 2025-02-26), and no URL was found for FY2024 or FY2025. NGX filings include a CBN approval notice for the Unity Bank and Providus Bank merger (2024-08-07) and resolutions of a court-ordered meeting (2025-09-29); these are cited as the context for the missing years. No values are imputed for Unity Bank 2024-2025.

### Jaiz Bank 2024: OCR rule

The 2024 NGX filing (143 pages) has no text layer. The sector table is read by OCR. The year is kept only if the OCR sector rows sum to the printed total within the rounding tolerance in section 8 and the total agrees with the loans note in the same filing. If either check fails, Jaiz 2024 is dropped and the reason recorded. The 2024 comparative column in the Jaiz 2025 filing (text layer, sector table on PDF p. 114) is used as an additional cross-check of the OCR values; it is not substituted for the 2024 filing under this plan.

### Consequence for totals

The panel is unbalanced: 12 banks in 2020-2023, 11 in 2024-2025 (10 in 2024 if Jaiz 2024 is dropped). Year totals are therefore reported in two forms: all available banks, and a balanced panel of the banks present in every year. Changes over time (RQ1, RQ2) are described on the balanced panel.

### Listed-entity changes

Holding-company restructurings during the period (ACCESSCORP from 2022-03-28, previously Access Bank Plc; GTCO from 2021-06-24, with Guaranty Trust Bank Plc filing FY2020; STERLINGNG from 2023-04-06, with Sterling Bank Plc filing FY2020-FY2022; FIRSTHOLDCO, formerly FBN Holdings) are recorded per bank-year, because they change which entity's group the sector note describes.

## 3. Exposure measure

### Order of preference

1. Gross loans and advances to customers by sector. Reason: PCAF attributes emissions to the outstanding amount lent, and the gross amount is the closest printed proxy; it is also unaffected by differences in impairment between banks and years.
2. Carrying amount (net of impairment) where gross is not printed. Reason: it is the only sector-level loan figure some banks print (UBA states carrying amounts or amounts net of impairment allowances; Phase 0 table format by bank).

Only the loans-and-advances-to-customers component of a credit-concentration table is used. Where the table combines asset classes (GTCO, UBA, FIRSTHOLDCO, FIDELITYBK, STANBIC and the Unity p. 62 table, per Phase 0), the loans-to-customers row or column is taken; loans to banks, investment securities, cash, central bank balances and off-balance-sheet items are excluded. Where a bank prints both a sector table and a sector-by-product table (GTCO, FIRSTHOLDCO), the table whose total reconciles with the loans note is used, and the choice is recorded.

Where the basis is not stated on the page (STANBIC, STERLINGNG and JAIZBANK in the Phase 0 format check), the basis is assigned by reconciling the table total with the gross and carrying amounts in the loans note. If neither matches, the basis is recorded as "not stated" and treated as carrying amount for the purpose of the gross-versus-carrying sensitivity.

The figures used are those printed for the reporting year in that year's report. Restated comparatives in the following year's report are recorded alongside but not used in the main specification.

### Level

Group level is the main specification. Reason: group figures are printed by every sampled bank, and the listed entity is the group for the holding companies. Bank (Nigeria) level is a sensitivity where printed (for example Group and Bank columns in Access 2020-2021, Zenith and Wema).

In holding-company filings the second column is often the holding company itself, not the Nigerian bank (Access 2022-2023 print the Company columns as dashes). The extraction phase records, for each bank-year, whether a column represents the Nigerian bank, the holding company or neither, and the bank-level sensitivity uses only columns that represent the Nigerian bank. Unity Bank prints no Group/Bank split.

### Foreign subsidiaries

Group exposures of banks with foreign banking subsidiaries include loans booked outside Nigeria, to which Nigerian intensities apply less well. Banks are flagged as follows, from the manual verification in `data/interim/phase0_manual_checks.csv` and Phase 0 table a:

| Bank | Foreign operations | Evidence |
|---|---|---|
| ACCESSCORP | yes | FY2025 report PDF p. 268: banking subsidiaries in 15 countries plus the UK |
| ZENITHBANK | yes | FY2025 filing PDF p. 243: Ghana, UK, Sierra Leone, Gambia |
| GTCO | yes | FY2025 report PDF p. 312: Gambia, Sierra Leone, Ghana, UK, Liberia, Cote d'Ivoire, Kenya, Tanzania |
| UBA | yes | FY2025 filing PDF p. 186 (partial list); 2024 sustainability report PDF p. 32: 24 countries |
| FIRSTHOLDCO | yes | FY2025 report PDF p. 272: DRC, Ghana, Sierra Leone, Guinea |
| FIDELITYBK | yes | FY2025 report PDF p. 163: UK subsidiary |
| FCMB | to confirm | FY2025 filing PDF p. 143: direct subsidiaries in Nigeria; indirect subsidiaries not checked; automated match names the UK |
| STANBIC | no (significant subsidiaries) | FY2025 filing PDF p. 96: all incorporated in Nigeria |
| STERLINGNG | none found | automated match only |
| WEMABANK | none found | automated match only |
| UNITYBNK | not checked | FY2025 report not available |
| JAIZBANK | to confirm | automated match names Gambia and UK; not verified |

Where a bank prints a geographical breakdown of loans (STANBIC prints a geographical concentration table alongside the industry table; others to be checked), the Nigeria share is recorded for description; it is not used to rescale sector exposures, because sector and geography are not cross-tabulated.

### Recorded fields

Every extracted row records: NGX symbol, financial year, reporting date, level (group, bank, holding company), basis (gross, carrying, not stated), units as printed (thousands or millions of naira), the amount as printed, the amount converted to naira, the sector label as printed, source file, PDF page, printed page where legible, extraction method (text layer, camelot, OCR, manual) and any note. Unit changes within a bank's series (Access thousands to millions from 2022; Wema millions to thousands in 2025) are handled by this field, not by inference.

## 4. Sector mapping

### Common sector list

Bank categories differ in number (12 at Zenith and Unity, 24 at Access, per Phase 0) and wording. A single common sector list is defined so that each common sector has (a) one or more BTR1 inventory categories and (b) one or more NBS GDP activities. The working list, to be finalised in the crosswalk once all printed labels are extracted:

| Common sector | BTR1 categories (Table 2.10) | NBS activities (rebased GDP annex) |
|---|---|---|
| Agriculture, forestry and fishing | 3.A-3.H (4 LULUCF in sensitivity) | crop production, livestock, forestry, fishing |
| Oil and gas, upstream | 1.B.2 oil and natural gas; energy-industry combustion in fuel extraction (1.A.1 sub-category, if separable in the NID) | crude petroleum and natural gas |
| Oil refining | 1.A.1 petroleum refining (if separable in the NID) | oil refining |
| Power (electricity and gas supply) | 1.A.1 public electricity and heat production | electricity, gas, steam and air conditioning |
| Mining and quarrying (non-oil) | share of 1.A.2 as separable in the NID | coal mining, metal ores, quarrying and other minerals |
| Manufacturing | 1.A.2 (excluding construction where separable), 2.A-2.C | manufacturing activities, including cement and food, beverage and tobacco |
| Construction | construction sub-category of 1.A.2, if separable in the NID | construction |
| Transport and storage | 1.A.3 | transportation and storage |
| Water, waste and sewerage | 5.A-5.D | water supply, sewerage, waste management and remediation |
| Services (trade, ICT, real estate, hospitality, education, health, professional and other services) | 1.A.4 commercial and institutional, allocated across service activities by GDP share | the corresponding NBS service activities |

Reasons. BTR1 classifies emissions by IPCC process and fuel category, not by industry, so each common sector is defined at the coarsest level at which both an inventory category and a GDP activity exist. Sub-category splits (energy industries, manufacturing, construction) depend on what the National Inventory Document tables print (for example NID Tables 3.9, 3.18 and 3.25, listed in `data/interim/phase0_intensity_notes.md`); where a split is not printed for every year 2020-2022, the sectors are merged rather than split by assumption. Commercial and institutional combustion (1.A.4) has no industry dimension in the inventory, so it is allocated across service activities in proportion to their GDP; this gives every service sector the same intensity, which is stated as a limitation.

The allocation of national emissions is production-based: emissions from electricity generation are assigned to the power sector, not to the electricity users. Each inventory tonne is counted once, which avoids double counting across sectors, but borrowers' purchased-electricity (Scope 2) emissions are not attributed to them. This is recorded as a limitation (section 9).

### Rules for categories that do not map to a production activity

Each rule is applied to every bank label assigned to that group, and each has a sensitivity listed in section 7.

| Printed category type | Main rule | Sensitivity | Reason |
|---|---|---|---|
| General commerce, trade | services intensity (trade is an NBS activity; its direct emissions are in 1.A.4) | economy-wide average intensity | a trade loan finances the trader, whose direct emissions are commercial combustion and own transport; goods traded are counted in the producing sectors |
| "Other", "others", "miscellaneous", product labels such as "Non-interest banking" (STERLINGNG) | economy-wide average intensity (BTR1 national total excluding LULUCF divided by total GDP at current basic prices) | zero direct intensity | no information on the borrowers; the economy-wide average is the neutral choice |
| Individuals, retail, consumer, personal | zero direct intensity | economy-wide average intensity | household borrowing is not a production activity in the national accounts, and household residential combustion (1.A.4 residential) is not attributable to retail lending without product detail |
| Government, public sector, state governments | services intensity (public administration) | zero direct intensity | loans to public bodies finance public administration; sovereign-level attribution of national emissions is a different PCAF asset class and is not applied |
| Finance and insurance, including loans to other financial institutions | services intensity (finance and insurance) | zero direct intensity | the direct emissions of financial firms are services emissions; the zero rule avoids attributing emissions that the borrowing institutions would in turn finance |

The economy-wide average and the services intensity are computed for each year on the same basis as the sector intensities (section 5).

### Crosswalk file

The crosswalk is written to `data/processed/sector_crosswalk.csv` before any intensity is applied, with one row per distinct printed label per bank: symbol, label as printed, years in which the label appears, common sector, rule applied (mapped, services, economy-wide, zero), and a note on ambiguous labels. A second file, `data/processed/btr1_nbs_sector_map.csv`, maps each common sector to its BTR1 categories and NBS activities. Both are reviewed and signed off by the author before section 6 is run; changes after sign-off are logged as deviations.

Recorded addition, 2026-11-05 (author sign-off of the crosswalk and sector map). The rows proposed for review in Phase 2a (`docs/phase2a_results.md`) are settled as follows; no other rule in this plan changes.

1. Undivided "Oil and gas" (any bank that prints oil and gas as one category) is split into upstream, downstream and services using, for each year, the simple average of the shares printed by the banks that print that split (Access and FCMB, main specification). A bank-year is used only if all three rows are printed; Access FY2025 omits its downstream row, so 2025 uses FCMB alone. The shares and their source pages are recorded in `data/processed/sector_crosswalk_splits.csv` and `data/interim/oil_gas_split_shares.csv`. Components: upstream to oil and gas upstream; downstream and services as in items 2 and 3.
2. "Oil and gas - services" is mapped to services.
3. "Oil and gas - downstream" stays in services (trade, under the general commerce rule). The target of S3f is therefore services.
4. Combined categories (construction and real estate; information, telecommunications and transport) are split by the NBS GDP shares (current basic prices) of their two activities in the same year: construction (NBS 24) and real estate (NBS 40); transport (NBS 27-32) and information and communication (NBS 33-36). 2025 uses the 2024 shares, because NBS 2025 GDP by activity was not located (section 5).
5. Kept as proposed: "General" (economy-wide average; zero under S3b); Stanbic "Mining" (oil and gas upstream, because Stanbic prints no oil and gas row); First HoldCo "Utilities" (power); First HoldCo "Retail services" (services, general commerce rule); Access "Conglomerate" (manufacturing); "Mortgage" (zero, individuals rule); Unity "Utilities" and Fidelity "Other public utilities" (water, waste and sewerage).
6. Sector map: other energy industries (1.A.1.c) are assigned to oil and gas upstream; fuel combustion in agriculture, forestry and fishing (1.A.4.c) and fuel transformation (charcoal production, 1.B.1.b) to agriculture, forestry and fishing; coal mining and handling (1.B.1.a) to the non-oil mining group, which is merged with manufacturing and construction because the NID does not split 1.A.2 (this section, "where a split is not printed ... the sectors are merged").

The sensitivities that go with these decisions are S3g-S3l (section 7).

## 5. Emission intensity

### Definition

Sector intensity for common sector s in year t:

intensity(s, t) = BTR1 emissions of s in year t (t CO2e) ÷ NBS gross value added of s in year t at current basic prices (naira)

expressed in tCO2e per naira. Emissions come from BTR1 Table 2.10 (`data/raw/intensity/Nigeria_BTR1.pdf`, PDF pp. 54-62, kt CO2e, 2000-2022) and, where sub-category splits are needed, the NID (`data/raw/intensity/Nigeria_BTR1_NID_2024.pdf`). GDP comes from the NBS rebasing annex (`data/raw/intensity/nbs_microdata_147_1256.pdf`, current basic prices PDF p. 7, 2019-2024, base year 2019). Units of the NBS table are recorded from the page when extracted.

Known extraction issues: Table 2.10 is split over nine pages in three year-blocks, and the year header on PDF p. 56 is printed "2014 2016 2016"; the column year is assigned from position and checked against the printed 2022 totals on PDF p. 62 (328,496.23 kt CO2e without LULUCF, 554,095.14 kt CO2e with LULUCF).

### Price basis

Exposures are year-end balances in nominal naira. GDP at current basic prices is in nominal naira of the same year. Both are therefore on a current-price basis for year t, and intensities are always computed with same-year GDP. Constant-price GDP (PDF p. 8) is not used for the intensity, because it would divide a nominal exposure by a real denominator. The remaining mismatch, a year-end stock against an annual flow, is recorded as a limitation; for group exposures it includes foreign-currency loans translated at the closing exchange rate.

### Years 2020-2022

Same-year BTR1 emissions and same-year NBS GDP.

### Years 2023-2025

BTR1 ends in 2022. Two options were considered.

Option A: emissions of each sector held at their 2022 level and divided by each later year's GDP at current basic prices.

Option B: BTR1 2022 sector emissions extended to 2023 and 2024 using the growth of the corresponding PIK series (Climate Watch API, `data/raw/intensity/climatewatch_NGA_PIK_2026-11-03.json`, 1850-2024).

Option A is the main specification. Reasons: it keeps a single emissions source with the BTR1 category detail; the PIK series in the Climate Watch API is available only at IPCC top-level sectors (agriculture, energy, industrial processes and product use, waste, other; Phase 0 table d), so it cannot extend the energy sub-categories separately and would apply one energy growth rate to power, transport, manufacturing combustion and oil and gas; and Option A introduces no further source with a different method. Option B is run as a sensitivity (section 7), applying each top-level PIK growth ratio to all common sectors within that top-level sector.

Holding a per-naira intensity fixed at its 2022 value while naira exposures grow with inflation would raise estimated emissions in proportion to nominal loan growth even if real activity and physical emissions were unchanged, and would overstate later years. Option A avoids this because the denominator is each later year's nominal GDP, which moves with the same price level as the exposures; a fixed 2022 intensity is not used in any specification.

### 2025

The NBS GDP by activity for 2025 was not located or opened in Phase 0 (press coverage reports a Q4 2025 release in February 2026; `data/interim/phase0_intensity_notes.md`). Rule: 2025 intensities are computed under Option A only if the NBS 2025 GDP by activity at current basic prices is located, opened and logged. If it is not, 2025 is computed with the 2024 intensity, labelled provisional, reported separately, and excluded from the period totals and from the balanced-panel trend; the label states that applying the 2024 per-naira intensity to 2025 nominal exposures carries the inflation bias described above.

## 6. Calculation

For bank b, year t, common sector s:

financed emissions(b, t, s) = exposure(b, t, s) × intensity(s, t)

where exposure is the sum of the bank's printed categories mapped to s (section 4), in naira. Financed emissions for bank b in year t are the sum over sectors; the sample total for year t is the sum over banks; the period total is the sum over years, reported for the available-bank panel and the balanced panel (section 2). Sector shares (RQ2) are each sector's financed emissions divided by the bank or sample total for that year.

This is an economic-activity approximation: it attributes to each naira lent the national average emissions per naira of value added in the borrower's sector. It corresponds most closely to PCAF data-quality score 5 for business loans (emissions estimated from economic activity with sector-average factors), but it is not a PCAF calculation. PCAF attributes a borrower's emissions in proportion to the outstanding amount relative to the borrower's total equity and debt (or enterprise value), using borrower-level or revenue-based data; neither borrower data nor the PCAF emission-factor database (restricted to signatories and accredited partners; `data/raw/intensity/PCAF-2025Database-2Pager-R2.pdf`, p. 1) is available to this study. The method implicitly assumes that one naira of loan finances one naira of sector value added.

Value added is smaller than revenue (gross output) for the same activity, so an intensity per naira of value added is higher than a revenue-based factor of the kind PCAF's economic emission factors use (CEDA-based; PCAF information sheet p. 2). Estimates on this basis are not directly comparable with revenue-based estimates, and this is listed as a limitation (section 9). The direction of the difference is known; its size is not estimated in this study.

## 7. Sensitivities, fixed in advance

Each sensitivity changes one element of the main specification, holds the rest fixed, and is reported as the bank-year and total estimate alongside the main result. No sensitivity is chosen or dropped after seeing results.

| # | Element | Main specification | Alternative |
|---|---|---|---|
| S1 | Level | group | bank (Nigeria) level, for bank-years where a Nigerian-bank column is printed (section 3) |
| S2 | Basis | gross, carrying where gross not printed | carrying amount for all bank-years where it is printed |
| S3a | Commerce and trade | services intensity | economy-wide average |
| S3b | "Other" and product labels | economy-wide average | zero |
| S3c | Individuals and retail | zero | economy-wide average |
| S3d | Government | services intensity | zero |
| S3e | Finance and insurance | services intensity | zero |
| S3f | Access 2025 printed-total residual (added 2026-11-04, see below) | economy-wide average ("Other" rule) | the common sector to which Access's "Oil And Gas - downstream" label is mapped in the crosswalk (services, per the 2026-11-05 sign-off) |
| S3g | Undivided oil and gas (added 2026-11-05) | split by Access/FCMB average shares (section 4) | all to oil and gas upstream |
| S3h | Undivided oil and gas (added 2026-11-05) | split by Access/FCMB average shares | all to downstream (services, general commerce rule) |
| S3i | "Oil and gas - services" and the services share of split oil and gas (added 2026-11-05) | services | oil and gas upstream |
| S3j | "Oil and gas - downstream" and the downstream share of split oil and gas (added 2026-11-05) | services (general commerce rule) | oil refining |
| S3k | Combined categories: construction and real estate; information, telecommunications and transport (added 2026-11-05) | split by same-year NBS GDP shares | construction; transport (single mapping) |
| S3l | Stanbic "Mining" (added 2026-11-05) | oil and gas upstream | mining and quarrying (non-oil) |
| S4 | 2023-2025 intensity | Option A (emissions held at 2022, later-year GDP) | Option B (emissions extended with PIK top-level growth to 2024; 2025 as in section 5) |
| S5 | LULUCF | excluded from agriculture | BTR1 category 4 LULUCF added to agriculture emissions |
| S6 | Emissions source | BTR1 sector emissions | Climate Watch source sector emissions (Climate Watch API, 1990-2023) mapped to the common sectors, same GDP denominators |

Recorded addition, 2026-11-04 (S3f). The Access Holdings FY2025 sector table omits its "Oil And Gas - downstream" row, so the printed total exceeds the printed rows by 249,219 million naira. By author decision this difference is carried as one row, "unallocated (printed total residual)" (`docs/phase1b_results.md`, deviation 8). In the main specification it takes the "Other" rule (economy-wide average intensity); S3f assigns it instead to the common sector of Access's "Oil And Gas - downstream" label in other years. S3f was added after Phase 1b extraction and before any intensity or estimate was computed. No other rule or sensitivity is changed by this addition.

Recorded addition, 2026-11-05 (S3g-S3l). These sensitivities accompany the author's sign-off of the crosswalk and sector map (section 4, recorded addition of the same date). They were fixed before any intensity or estimate was computed. "General" takes the "Other" rule, so its zero sensitivity is S3b and needs no new entry. No other rule or sensitivity is changed by this addition.

Reasons for the main choices not argued above. S5: LULUCF emissions and removals arise from land-use change across many land users and cannot be tied to the agricultural borrowers of commercial banks; excluding them is the conservative main case, and the printed BTR1 totals with and without LULUCF show that the choice is material at national level. S6: Climate Watch sectors (electricity/heat, manufacturing/construction, transportation, building, fugitive emissions, industrial processes, agriculture, waste, LULUCF) map to the common sectors at a similar level of detail, so the sensitivity tests dependence on the inventory source. The Climate Watch licence was not confirmed on an opened page (Phase 0); the sensitivity is computed, but raw Climate Watch values are redistributed in the repository only if the licence is confirmed.

## 8. Validation

1. Extraction accuracy. After extraction, a random sample of extracted sector values is recomputed by reading the PDF page: at least 5% of all extracted sector-row values, and at least one complete table per bank, drawn with a fixed, recorded random seed. Any mismatch triggers a full manual re-check of that table, and the error rate is reported. All OCR values (Jaiz 2024) are checked in full.
2. Internal consistency. For each table, sector rows must sum to the printed total within rounding, defined as no more than half a unit of the printed rounding per row (for example, a 24-row table in millions of naira may differ by up to 12 million naira). The Phase 0 test is consistent with this rule (Access 2023 differences of 2 and -2 million naira on 24 rows; Zenith 2023 differences of zero). Tables that fail are re-extracted; persistent failures are recorded and the bank-year is flagged.
3. External consistency. Each table total is cross-checked with the gross or carrying loans-to-customers figure in the loans note or statement of financial position of the same report, as in the Phase 0 test (for example Access 2023 p. 358, Zenith 2023 pp. 41 and 86). Differences are explained (loans to banks included, off-balance-sheet items, holding-company column) or the bank-year is flagged.
4. Intensity inputs. BTR1 extracted category values must sum to the printed category and national totals for each year; NBS activities must sum to the printed GDP total for each year.
5. Comparison with published figures (RQ3). Estimates for Fidelity (2023, and 2024-2025 once the 2025 annual report page is confirmed) and UBA (2023, 2024) are compared with the published figures on a matched basis as far as the disclosures allow: the same year, level and, for UBA, the coverage share printed (90% in 2023, 52% in 2024). Differences are explained by listing the known sources of divergence (attribution method, borrower Scope 1&2 versus Scope 3, coverage, level, emission factors, value added versus revenue), not reduced by adjusting the method. No parameter of the main specification is changed in response to the comparison.

## 9. Outputs by phase

Phase numbering after 1a is provisional.

| Phase | Work | Outputs |
|---|---|---|
| 1b Extraction | sector tables for 12 banks 2020-2025, OCR for Jaiz 2024, loans-note totals, basis and level per bank-year | `data/processed/exposures_by_sector.csv` (fields in section 3), `data/processed/sample.csv` (bank-years included or excluded, with reasons), `data/interim/extraction_validation.csv`, `docs/phase1b_results.md` |
| 2 Mapping and intensities | crosswalk, BTR1 and NID extraction, NBS GDP extraction, 2025 GDP search, IFRS S2 and FRC documents opened | `data/processed/sector_crosswalk.csv`, `data/processed/btr1_nbs_sector_map.csv`, `data/processed/btr1_emissions_by_category.csv`, `data/processed/nbs_gdp_by_activity.csv`, `data/processed/sector_intensity.csv`, `docs/phase2_results.md` |
| 3 Estimation | main specification and sensitivities S1-S6 | `data/processed/financed_emissions_main.csv` (bank, year, sector), `data/processed/financed_emissions_sensitivities.csv`, `docs/phase3_results.md` |
| 4 Comparison, disclosure and write-up | RQ3 comparison, RQ4 disclosure table, figures | `data/processed/published_comparison.csv`, `data/processed/disclosure_table.csv`, `figures/`, `docs/results.md` |

Each phase's code goes in `src/bank_emissions/` with tests in `tests/`, and each results document lists failures and deviations from this plan.

Recorded additions, 2026-11-05 (Phase 3 and Phase 4). These add reporting without changing any estimation rule:

1. Sensitivity flag (reporting rule). A sensitivity is flagged for a bank-year as driven by oil refining, or by water, waste and sewerage, when the change in financed emissions from lines targeted at that intensity group is at least half of the net change against the main specification, in absolute terms.
2. Change over time (descriptive). The change in financed emissions from 2022 to 2024, for each balanced-panel bank and the balanced-panel total, is decomposed by additive LMDI-I over intensity groups into an exposure effect (total exposure and sector mix) and an intensity effect. Amended 2026-11-05: the effect of the year-varying split shares of undivided "Oil and gas" (section 4, item 1 of the 2026-11-05 sign-off) is reported as its own line, measured as actual 2024 minus a 2024 counterfactual that uses the 2022 split shares; the LMDI terms (volume, printed sector mix, intensity) run from 2022 to that counterfactual, so the four lines sum to the change.
3. Constant 2022 naira (descriptive). Total loans are restated in constant 2022 naira with the implicit GDP deflator at basic prices (NBS rebasing annex, current and constant 2019 basic prices, PDF pp. 7-8), and financed emissions are restated with those exposures and the 2022 intensities. 2025 is not restated (no deflator).

### What the study cannot claim

- That the estimates are any bank's actual financed emissions. They are sector-average approximations of the emissions associated with each bank's loan mix, not attributions of identified borrowers' emissions.
- That the estimates follow the PCAF Standard, or that they meet the IFRS S2 measurement requirements. They are comparable in kind to PCAF data-quality score 5, without PCAF's attribution factor or emission factors.
- That a difference between an estimate and a published figure shows that either is wrong. The two use different methods, coverage and possibly scopes.
- That differences between banks reflect differences in borrower emission efficiency. Within a sector every bank receives the same intensity, so differences arise only from sector mix and loan volume.
- That changes over 2023-2025 reflect changes in physical emissions. Sector emissions after 2022 are held at 2022 (or extended with a top-level series), so later-year changes come from exposures and GDP.
- That loans booked by foreign subsidiaries carry Nigerian emission intensities. Group-level estimates for flagged banks apply Nigerian intensities to the whole loan book.
- That borrowers' purchased-electricity (Scope 2) and value-chain (Scope 3) emissions are included. The production-based allocation assigns electricity emissions to the power sector only, and no Scope 3 of borrowers is estimated.
- That emissions from loans to individuals, government or financial institutions are measured. They are set by the rules in section 4, and the sensitivities show how much the totals depend on those rules.
- That results cover the whole Nigerian banking system. The sample is the NGX-listed banks with sector notes, excluding ETI and Unity Bank after 2023, and only loans and advances to customers; securities, interbank lending and off-balance-sheet exposures are excluded.
- That value-added-based intensities are comparable to revenue-based factors. They are higher by construction, and the size of the difference is not estimated.
