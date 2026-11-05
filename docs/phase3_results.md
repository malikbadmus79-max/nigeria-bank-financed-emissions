# Phase 3 results: financed-emissions estimates

Date: 2026-11-05. Plan: `docs/analysis_plan.md` sections 6 and 7, with the signed-off crosswalk, splits and sector map (Phase 2a) and intensities (Phase 2b). Earlier outputs are unchanged: SHA-256 manifests for Phases 1b, 2a and 2b are checked by `tests/test_phase3.py`. Figures are reported without interpretation; no comparison with published figures is made here (Phase 4).

## Outputs

| File | Content |
|---|---|
| `data/processed/financed_emissions_main.csv` | main specification, one line per exposure row (or per component of a split label): bank, year, level, basis, printed category, component and share, rule, common sector, intensity group, exposure (naira), intensity (t CO2e per naira), t CO2e |
| `data/processed/financed_emissions_bank_year.csv` | totals by bank-year, with balanced-panel membership and provisional flag |
| `data/processed/financed_emissions_totals.csv` | totals by year and for 2020-2024: all available banks; balanced panel |
| `data/processed/financed_emissions_sector_year.csv` | by reporting sector and year, both total types, with shares |
| `data/processed/financed_emissions_bank_sector.csv` | by bank-year and reporting sector, with shares |
| `data/processed/financed_emissions_sensitivities.csv` | by bank-year: main, S1-S6 (blank where not applicable), minimum and maximum with the sensitivity setting each, driver flags; plus total rows for both total types |
| `data/interim/sensitivity_flags.csv` | bank-years where a change is driven by oil-refining or water-and-waste lines |
| `data/interim/estimation_checks.csv` | checks |

Code: `src/bank_emissions/phase3_estimate.py` (`python -m bank_emissions.phase3_estimate`).

## Method

Each main-specification exposure row (`exposures_by_sector.csv`, `main_spec` true; 70 bank-years) becomes one line, or one line per component for the 18 split labels (component exposure = row exposure x share). A line's intensity is that of its target: the intensity group of its common sector (rule "mapped"; construction, manufacturing and non-oil mining share the merged group), the services intensity (services rule: commerce, government, finance), the economy-wide average (economy-wide rule) or zero (zero rule; not a loan exposure). Financed emissions = exposure x intensity of the same year (`sector_intensity.csv`, specification "main"). 2025 uses the provisional intensities and is kept out of the period totals and trends.

Total types (plan section 2): all available banks in each year, and a balanced panel of the banks present in every year 2020-2025: 11 banks (all sampled banks except Unity Bank, which has no 2024-2025 figures). From 2024 the two total types coincide.

Sensitivities (plan section 7, each changing one element):
- S1: bank (Nigeria) level, gross where printed, else carrying; applies to bank-years with a bank-level table. Where the main specification is already bank level (Fidelity 2020-2022, Unity Bank, Jaiz Bank) S1 equals main.
- S2: carrying amount at the main level where printed; where the main basis is already carrying (GTCO, UBA, First HoldCo 2020-2021) S2 equals main.
- S3a-S3l: the target of lines carrying the sensitivity's tag (crosswalk or split component) is changed; a bank-year with no tagged line is not applicable.
- S4: Option B intensities (2023 onwards only); S5: LULUCF added to agriculture, economy-wide with LULUCF; S6: Climate Watch intensities.
In the total rows of the sensitivities file, bank-years where a sensitivity does not apply keep their main value.

## Totals

| Total type | Year | Banks | Exposure (naira trillion) | Financed emissions (Mt CO2e) |
|---|---|---|---|---|
| all available banks | 2020 | 12 | 16.912 | 35.240 |
| all available banks | 2021 | 12 | 20.529 | 37.742 |
| all available banks | 2022 | 12 | 24.700 | 39.612 |
| all available banks | 2023 | 12 | 39.187 | 59.171 |
| all available banks | 2024 | 11 | 54.266 | 78.338 |
| all available banks | 2025 (prov.) | 11 | 57.172 | 77.389 |
| all available banks | 2020-2024 | 12 | 155.592 | 250.104 |
| balanced panel | 2020 | 11 | 16.705 | 34.980 |
| balanced panel | 2021 | 11 | 20.256 | 37.424 |
| balanced panel | 2022 | 11 | 24.407 | 39.330 |
| balanced panel | 2023 | 11 | 38.825 | 58.836 |
| balanced panel | 2024 | 11 | 54.266 | 78.338 |
| balanced panel | 2025 (prov.) | 11 | 57.172 | 77.389 |
| balanced panel | 2020-2024 | 11 | 154.459 | 248.908 |

## Main specification by bank-year (Mt CO2e)

| Bank | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 (prov.) | Level/basis (main) |
|---|---|---|---|---|---|---|---|
| ACCESSCORP | 5.509 | 7.824 | 9.945 | 17.252 | 19.812 | 19.540 | group/gross |
| FCMB | 1.454 | 1.198 | 1.387 | 1.424 | 2.266 | 2.150 | group/gross |
| FIDELITYBK | 6.758 | 8.225 | 8.342 | 10.287 | 14.369 | 14.412 | bank/gross; group/gross |
| FIRSTHOLDCO | 4.583 | 4.149 | 4.749 | 7.663 | 11.405 | 11.654 | group/carrying; group/gross |
| GTCO | 1.330 | 1.444 | 1.322 | 1.894 | 2.229 | 2.417 | group/carrying |
| JAIZBANK | 0.067 | 0.145 | 0.160 | 0.332 | 0.351 | 0.608 | bank/gross |
| STANBIC | 1.024 | 1.560 | 1.845 | 3.135 | 3.402 | 3.501 | group/gross |
| STERLINGNG | 1.267 | 1.429 | 1.616 | 2.004 | 2.036 | 2.436 | group/gross |
| UBA | 5.247 | 3.482 | 3.552 | 5.566 | 7.390 | 7.707 | group/carrying |
| UNITYBNK | 0.260 | 0.318 | 0.282 | 0.335 |  |  | bank/gross |
| WEMABANK | 0.992 | 1.068 | 1.097 | 1.916 | 2.824 | 3.870 | group/gross |
| ZENITHBANK | 6.747 | 6.901 | 5.315 | 7.364 | 12.254 | 9.095 | group/gross |

## Shares by reporting sector (% of the year's financed emissions)

Balanced panel:

| Reporting sector | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 (prov.) |
|---|---|---|---|---|---|---|
| Agriculture, forestry and fishing | 2.4 | 2.6 | 2.8 | 2.6 | 2.5 | 3.4 |
| Construction | 1.8 | 1.7 | 1.4 | 1.3 | 1.1 | 1.3 |
| Individuals and other zero-rule | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Manufacturing | 7.6 | 8.1 | 8.5 | 6.9 | 5.9 | 4.3 |
| Mining and quarrying (non-oil) | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 |
| Not a loan exposure |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Oil and gas, upstream | 13.8 | 12.6 | 12.5 | 18.2 | 28.6 | 23.5 |
| Oil refining | 0.0 | 0.5 | 5.9 | 4.9 | 4.4 | 1.9 |
| Other (economy-wide average rule) | 3.5 | 5.1 | 5.7 | 5.3 | 4.9 | 8.3 |
| Power (electricity and gas supply) | 33.6 | 19.0 | 19.5 | 17.1 | 16.7 | 18.8 |
| Services | 0.6 | 0.7 | 0.8 | 0.8 | 0.6 | 0.7 |
| Transport and storage | 36.6 | 49.7 | 42.0 | 42.5 | 34.5 | 37.0 |
| Water, waste and sewerage | 0.2 | 0.1 | 0.6 | 0.4 | 0.6 | 0.7 |

All available banks:

| Reporting sector | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 (prov.) |
|---|---|---|---|---|---|---|
| Agriculture, forestry and fishing | 3.0 | 3.3 | 3.4 | 3.1 | 2.5 | 3.4 |
| Construction | 1.8 | 1.7 | 1.4 | 1.3 | 1.1 | 1.3 |
| Individuals and other zero-rule | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Manufacturing | 7.6 | 8.0 | 8.5 | 6.8 | 5.9 | 4.3 |
| Mining and quarrying (non-oil) | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 |
| Not a loan exposure |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Oil and gas, upstream | 13.7 | 12.5 | 12.4 | 18.1 | 28.6 | 23.5 |
| Oil refining | 0.0 | 0.5 | 5.9 | 4.9 | 4.4 | 1.9 |
| Other (economy-wide average rule) | 3.5 | 5.0 | 5.7 | 5.3 | 4.9 | 8.3 |
| Power (electricity and gas supply) | 33.4 | 18.8 | 19.4 | 17.0 | 16.7 | 18.8 |
| Services | 0.6 | 0.7 | 0.8 | 0.8 | 0.6 | 0.7 |
| Transport and storage | 36.3 | 49.2 | 41.7 | 42.3 | 34.5 | 37.0 |
| Water, waste and sewerage | 0.2 | 0.2 | 0.6 | 0.4 | 0.6 | 0.7 |

Construction, manufacturing and non-oil mining are shown separately but share one intensity (the merged group). "Other (economy-wide average rule)" covers labels under the "Other" rule, including "General" and the Access 2025 residual.

## Sensitivities: totals (Mt CO2e)

All available banks:

| Specification | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 (prov.) | 2020-2024 |
|---|---|---|---|---|---|---|---|
| main | 35.24 | 37.74 | 39.61 | 59.17 | 78.34 | 77.39 | 250.10 |
| S1 | 32.75 | 34.97 | 38.61 | 55.91 | 73.25 | 72.97 | 235.49 |
| S2 | 34.57 | 37.53 | 39.41 | 58.32 | 76.56 | 76.31 | 246.39 |
| S3a | 38.42 | 41.81 | 44.49 | 66.05 | 86.85 | 87.16 | 277.62 |
| S3b | 33.99 | 35.84 | 37.37 | 56.04 | 74.49 | 70.99 | 237.73 |
| S3c | 36.30 | 39.07 | 40.83 | 60.71 | 79.81 | 78.92 | 256.72 |
| S3d | 35.20 | 37.69 | 39.55 | 59.10 | 78.27 | 77.30 | 249.81 |
| S3e | 35.23 | 37.73 | 39.59 | 59.15 | 78.30 | 77.34 | 250.01 |
| S3f | 35.24 | 37.74 | 39.61 | 59.17 | 78.34 | 77.17 | 250.10 |
| S3g | 45.91 | 49.44 | 50.52 | 76.10 | 95.64 | 93.78 | 317.61 |
| S3h | 32.36 | 34.98 | 36.67 | 51.88 | 61.78 | 63.64 | 217.68 |
| S3i | 46.44 | 49.56 | 49.58 | 73.70 | 90.01 | 86.03 | 309.29 |
| S3j | 35.22 | 54.31 | 111.27 | 197.16 | 366.72 | 371.46 | 764.69 |
| S3k | 38.05 | 41.55 | 42.67 | 63.23 | 81.15 | 81.84 | 266.66 |
| S3l | 34.67 | 37.04 | 38.95 | 58.15 | 76.84 | 75.71 | 245.66 |
| S4 | 35.24 | 37.74 | 39.61 | 58.97 | 79.57 | 78.65 | 251.13 |
| S5 | 38.85 | 42.24 | 44.81 | 66.23 | 86.20 | 88.94 | 278.35 |
| S6 | 45.71 | 44.61 | 45.03 | 68.38 | 93.71 | 91.45 | 297.44 |

Balanced panel:

| Specification | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 (prov.) | 2020-2024 |
|---|---|---|---|---|---|---|---|
| main | 34.98 | 37.42 | 39.33 | 58.84 | 78.34 | 77.39 | 248.91 |
| S1 | 32.49 | 34.65 | 38.33 | 55.58 | 73.25 | 72.97 | 234.29 |
| S2 | 34.32 | 37.21 | 39.13 | 57.99 | 76.56 | 76.31 | 245.21 |
| S3a | 38.16 | 41.49 | 44.21 | 65.71 | 86.85 | 87.16 | 276.43 |
| S3b | 33.74 | 35.53 | 37.09 | 55.71 | 74.49 | 70.99 | 236.57 |
| S3c | 36.04 | 38.76 | 40.54 | 60.37 | 79.81 | 78.92 | 255.52 |
| S3d | 34.94 | 37.38 | 39.27 | 58.77 | 78.27 | 77.30 | 248.61 |
| S3e | 34.97 | 37.41 | 39.31 | 58.81 | 78.30 | 77.34 | 248.81 |
| S3f | 34.98 | 37.42 | 39.33 | 58.84 | 78.34 | 77.17 | 248.91 |
| S3g | 45.64 | 49.12 | 50.23 | 75.77 | 95.64 | 93.78 | 316.40 |
| S3h | 32.10 | 34.66 | 36.39 | 51.55 | 61.78 | 63.64 | 216.49 |
| S3i | 46.17 | 49.24 | 49.30 | 73.37 | 90.01 | 86.03 | 308.08 |
| S3j | 34.96 | 53.99 | 110.98 | 196.81 | 366.72 | 371.46 | 763.46 |
| S3k | 37.79 | 41.23 | 42.39 | 62.90 | 81.15 | 81.84 | 265.46 |
| S3l | 34.41 | 36.72 | 38.67 | 57.82 | 76.84 | 75.71 | 244.46 |
| S4 | 34.98 | 37.42 | 39.33 | 58.63 | 79.57 | 78.65 | 249.93 |
| S5 | 37.97 | 41.19 | 43.81 | 65.03 | 86.20 | 88.94 | 274.21 |
| S6 | 45.43 | 44.29 | 44.74 | 68.04 | 93.71 | 91.45 | 296.21 |

## Sensitivities: range by bank-year (Mt CO2e)

The minimum and maximum are taken over the sensitivities that apply to the bank-year. Across the 70 bank-years the maximum is set by: S3j 46, S6 9, S5 7, S3g 4, S3i 2, S3k 2; the minimum by: S3h 35, S3b 22, S1 7, S3l 6.

| Bank | Year | Main | Min | Set by | Max | Set by  |
|---|---|---|---|---|---|---|
| ACCESSCORP | 2020 | 5.509 | 4.709 | S1 | 8.047 | S3i |
| ACCESSCORP | 2021 | 7.824 | 6.721 | S1 | 10.557 | S3i |
| ACCESSCORP | 2022 | 9.945 | 9.299 | S3b | 23.482 | S3j |
| ACCESSCORP | 2023 | 17.252 | 15.669 | S3b | 35.337 | S3j |
| ACCESSCORP | 2024 | 19.812 | 17.709 | S3b | 53.284 | S3j |
| ACCESSCORP | 2025 (prov.) | 19.540 | 14.922 | S3b | 24.346 | S5 |
| FCMB | 2020 | 1.454 | 1.449 | S3b | 2.188 | S6 |
| FCMB | 2021 | 1.198 | 1.181 | S3b | 2.523 | S3j |
| FCMB | 2022 | 1.387 | 1.369 | S3b | 5.859 | S3j |
| FCMB | 2023 | 1.424 | 1.409 | S3b | 9.703 | S3j |
| FCMB | 2024 | 2.266 | 2.256 | S3b | 19.259 | S3j |
| FCMB | 2025 (prov.) | 2.150 | 2.137 | S3b | 16.740 | S3j |
| FIDELITYBK | 2020 | 6.758 | 6.472 | S3h | 8.268 | S6 |
| FIDELITYBK | 2021 | 8.225 | 7.867 | S3h | 9.860 | S3j |
| FIDELITYBK | 2022 | 8.342 | 7.945 | S3h | 15.598 | S3j |
| FIDELITYBK | 2023 | 10.287 | 9.276 | S3h | 25.769 | S3j |
| FIDELITYBK | 2024 | 14.369 | 11.724 | S3h | 52.375 | S3j |
| FIDELITYBK | 2025 (prov.) | 14.412 | 12.051 | S3h | 62.388 | S3j |
| FIRSTHOLDCO | 2020 | 4.583 | 3.949 | S3h | 6.930 | S3g |
| FIRSTHOLDCO | 2021 | 4.149 | 3.460 | S3h | 7.303 | S3j |
| FIRSTHOLDCO | 2022 | 4.749 | 3.892 | S3h | 20.399 | S3j |
| FIRSTHOLDCO | 2023 | 7.663 | 5.674 | S3h | 38.115 | S3j |
| FIRSTHOLDCO | 2024 | 11.405 | 6.968 | S3h | 75.175 | S3j |
| FIRSTHOLDCO | 2025 (prov.) | 11.654 | 7.696 | S3h | 92.092 | S3j |
| GTCO | 2020 | 1.330 | 0.743 | S3h | 3.887 | S3k |
| GTCO | 2021 | 1.444 | 0.925 | S3h | 4.978 | S3k |
| GTCO | 2022 | 1.322 | 0.832 | S3h | 10.270 | S3j |
| GTCO | 2023 | 1.894 | 0.944 | S3h | 16.431 | S3j |
| GTCO | 2024 | 2.229 | 0.852 | S3h | 22.012 | S3j |
| GTCO | 2025 (prov.) | 2.417 | 1.069 | S3h | 29.812 | S3j |
| JAIZBANK | 2020 | 0.067 | 0.052 | S3b | 0.122 | S5 |
| JAIZBANK | 2021 | 0.145 | 0.133 | S3b | 0.260 | S5 |
| JAIZBANK | 2022 | 0.160 | 0.141 | S3b | 0.377 | S3j |
| JAIZBANK | 2023 | 0.332 | 0.308 | S3h | 0.695 | S3j |
| JAIZBANK | 2024 | 0.351 | 0.291 | S3h | 1.212 | S3j |
| JAIZBANK | 2025 (prov.) | 0.608 | 0.528 | S3h | 2.242 | S3j |
| STANBIC | 2020 | 1.024 | 0.458 | S3l | 1.519 | S6 |
| STANBIC | 2021 | 1.560 | 0.860 | S3l | 2.194 | S6 |
| STANBIC | 2022 | 1.845 | 1.183 | S3l | 2.256 | S6 |
| STANBIC | 2023 | 3.135 | 2.118 | S3l | 3.783 | S6 |
| STANBIC | 2024 | 3.402 | 1.900 | S3l | 4.274 | S6 |
| STANBIC | 2025 (prov.) | 3.501 | 1.821 | S3l | 4.659 | S6 |
| STERLINGNG | 2020 | 1.267 | 1.084 | S3h | 1.943 | S3g |
| STERLINGNG | 2021 | 1.429 | 1.294 | S3h | 2.045 | S3j |
| STERLINGNG | 2022 | 1.616 | 1.477 | S3b | 3.723 | S3j |
| STERLINGNG | 2023 | 2.004 | 1.738 | S3h | 6.072 | S3j |
| STERLINGNG | 2024 | 2.036 | 1.549 | S3h | 9.047 | S3j |
| STERLINGNG | 2025 (prov.) | 2.436 | 1.964 | S3h | 12.039 | S3j |
| UBA | 2020 | 5.247 | 3.787 | S1 | 7.904 | S6 |
| UBA | 2021 | 3.482 | 2.240 | S1 | 5.258 | S3j |
| UBA | 2022 | 3.552 | 2.751 | S3b | 10.108 | S3j |
| UBA | 2023 | 5.566 | 2.831 | S1 | 20.638 | S3j |
| UBA | 2024 | 7.390 | 3.741 | S1 | 32.900 | S3j |
| UBA | 2025 (prov.) | 7.707 | 4.393 | S1 | 46.330 | S3j |
| UNITYBNK | 2020 | 0.260 | 0.253 | S3b | 0.886 | S5 |
| UNITYBNK | 2021 | 0.318 | 0.310 | S3b | 1.051 | S5 |
| UNITYBNK | 2022 | 0.282 | 0.273 | S3b | 1.000 | S5 |
| UNITYBNK | 2023 | 0.335 | 0.327 | S3b | 1.203 | S5 |
| WEMABANK | 2020 | 0.992 | 0.917 | S3b | 1.210 | S3g |
| WEMABANK | 2021 | 1.068 | 0.968 | S3b | 1.271 | S3j |
| WEMABANK | 2022 | 1.097 | 0.993 | S3b | 2.066 | S3j |
| WEMABANK | 2023 | 1.916 | 1.771 | S3h | 4.133 | S3j |
| WEMABANK | 2024 | 2.824 | 2.501 | S3h | 7.461 | S3j |
| WEMABANK | 2025 (prov.) | 3.870 | 3.453 | S3h | 12.349 | S3j |
| ZENITHBANK | 2020 | 6.747 | 6.082 | S3h | 9.211 | S3g |
| ZENITHBANK | 2021 | 6.901 | 6.284 | S3h | 9.726 | S3j |
| ZENITHBANK | 2022 | 5.315 | 4.661 | S3h | 17.252 | S3j |
| ZENITHBANK | 2023 | 7.364 | 5.442 | S3h | 36.779 | S3j |
| ZENITHBANK | 2024 | 12.254 | 6.803 | S3h | 90.594 | S3j |
| ZENITHBANK | 2025 (prov.) | 9.095 | 5.881 | S3h | 74.427 | S3j |

## Flags: sensitivities driven by oil refining or by water and waste

A bank-year is flagged when the change in financed emissions from lines targeted at oil refining (or at water, waste and sewerage), in either version, is at least half of the net change in absolute terms (`sensitivity_flags.csv`). Where opposing changes nearly cancel, the driver's change can exceed the net change many times; both are listed.

Oil refining (main intensity, t CO2e per million naira): 2020 0.000 (GDP N55.9 bn), 2021 16.199 (GDP N31.7 bn), 2022 49.310 (GDP N19.9 bn), 2023 66.323 (GDP N14.8 bn), 2024 82.935 (GDP N11.8 bn), 2025 82.935 (GDP N11.8 bn). The refining GDP falls to N11.8 billion in 2024.

- S3j (downstream to oil refining) is flagged in 52 bank-years; in every one the refining lines account for all of the change (share of change at least 100%). S3j sets the maximum of the totals in every year from 2021 and the maximum of 46 of the 70 bank-years. Banks and years:

| Bank | Years flagged (S3j, oil refining) |
|---|---|
| ACCESSCORP | 2021, 2022, 2023, 2024 |
| FCMB | 2021, 2022, 2023, 2024, 2025 |
| FIDELITYBK | 2021, 2022, 2023, 2024, 2025 |
| FIRSTHOLDCO | 2021, 2022, 2023, 2024, 2025 |
| GTCO | 2021, 2022, 2023, 2024, 2025 |
| JAIZBANK | 2021, 2022, 2023, 2024, 2025 |
| STERLINGNG | 2021, 2022, 2023, 2024, 2025 |
| UBA | 2021, 2022, 2023, 2024, 2025 |
| UNITYBNK | 2021, 2022, 2023 |
| WEMABANK | 2021, 2022, 2023, 2024, 2025 |
| ZENITHBANK | 2021, 2022, 2023, 2024, 2025 |

- Excluding S3j, the maximum of the totals is set by:

| Total | Year | Main | Max excluding S3j | Set by |
|---|---|---|---|---|
| all available banks | 2020 | 35.24 | 46.44 | S3i |
| all available banks | 2021 | 37.74 | 49.56 | S3i |
| all available banks | 2022 | 39.61 | 50.52 | S3g |
| all available banks | 2023 | 59.17 | 76.10 | S3g |
| all available banks | 2024 | 78.34 | 95.64 | S3g |
| all available banks | 2025 | 77.39 | 93.78 | S3g |
| all available banks | 2020-2024 | 250.10 | 317.61 | S3g |
| balanced panel | 2020 | 34.98 | 46.17 | S3i |
| balanced panel | 2021 | 37.42 | 49.24 | S3i |
| balanced panel | 2022 | 39.33 | 50.23 | S3g |
| balanced panel | 2023 | 58.84 | 75.77 | S3g |
| balanced panel | 2024 | 78.34 | 95.64 | S3g |
| balanced panel | 2025 | 77.39 | 93.78 | S3g |
| balanced panel | 2020-2024 | 248.91 | 316.40 | S3g |

Water, waste and sewerage (main intensity, t CO2e per million naira): 2020 79.456, 2021 70.417, 2022 69.851, 2023 63.479, 2024 48.871, 2025 48.871.

- Water-and-waste-driven changes:

| Sensitivity | Bank | Year | Driver | Net change (t CO2e) | Change from driver lines (t CO2e) |
|---|---|---|---|---|---|
| S4 | FCMB | 2023 | water and waste | -2,184 | 1,344 |
| S4 | WEMABANK | 2023 | water and waste | -104 | 6,082 |
| S6 | FCMB | 2025 | water and waste | 294,370 | -164,990 |
| S6 | UNITYBNK | 2021 | water and waste | 7,035 | -8,816 |
| S6 | WEMABANK | 2021 | water and waste | 31,320 | -24,990 |
| S6 | WEMABANK | 2022 | water and waste | -32,019 | -94,876 |
| S6 | WEMABANK | 2023 | water and waste | 72,911 | -99,000 |

No other sensitivity is flagged.

## Checks (`data/interim/estimation_checks.csv`)

| Check | Result | Detail |
|---|---|---|
| recompute_bank_year | pass | 70/70 bank-years identical within 1e-12 (separate function) |
| exposure_equals_phase1b_total | pass | 70/70 bank-years: expanded exposure equals the Phase 1b main-specification total (sample.csv); largest relative difference 1.6e-16 |
| every_included_bank_year_estimated | pass | 70 bank-years estimated; missing: [] |
| bank_year_sector_shares_sum_to_1 | pass | 70 bank-years; largest deviation 3.3e-16 |
| year_sector_shares_sum_to_1 | pass | 12 total-type years; largest deviation 2.2e-16 |
| no_negative_line_values | pass | 0 negative lines |

## Deviations and notes

1. Applicability of S1 and S2 follows the plan's wording ("for bank-years where a Nigerian-bank column is printed"; "for all bank-years where it is printed"). Where the main specification is already at that level or basis, the sensitivity equals main; where no such table is printed it is not applicable. In the sensitivity totals, non-applicable bank-years keep the main value so that totals cover the same bank-years.
2. S2 for Wema 2025: the printed Group carrying amount of "Administrative and support service activities" is clipped in the PDF and was left empty in Phase 1b; S2 for that bank-year omits that cell.
3. S3f affects only Access 2025, which is provisional, so it changes no period total.
4. S6 financed emissions are written to the committed sensitivities file. They are products of exposures and Climate Watch-based intensities; the raw Climate Watch values and the S6 intensities remain only in the git-ignored `data/raw/derived/` (Phase 2b).
5. 2025 is provisional (2024 intensities applied to 2025 exposures) and is excluded from the 2020-2024 totals; it is reported in its own column or row.
6. Reporting sectors for shares keep construction, manufacturing and non-oil mining separate although they share one intensity, and show the rule categories as their own rows.
7. The flag rule (half of the net change) is set in this phase; the plan asks for the flag but gives no threshold.
