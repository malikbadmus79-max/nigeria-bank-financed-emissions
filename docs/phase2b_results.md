# Phase 2b results: sector emission intensities

Date: 2026-11-05. Plan: `docs/analysis_plan.md` section 5, sensitivities S4-S6 of section 7, and the signed-off sector map (`data/processed/btr1_nbs_sector_map.csv`, Phase 2a). No financed emissions are computed. Phase 1b and Phase 2a outputs are unchanged (SHA-256 manifests `data/interim/phase1b_outputs_manifest.json` and `phase2a_outputs_manifest.json`, checked by `tests/test_phase2b.py`).

## Outputs

| File | Content |
|---|---|
| `data/processed/sector_intensity.csv` | 162 rows: 9 intensity groups (8 sectors and the economy-wide average) x 6 years (2020-2025) x 3 specifications (main, S4_PIK, S5_LULUCF): emissions (kt and t CO2e), GDP (naira, current basic prices), intensity (t CO2e per naira and per million naira), years used, method, provisional flag, source categories and pages |
| `data/interim/pik_growth_ratios.csv` | PIK growth ratios (2023 and 2024 relative to 2022) by IPCC top-level sector, used in S4 |
| `data/interim/intensity_checks.csv` | 85 checks: 67 pass, 18 informational, none fail |
| `data/raw/derived/sector_intensity_s6_climatewatch.csv`, `intensity_checks_s6.csv` | S6 (Climate Watch) rows and checks; git-ignored, not committed (see S6) |

Code: `src/bank_emissions/phase2b_intensity.py` (`python -m bank_emissions.phase2b_intensity`).

## Method

Intensity = emissions of the group's inventory categories (t CO2e) / NBS GDP of the group's activities at current basic prices (naira). Groups, categories and activities are read from the signed-off sector map. BTR1 Table 2.10 values are used where Table 2.10 prints the category (two decimals); NID sub-category values (whole kt) are used for 1.A.1.a-c, 1.A.4.a-c and 1.B.1.a-b. Notation keys (NE, NO, NA, FX) count as zero.

| Years | Emissions | GDP | Rule |
|---|---|---|---|
| 2020-2022 | same year | same year | plan section 5 |
| 2023-2024 | 2022 | same year | Option A (main specification) |
| 2025 | 2022 | 2024 | provisional: the 2024 intensity, flagged, outside period totals and the balanced-panel trend (NBS 2025 GDP by activity not located, Phase 2a) |

Economy-wide average: BTR1 total CO2 equivalent emissions without LULUCF (PDF p. 62) / GDP at current basic prices summed over all 46 NBS activities.

## Main specification

Intensity, t CO2e per million naira (current basic prices):

| Intensity group | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 (prov.) |
|---|---|---|---|---|---|---|
| Agriculture, forestry and fishing | 1.336 | 1.137 | 1.069 | 0.962 | 0.868 | 0.868 |
| Oil and gas, upstream | 4.303 | 4.154 | 3.335 | 3.047 | 2.735 | 2.735 |
| Oil refining | 0.000 | 16.199 | 49.310 | 66.323 | 82.935 | 82.935 |
| Power | 15.298 | 8.987 | 9.277 | 6.817 | 6.011 | 6.011 |
| Manufacturing, construction and non-oil mining (merged) | 0.948 | 0.891 | 0.715 | 0.623 | 0.550 | 0.550 |
| Transport and storage | 23.978 | 25.968 | 23.673 | 20.647 | 15.616 | 15.616 |
| Water, waste and sewerage | 79.456 | 70.417 | 69.851 | 63.479 | 48.871 | 48.871 |
| Services | 0.025 | 0.025 | 0.028 | 0.024 | 0.019 | 0.019 |
| Economy-wide average | 1.468 | 1.336 | 1.211 | 1.061 | 0.901 | 0.901 |

Emissions, kt CO2e (2023-2025 hold the 2022 values):

| Intensity group | 2020 | 2021 | 2022 |
|---|---|---|---|
| Agriculture, forestry and fishing (3, 1.A.4.c, 1.B.1.b) | 80,927.6 | 81,271.2 | 83,712.6 |
| Oil and gas, upstream (1.B.2, 1.A.1.c) | 43,872.4 | 40,028.6 | 39,932.0 |
| Oil refining (1.A.1.b) | 0.0 | 513.0 | 979.0 |
| Power (1.A.1.a) | 17,025.0 | 17,441.0 | 18,231.0 |
| Manufacturing, construction and non-oil mining (1.A.2, 2.A-2.C, 1.B.1.a) | 26,000.1 | 28,771.1 | 27,202.2 |
| Transport and storage (1.A.3) | 52,009.4 | 58,948.0 | 59,044.8 |
| Water, waste and sewerage (5) | 36,124.2 | 37,074.9 | 38,049.9 |
| Services (1.A.4.a) | 2,705.0 | 3,052.0 | 3,794.0 |
| Residential combustion, not attributed (1.A.4.b) | 52,082.0 | 54,485.0 | 57,550.0 |
| National total without LULUCF | 310,745.7 | 321,584.9 | 328,496.2 |

GDP at current basic prices, naira trillion:

| Intensity group | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| Agriculture, forestry and fishing | 60.556 | 71.502 | 78.298 | 87.042 | 96.462 |
| Oil and gas, upstream | 10.196 | 9.636 | 11.973 | 13.106 | 14.601 |
| Oil refining | 0.056 | 0.032 | 0.020 | 0.015 | 0.012 |
| Power | 1.113 | 1.941 | 1.965 | 2.674 | 3.033 |
| Manufacturing, construction and non-oil mining | 27.415 | 32.277 | 38.065 | 43.679 | 49.417 |
| Transport and storage | 2.169 | 2.270 | 2.494 | 2.860 | 3.781 |
| Water, waste and sewerage | 0.455 | 0.527 | 0.545 | 0.599 | 0.779 |
| Services | 109.749 | 122.570 | 137.845 | 159.535 | 196.535 |
| Total | 211.708 | 240.755 | 271.205 | 309.511 | 364.619 |

Petroleum refining combustion (1.A.1.b) is printed as 0 in 2020 (NID Table 3.9), so the 2020 refining intensity is 0.

## Sensitivities that change intensities

S4 (Option B, PIK). Each BTR1 2022 category (and NID sub-category) is multiplied by the PIK growth of its IPCC top-level sector (Kyoto GHG, Climate Watch API, source PIK); 2020-2022 are as in the main specification; 2025 is the S4 2024 intensity (provisional). Growth ratios relative to 2022: energy 0.995 (2023) and 1.015 (2024); industrial processes 1.000 and 1.000; agriculture 1.0205 and 1.0372; waste 1.0289 and 1.0526. The economy-wide total is the sum of extended categories 1, 2, 3 and 5 (category 6 is not estimated).

| Intensity group, t CO2e per million naira | 2023 | 2024 |
|---|---|---|
| Agriculture, forestry and fishing | 0.980 | 0.899 |
| Oil and gas, upstream | 3.032 | 2.776 |
| Oil refining | 65.991 | 84.179 |
| Power | 6.783 | 6.101 |
| Manufacturing, construction and non-oil mining | 0.621 | 0.555 |
| Transport and storage | 20.544 | 15.850 |
| Water, waste and sewerage | 65.316 | 51.443 |
| Services | 0.024 | 0.020 |
| Economy-wide average | 1.067 | 0.923 |

S5 (LULUCF added to agriculture). BTR1 category 4 (net LULUCF) is added to the agriculture group; other groups are unchanged; the economy-wide average uses the national total with LULUCF. Agriculture: 4.798 (2020), 4.087 (2021), 3.950 (2022), 3.554 (2023), 3.207 (2024 and 2025 provisional). Economy-wide: 2.458, 2.212, 2.043, 1.790, 1.520, 1.520.

S6 (Climate Watch). Computed; values not committed. The plan (section 7) allows redistributing raw Climate Watch values only if the licence is confirmed on an opened page. A search on 2026-11-05 did not reach the climatewatchdata.org terms page; secondary listings of the historical emissions dataset give both CC BY 4.0 and CC BY-NC 4.0. The S6 rows and their checks are written to `data/raw/derived/` (git-ignored) and are rebuilt from the raw API file by the same command; the committed check file records pass/fail only. All 12 S6 checks pass. Mapping used (Climate Watch source 'Climate Watch', all GHG): Agriculture and Other Fuel Combustion to agriculture; Electricity/Heat to power; Fugitive Emissions to oil and gas upstream; Manufacturing/Construction and Industrial Processes to the merged manufacturing group; Transportation to transport; Waste to water and waste; Building to services in proportion to the BTR1 commercial share of 1.A.4 (1.A.4.a / (1.A.4.a + 1.A.4.b)) of the same year, the rest unattributed. Refining has no Climate Watch counterpart, and the BTR1 refining emissions are kept. 2023-2024 hold the 2022 Climate Watch values (Option A; S6 changes only the emissions source, although Climate Watch prints 2023).

## Checks (`data/interim/intensity_checks.csv`)

1. Recomputation: the 54 main-specification intensities were recomputed by a separate function that filters the input CSVs directly; all 54 agree (largest absolute difference 0).
2. Assigned emissions plus unattributed residential combustion equal the national total (24 checks: 4 specifications x 6 years, all pass). Main specification: differences of -0.05 kt (2020), -0.10 kt (2021) and -0.72 kt (2022 to 2025) against a tolerance of 4.51 kt (NID sub-categories are whole kt). S6 uses a tolerance of 50 kt (Climate Watch publishes Mt to two decimals).
3. GDP of the groups sums to total GDP in every year and specification (24 checks, all pass).
4. GDP-weighted average of group intensities against the economy-wide intensity (18 checks, informational). The two are not equal by construction: the economy-wide average includes residential combustion, which no group carries. In every year the gap equals unattributed residential emissions / total GDP. Main specification, t CO2e per million naira:

| Year | GDP-weighted average of groups | Economy-wide | Difference = residential / total GDP |
|---|---|---|---|
| 2020 | 1.2218 | 1.4678 | 0.2460 |
| 2021 | 1.1094 | 1.3357 | 0.2263 |
| 2022 | 0.9990 | 1.2112 | 0.2122 |
| 2023 | 0.8754 | 1.0613 | 0.1859 |
| 2024 | 0.7431 | 0.9009 | 0.1578 |
| 2025 (prov.) | 0.7431 | 0.9009 | 0.1578 |

   The identity "weighted average + residential / total GDP = economy-wide" is checked instead (18 checks, all pass; largest relative difference 2.2e-6, from NID whole-kt rounding).

## Departures and notes

1. The requested check that the GDP-weighted average of group intensities equals the economy-wide intensity does not hold, because unattributed residential combustion (16.8-17.5% of national emissions) is in the economy-wide total and in no group. The check is replaced by the identity above, and the gap is reported each year.
2. S5: the economy-wide average uses the national total with LULUCF. The plan says the economy-wide average is computed "on the same basis as the sector intensities"; with LULUCF added to agriculture, that basis includes LULUCF.
3. S4: PIK top-level values in the API file are rounded to about three significant figures (for example energy 200, 199 and 203 Mt CO2e for 2022-2024), which sets the precision of the growth ratios. The industrial-processes ratio is exactly 1.000 in both years. Only the ratios are written to the repository; the PIK values come from the Climate Watch API file in `data/raw/`.
4. S6 values are not committed (licence condition). The S6 mapping choices (Building split by the BTR1 commercial share; refining kept from BTR1; Other Fuel Combustion to agriculture; Fugitive Emissions, which include solid fuels, to oil and gas upstream) are not set out in the plan and need sign-off before S6 is used.
5. NID sub-category values are whole kt; group totals that use them carry up to 0.5 kt of rounding per sub-category.
6. 2025 intensities are provisional (plan section 5): the 2024 intensity, flagged in every 2025 row, and excluded from period totals and the balanced-panel trend.
