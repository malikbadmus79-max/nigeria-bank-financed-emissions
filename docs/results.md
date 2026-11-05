# Results: financed emissions of NGX-listed banks, 2020-2025

Date: 2026-11-05. This document reports the results for research questions RQ1-RQ4 of `docs/analysis_plan.md`. Method details, checks and deviations by phase are in `docs/phase1b_results.md`, `docs/phase2a_results.md`, `docs/phase2b_results.md` and `docs/phase3_results.md`. All tables below are generated from the processed CSV files by `python -m bank_emissions.phase4_report`.

## What is estimated

Financed emissions are estimated as each bank's loans and advances to customers by sector (audited credit-concentration notes, 2020-2025) multiplied by a sector emission intensity: Nigeria's national inventory emissions of the sector (BTR1 and its National Inventory Document, 2020-2022) divided by the sector's gross value added at current basic prices (NBS). For 2023-2024, emissions are held at 2022 and divided by each year's value added (Option A, plan section 5). 2025 uses the 2024 intensities, is labelled provisional and is kept out of period totals and trends. The estimate is a sector-average approximation of the direct emissions associated with each bank's loan mix, comparable in kind to PCAF data-quality score 5 but without PCAF's attribution factor.

Sample: 12 banks (Ecobank Transnational excluded; Unity Bank 2020-2023 only), 70 bank-years. Main specification: group level where printed, gross loans where printed, else carrying amount (GTCO, UBA and First HoldCo 2020-2021 are on a carrying basis; Fidelity 2020-2022 is at bank level; plan section 3 and recorded deviations). The balanced panel is the 11 banks present in every year (all except Unity Bank).

## RQ1: financed emissions by bank and year

| Total | Year | Banks | Loans (naira trillion) | Financed emissions (Mt CO2e) |
|---|---|---|---|---|
| all available banks | 2020 | 12 | 16.91 | 35.24 |
| all available banks | 2021 | 12 | 20.53 | 37.74 |
| all available banks | 2022 | 12 | 24.70 | 39.61 |
| all available banks | 2023 | 12 | 39.19 | 59.17 |
| all available banks | 2024 | 11 | 54.27 | 78.34 |
| all available banks | 2025 (provisional) | 11 | 57.17 | 77.39 |
| all available banks | 2020-2024 | 12 | 155.59 | 250.10 |
| balanced panel | 2020 | 11 | 16.71 | 34.98 |
| balanced panel | 2021 | 11 | 20.26 | 37.42 |
| balanced panel | 2022 | 11 | 24.41 | 39.33 |
| balanced panel | 2023 | 11 | 38.82 | 58.84 |
| balanced panel | 2024 | 11 | 54.27 | 78.34 |
| balanced panel | 2025 (provisional) | 11 | 57.17 | 77.39 |
| balanced panel | 2020-2024 | 11 | 154.46 | 248.91 |

From 2024 the two total types coincide (Unity Bank has no 2024-2025 figures).

Main specification by bank, Mt CO2e:

| Bank | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 (prov.) |
|---|---|---|---|---|---|---|
| ACCESSCORP | 5.51 | 7.82 | 9.95 | 17.25 | 19.81 | 19.54 |
| FCMB | 1.45 | 1.20 | 1.39 | 1.42 | 2.27 | 2.15 |
| FIDELITYBK | 6.76 | 8.22 | 8.34 | 10.29 | 14.37 | 14.41 |
| FIRSTHOLDCO | 4.58 | 4.15 | 4.75 | 7.66 | 11.41 | 11.65 |
| GTCO | 1.33 | 1.44 | 1.32 | 1.89 | 2.23 | 2.42 |
| JAIZBANK | 0.07 | 0.14 | 0.16 | 0.33 | 0.35 | 0.61 |
| STANBIC | 1.02 | 1.56 | 1.84 | 3.14 | 3.40 | 3.50 |
| STERLINGNG | 1.27 | 1.43 | 1.62 | 2.00 | 2.04 | 2.44 |
| UBA | 5.25 | 3.48 | 3.55 | 5.57 | 7.39 | 7.71 |
| UNITYBNK | 0.26 | 0.32 | 0.28 | 0.34 |  |  |
| WEMABANK | 0.99 | 1.07 | 1.10 | 1.92 | 2.82 | 3.87 |
| ZENITHBANK | 6.75 | 6.90 | 5.31 | 7.36 | 12.25 | 9.09 |

Share of national emissions (BTR1 total without LULUCF), 2020-2022:

| Total | Year | Financed emissions (Mt) | National total without LULUCF (Mt) | Share |
|---|---|---|---|---|
| all available banks | 2020 | 35.24 | 310.75 | 11.3% |
| all available banks | 2021 | 37.74 | 321.58 | 11.7% |
| all available banks | 2022 | 39.61 | 328.50 | 12.1% |
| balanced panel | 2020 | 34.98 | 310.75 | 11.3% |
| balanced panel | 2021 | 37.42 | 321.58 | 11.6% |
| balanced panel | 2022 | 39.33 | 328.50 | 12.0% |

The share compares financed emissions, which apply national sector intensities to bank loans, with the national inventory total; it is a scale reference, not a share of emissions that the banks cause.

### Change 2022-2024

The rise in estimated financed emissions from 2023 onwards reflects the growth of loan values in naira, including the naira value of foreign-currency loans and of loans booked by subsidiaries outside Nigeria, set against each year's nominal GDP. It does not reflect measured physical emissions: sector emissions after 2022 are held at their 2022 level (Option A), so the intensity of every sector falls as nominal value added rises, and every change after 2022 comes from loan values and GDP.

Decomposition, Mt CO2e. Method: a counterfactual 2024 is formed in which undivided "Oil and gas" loans are split into upstream, downstream and services with the 2022 split shares (Access/FCMB averages) instead of the 2024 shares. The change from 2022 to that counterfactual is decomposed by additive LMDI-I over intensity groups into loan volume (change in total loans), printed sector mix (change in the shares of the banks' printed categories) and intensity (change in sector intensity, which under Option A is the change in nominal value added). The oil-and-gas split-share effect is actual 2024 minus the counterfactual, i.e. the effect of the year-varying split shares at 2024 loans and intensities. The four effects sum to the change; the residual is zero to rounding in every row.

| Bank | 2022 (Mt) | 2024 (Mt) | Change (Mt) | Loan volume | Printed sector mix | Oil and gas split shares | Intensity | (info) O&G split shares at 2022 values | Loans 2022 (naira tn) | Loans 2024 (naira tn) |
|---|---|---|---|---|---|---|---|---|---|---|
| ACCESSCORP | 9.95 | 19.81 | 9.87 | 11.52 | 0.84 | 0.00 | -2.49 | 0.00 | 5.20 | 11.77 |
| FCMB | 1.39 | 2.27 | 0.88 | 1.16 | 0.26 | 0.00 | -0.54 | 0.00 | 1.25 | 2.49 |
| FIDELITYBK | 8.34 | 14.37 | 6.03 | 7.64 | 0.96 | 1.50 | -4.08 | 0.52 | 2.20 | 4.58 |
| FIRSTHOLDCO | 4.75 | 11.41 | 6.66 | 5.64 | 0.84 | 2.51 | -2.34 | 1.12 | 3.93 | 9.26 |
| GTCO | 1.32 | 2.23 | 0.91 | 0.54 | -0.04 | 0.78 | -0.37 | 0.64 | 1.89 | 2.79 |
| JAIZBANK | 0.16 | 0.35 | 0.19 | 0.15 | 0.09 | 0.03 | -0.08 | 0.02 | 0.15 | 0.29 |
| STANBIC | 1.84 | 3.40 | 1.56 | 1.74 | 0.51 | 0.00 | -0.70 | 0.00 | 1.24 | 2.47 |
| STERLINGNG | 1.62 | 2.04 | 0.42 | 0.69 | 0.08 | 0.28 | -0.62 | 0.15 | 0.76 | 1.14 |
| UBA | 3.55 | 7.39 | 3.84 | 4.01 | 0.54 | 1.00 | -1.71 | 0.47 | 3.14 | 7.25 |
| WEMABANK | 1.10 | 2.82 | 1.73 | 1.43 | 0.76 | 0.18 | -0.64 | 0.07 | 0.54 | 1.24 |
| ZENITHBANK | 5.31 | 12.25 | 6.94 | 6.84 | -0.61 | 3.09 | -2.38 | 0.85 | 4.12 | 10.99 |
| (balanced panel total) | 39.33 | 78.34 | 39.01 | 42.05 | 3.75 | 9.37 | -16.16 | 3.83 | 24.41 | 54.27 |

For the balanced panel the change of 39.01 Mt combines 42.05 Mt from loan volume, 3.75 Mt from printed sector mix, 9.37 Mt from the oil-and-gas split shares and -16.16 Mt from intensity. The split shares move from 21.2% upstream, 26.0% downstream and 52.8% services in 2022 to 48.9%, 23.0% and 28.1% in 2024 (`data/interim/oil_gas_split_shares.csv`), shifting undivided oil-and-gas loans from the services intensity to the upstream intensity; the effect is zero for Access and FCMB (which print the split themselves) and Stanbic (no undivided oil-and-gas label). The size of this effect depends on where it is evaluated: at 2022 loans and intensities it is 3.83 Mt (last column, for information; that ordering does not enter the sum). The combined categories (construction and real estate; information, telecoms and transport) are also split with year-varying NBS GDP shares; their effect, 0.03 Mt for the balanced panel, is left inside the printed-mix effect.

Loans and financed emissions in constant 2022 naira (implicit GDP deflator at basic prices, NBS rebasing annex pp. 7-8; recorded addition to the plan, descriptive):

| Total | Year | Deflator (2022 = 1) | Loans, nominal (naira tn) | Loans, constant 2022 naira (tn) | Financed emissions, main (Mt) | Constant-2022-naira loans x 2022 intensities (Mt) |
|---|---|---|---|---|---|---|
| all available banks | 2020 | 0.822 | 16.91 | 20.57 | 35.24 | 35.16 |
| all available banks | 2021 | 0.926 | 20.53 | 22.17 | 37.74 | 37.60 |
| all available banks | 2022 | 1.000 | 24.70 | 24.70 | 39.61 | 39.61 |
| all available banks | 2023 | 1.108 | 39.19 | 35.38 | 59.17 | 61.57 |
| all available banks | 2024 | 1.262 | 54.27 | 43.00 | 78.34 | 84.61 |
| balanced panel | 2020 | 0.822 | 16.71 | 20.32 | 34.98 | 34.90 |
| balanced panel | 2021 | 0.926 | 20.26 | 21.87 | 37.42 | 37.28 |
| balanced panel | 2022 | 1.000 | 24.41 | 24.41 | 39.33 | 39.33 |
| balanced panel | 2023 | 1.108 | 38.82 | 35.05 | 58.84 | 61.24 |
| balanced panel | 2024 | 1.262 | 54.27 | 43.00 | 78.34 | 84.61 |

The last column applies the 2022 intensities to loans in constant 2022 naira. Balanced panel: 39.33 Mt in 2022 and 84.61 Mt in 2024 on that basis, against 78.34 Mt in 2024 in the main specification. Loans in constant 2022 naira: 24.41 trillion (2022) and 43.00 trillion (2024). The aggregate deflator does not capture exchange-rate effects on foreign-currency loans or the different price movements of individual sectors.

## RQ2: sectors

Share of financed emissions by reporting sector, balanced panel (%), with the pooled 2020-2024 shares of loans and of financed emissions:

| Sector | Loan share 2020-2024 | Emissions share 2020-2024 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 (prov.) |
|---|---|---|---|---|---|---|---|---|
| Transport and storage | 3.2 | 40.1 | 36.6 | 49.7 | 42.0 | 42.5 | 34.5 | 37.0 |
| Power (electricity and gas supply) | 3.9 | 20.0 | 33.6 | 19.0 | 19.5 | 17.1 | 16.7 | 18.8 |
| Oil and gas, upstream | 10.0 | 19.1 | 13.8 | 12.6 | 12.5 | 18.2 | 28.6 | 23.5 |
| Manufacturing | 16.7 | 7.1 | 7.6 | 8.1 | 8.5 | 6.9 | 5.9 | 4.3 |
| Other (economy-wide average rule) | 7.3 | 5.0 | 3.5 | 5.1 | 5.7 | 5.3 | 4.9 | 8.3 |
| Oil refining | 0.1 | 3.6 | 0.0 | 0.5 | 5.9 | 4.9 | 4.4 | 1.9 |
| Agriculture, forestry and fishing | 4.1 | 2.5 | 2.4 | 2.6 | 2.8 | 2.6 | 2.5 | 3.4 |
| Construction | 3.2 | 1.4 | 1.8 | 1.7 | 1.4 | 1.3 | 1.1 | 1.3 |
| Services | 47.5 | 0.7 | 0.6 | 0.7 | 0.8 | 0.8 | 0.6 | 0.7 |
| Water, waste and sewerage | 0.0 | 0.4 | 0.2 | 0.1 | 0.6 | 0.4 | 0.6 | 0.7 |
| Mining and quarrying (non-oil) | 0.3 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 |
| Individuals and other zero-rule | 3.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Not a loan exposure | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

"Services" includes the lines placed in services by rule (general commerce, government, finance and insurance). "Other (economy-wide average rule)" includes "General", "Others" and the Access 2025 residual. Construction, manufacturing and non-oil mining share one intensity (the merged group). Within a sector every bank receives the same intensity, so differences between banks arise from loan mix and loan volume only. Figure: `figures/fig1_loan_vs_emission_share.png`.

## Sensitivities

Totals by specification, balanced panel, Mt CO2e (bank-years where a sensitivity does not apply keep the main value):

| Specification | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 (prov.) | 2020-2024 |
|---|---|---|---|---|---|---|---|
| main | 35.0 | 37.4 | 39.3 | 58.8 | 78.3 | 77.4 | 248.9 |
| S1 | 32.5 | 34.6 | 38.3 | 55.6 | 73.2 | 73.0 | 234.3 |
| S2 | 34.3 | 37.2 | 39.1 | 58.0 | 76.6 | 76.3 | 245.2 |
| S3a | 38.2 | 41.5 | 44.2 | 65.7 | 86.8 | 87.2 | 276.4 |
| S3b | 33.7 | 35.5 | 37.1 | 55.7 | 74.5 | 71.0 | 236.6 |
| S3c | 36.0 | 38.8 | 40.5 | 60.4 | 79.8 | 78.9 | 255.5 |
| S3d | 34.9 | 37.4 | 39.3 | 58.8 | 78.3 | 77.3 | 248.6 |
| S3e | 35.0 | 37.4 | 39.3 | 58.8 | 78.3 | 77.3 | 248.8 |
| S3f | 35.0 | 37.4 | 39.3 | 58.8 | 78.3 | 77.2 | 248.9 |
| S3g | 45.6 | 49.1 | 50.2 | 75.8 | 95.6 | 93.8 | 316.4 |
| S3h | 32.1 | 34.7 | 36.4 | 51.5 | 61.8 | 63.6 | 216.5 |
| S3i | 46.2 | 49.2 | 49.3 | 73.4 | 90.0 | 86.0 | 308.1 |
| S3j | 35.0 | 54.0 | 111.0 | 196.8 | 366.7 | 371.5 | 763.5 |
| S3k | 37.8 | 41.2 | 42.4 | 62.9 | 81.1 | 81.8 | 265.5 |
| S3l | 34.4 | 36.7 | 38.7 | 57.8 | 76.8 | 75.7 | 244.5 |
| S4 | 35.0 | 37.4 | 39.3 | 58.6 | 79.6 | 78.7 | 249.9 |
| S5 | 38.0 | 41.2 | 43.8 | 65.0 | 86.2 | 88.9 | 274.2 |
| S6 | 45.4 | 44.3 | 44.7 | 68.0 | 93.7 | 91.4 | 296.2 |

By bank, 2020-2024 totals, Mt CO2e (range over the sensitivities other than S3j; S3j shown separately):

| Bank | Main 2020-2024 (Mt) | Min excl. S3j | Set by | Max excl. S3j | Set by  | S3j |
|---|---|---|---|---|---|---|
| ACCESSCORP | 60.34 | 54.70 | S3b | 71.05 | S3i | 128.03 |
| FCMB | 7.73 | 7.66 | S3b | 11.03 | S3i | 38.80 |
| FIDELITYBK | 47.98 | 43.28 | S3h | 57.14 | S3g | 110.36 |
| FIRSTHOLDCO | 32.55 | 23.94 | S3h | 50.25 | S3g | 145.57 |
| GTCO | 8.22 | 4.30 | S3h | 23.34 | S3k | 53.86 |
| JAIZBANK | 1.05 | 0.94 | S3h | 1.60 | S5 | 2.55 |
| STANBIC | 10.97 | 6.52 | S3l | 14.03 | S6 | 10.97 |
| STERLINGNG | 8.35 | 7.17 | S3h | 11.15 | S3g | 22.15 |
| UBA | 25.24 | 15.66 | S1 | 34.03 | S3g | 74.15 |
| UNITYBNK | 1.20 | 1.16 | S3b | 4.14 | S5 | 1.23 |
| WEMABANK | 7.90 | 7.27 | S3h | 9.17 | S3g | 15.92 |
| ZENITHBANK | 38.58 | 29.27 | S3h | 56.24 | S3g | 161.09 |

Flags (reporting rule: the change from oil-refining, or water-and-waste, lines is at least half of the net change):

| sensitivity | driver | bank-years flagged |
|---|---|---|
| S3j | oil refining | 52 |
| S4 | water and waste | 2 |
| S6 | water and waste | 5 |

S3j (downstream lending treated as oil refining) is driven entirely by the oil-refining intensity, which rises to 82.9 t CO2e per million naira in 2024 as refining value added falls to N11.8 billion; S3j sets the maximum of the totals from 2021. Figure: `figures/fig3_estimate_ranges.png`.


### Post-results check: S7, transport intensity excluding passenger cars

**Added after the results (2026-11-05); not part of the fixed analysis plan.** The main transport intensity uses all of BTR1 category 1.A.3, which includes road transport (1.A.3.b) and, within it, passenger cars (1.A.3.b.i). S7 removes passenger-car emissions from the transport sector's emissions (they are then not attributed, like residential combustion); the transport value added and every other element are as in the main specification.

Does the National Inventory Document split road transport by vehicle type? Yes, in two places: Annex II, Table AII.1 (PDF pp. 202-203) prints emissions by vehicle type and gas (cars, light-duty trucks, heavy-duty trucks and buses, motorcycles) for the base year 2000 and for 2022 only; Table 3.32 (PDF pp. 82-84) prints fuel use by vehicle type for every year 2000-2022. The road-transport time series itself (Table 3.27, PDF p. 80) is not split.

Car emissions used: 2022 as printed in Table AII.1 (CO2 + CH4 + N2O), also applied to 2023-2024 under Option A; 2020 and 2021 rebuilt as the car share of road emissions from the Table 3.32 fuel use (CO2 per kt of gasoline and diesel fitted to the printed vehicle-type CO2 of 2000 and 2022) applied to the Table 3.27 road total. Car share of road emissions: 60.3% (2020), 59.8% (2021), 59.3% (2022, printed). IPCC category 1.A.3.b.i covers all passenger cars, privately and commercially used (including taxis).

| Year | 1.A.3 (kt) | Cars 1.A.3.b.i (kt) | Transport excl. cars (kt) | Intensity main (t per million naira) | Intensity S7 |
|---|---|---|---|---|---|
| 2020 | 52,009 | 30,583 | 21,427 | 23.978 | 9.879 |
| 2021 | 58,948 | 34,349 | 24,599 | 25.968 | 10.836 |
| 2022 | 59,045 | 33,784 | 25,261 | 23.673 | 10.128 |
| 2023 | 59,045 | 33,784 | 25,261 | 20.647 | 8.833 |
| 2024 | 59,045 | 33,784 | 25,261 | 15.616 | 6.681 |
| 2025 (prov.) | 59,045 | 33,784 | 25,261 | 15.616 | 6.681 |

| Total | Year | Main (Mt) | S7 (Mt) | Transport share, main | Transport share, S7 |
|---|---|---|---|---|---|
| all available banks | 2020 | 35.24 | 27.72 | 36.3% | 19.0% |
| all available banks | 2021 | 37.74 | 26.91 | 49.2% | 28.8% |
| all available banks | 2022 | 39.61 | 30.15 | 41.7% | 23.5% |
| all available banks | 2023 | 59.17 | 44.85 | 42.3% | 23.9% |
| all available banks | 2024 | 78.34 | 62.89 | 34.5% | 18.4% |
| all available banks | 2020-2024 | 250.10 | 192.53 | 40.0% | 22.0% |
| all available banks | 2025 (prov.) | 77.39 | 61.00 | 37.0% | 20.1% |
| balanced panel | 2020 | 34.98 | 27.46 | 36.6% | 19.2% |
| balanced panel | 2021 | 37.42 | 26.60 | 49.7% | 29.2% |
| balanced panel | 2022 | 39.33 | 29.87 | 42.0% | 23.7% |
| balanced panel | 2023 | 58.84 | 44.52 | 42.5% | 24.0% |
| balanced panel | 2024 | 78.34 | 62.89 | 34.5% | 18.4% |
| balanced panel | 2020-2024 | 248.91 | 191.33 | 40.1% | 22.1% |
| balanced panel | 2025 (prov.) | 77.39 | 61.00 | 37.0% | 20.1% |

Balanced panel, 2020-2024: 248.91 Mt in the main specification and 191.33 Mt under S7; the transport share of financed emissions is 40.1% and 22.1%.

Shares of financed emissions by reporting sector under S7, balanced panel, 2020-2024 pooled (`data/processed/postresults_s7_sector_shares.csv`):

| Reporting sector | Loan share | Emissions share, main | Emissions share, S7 |
|---|---|---|---|
| Power (electricity and gas supply) | 3.9% | 20.0% | 26.0% |
| Oil and gas, upstream | 10.0% | 19.1% | 24.9% |
| Transport and storage | 3.2% | 40.1% | 22.1% |
| Manufacturing | 16.7% | 7.1% | 9.3% |
| Other (economy-wide average rule) | 7.3% | 5.0% | 6.4% |
| Oil refining | 0.1% | 3.6% | 4.6% |
| Agriculture, forestry and fishing | 4.1% | 2.5% | 3.3% |
| Construction | 3.2% | 1.4% | 1.8% |
| Services | 47.5% | 0.7% | 0.9% |
| Water, waste and sewerage | 0.0% | 0.4% | 0.6% |
| Mining and quarrying (non-oil) | 0.3% | 0.1% | 0.1% |
| Individuals and other zero-rule | 3.8% | 0.0% | 0.0% |
| Not a loan exposure | 0.0% | 0.0% | 0.0% |

Transport, power and oil and gas upstream combined (balanced panel, 2020-2024 pooled; row "combined" in the file): 17.1% of loans; 79.2% of financed emissions under the main specification and 73.0% under S7.

S7 financed emissions as a share of national emissions without LULUCF (BTR1), 2020-2022 (`data/processed/postresults_s7_national_share.csv`):

| Total | Year | Main (Mt) | S7 (Mt) | National total without LULUCF (Mt) | Share, main | Share, S7 |
|---|---|---|---|---|---|---|
| all available banks | 2020 | 35.24 | 27.72 | 310.75 | 11.3% | 8.9% |
| all available banks | 2021 | 37.74 | 26.91 | 321.58 | 11.7% | 8.4% |
| all available banks | 2022 | 39.61 | 30.15 | 328.50 | 12.1% | 9.2% |
| balanced panel | 2020 | 34.98 | 27.46 | 310.75 | 11.3% | 8.8% |
| balanced panel | 2021 | 37.42 | 26.60 | 321.58 | 11.6% | 8.3% |
| balanced panel | 2022 | 39.33 | 29.87 | 328.50 | 12.0% | 9.1% |

Checks (`data/interim/postresults_s7_checks.csv`): fuel_factor_fit: pass; method_reproduces_printed_2022_shares: pass; printed_vehicle_sum_equals_table_3_27_2022: pass. Files: `data/processed/postresults_s7_road_split.csv`, `postresults_s7_intensity.csv`, `postresults_s7_results.csv`; code `src/bank_emissions/postresults_s7.py`. Earlier outputs are unchanged.

## RQ3: comparison with published financed emissions

Published figures as printed, with the estimate for the same bank and year. Ratios are estimate / published; nothing is adjusted to close the gaps. "Main x coverage" applies UBA's printed share of gross exposure included (90% in 2023, 52% in 2024).

| Bank | Year | Published item | Published (t CO2e) | Source | Estimate main (t) | Main / published | Bank level / published | Main x coverage / published |
|---|---|---|---|---|---|---|---|---|
| FIDELITYBK | 2023 | Scope 3 Category 15 financed emissions (gross total scopes 1 and 2) | 682,300 | FIDELITYBK_2023_sustainability.pdf p. 27 | 10,287,459 | 15.08 | 15.08 |  |
| FIDELITYBK | 2024 | Scope 3 Category 15 - Investments: Financed Emission | 4,606,362 | FIDELITYBK_2025_ir.pdf p. 99 | 14,368,761 | 3.12 | 3.12 |  |
| FIDELITYBK | 2025 | Scope 3 Category 15 - Investments: Financed Emission | 5,704,318 | FIDELITYBK_2025_ir.pdf p. 99 | 14,411,548 | 2.53 | 2.54 |  |
| FIDELITYBK | 2023 | (consistency) 2023 column of the FY2025 table | 682,300 | FIDELITYBK_2025_ir.pdf p. 99 | 10,287,459 | 15.08 | 15.08 |  |
| UBA | 2023 | Absolute gross financed emissions, Scope 1&2 (SASB table) | 2,258,646 | UBA_2024_sustainability.pdf p. 33 | 5,565,773 | 2.46 | 1.25 | 2.22 |
| UBA | 2023 | Absolute gross financed emissions, Scope 3 (SASB table) | 804,727 | UBA_2024_sustainability.pdf p. 33 | 5,565,773 | 6.92 | 3.52 | 6.22 |
| UBA | 2024 | Absolute gross financed emissions, Scope 1&2 (SASB table) | 602,146 | UBA_2024_sustainability.pdf p. 33 | 7,389,761 | 12.27 | 6.21 | 6.38 |
| UBA | 2024 | Absolute gross financed emissions, Scope 3 (SASB table) | 378,880 | UBA_2024_sustainability.pdf p. 33 | 7,389,761 | 19.50 | 9.87 | 10.14 |
| UBA | 2024 | Scope 1 + Scope 2 emissions, asset-class table total | 620,147 | UBA_2024_sustainability.pdf p. 37 | 7,389,761 | 11.92 | 6.03 | 6.20 |

| Bank | Year | Level (published) | Coverage (published) | Method (published) | Estimate level/basis |
|---|---|---|---|---|---|
| FIDELITYBK | 2023 | bank: boundary is Fidelity Bank's offices and channels across Nigeria, excluding subsidiaries outside Nigeria (same page) | not stated | not stated on this page (PCAF named on p. 30) | group/gross |
| FIDELITYBK | 2024 | bank (Fidelity Bank; operational boundary 'all bank locations across Nigeria', p. 100); financed-emissions boundary not stated | not stated | PCAF Global GHG Accounting and Reporting Standard (2020), p. 100 | group/gross |
| FIDELITYBK | 2025 | bank (Fidelity Bank; operational boundary 'all bank locations across Nigeria', p. 100); financed-emissions boundary not stated | not stated | PCAF Global GHG Accounting and Reporting Standard (2020), p. 100 | group/gross |
| UBA | 2023 | not stated; the same section (p. 32) describes UBA as operating in 24 countries | 90% of gross exposure (p. 33) | PCAF (p. 38) | group/carrying |
| UBA | 2024 | not stated; the same section (p. 32) describes UBA as operating in 24 countries | 52% of gross exposure (p. 33) | PCAF Standard and PCAF Database (p. 38); weighted data quality score 4.37 and 4.35 by asset class (p. 37, 2024) | group/carrying |

Known sources of divergence (plan section 8.5), none quantified here:
- Attribution: PCAF attributes a borrower's emissions in proportion to the loan's share of the borrower's equity and debt; the estimate attributes sector-average emissions per naira of value added to each naira lent.
- Emission factors: the estimate uses value added (smaller than revenue), which gives higher intensities than revenue-based factors; the published figures use borrower or proxy data (UBA weighted data quality scores 4.35-4.37).
- Scopes: the estimate covers the direct emissions of the borrowers' sectors (production-based, electricity emissions in the power sector only); UBA reports borrowers' Scope 1 and 2 and Scope 3 separately; Fidelity 2023 reports borrowers' Scopes 1 and 2.
- Coverage and level: UBA covers 90% and 52% of gross exposure; Fidelity's 2023 boundary excludes subsidiaries outside Nigeria; the estimate's main specification is at group level (Fidelity's 2023 Bank and Group tables differ only in consumer credit, which takes zero intensity, so the bank-level estimate equals the main one that year).
- Exposure basis: the UBA estimate is on carrying amounts (gross not printed by sector).
- UBA's 2024 report prints 2024 Scope 1&2 financed emissions as 602,146 tCO2e in the SASB table (p. 33) and 620,146.98 tCO2e in the asset-class table (p. 37); both are listed.
- The Fidelity 2025 estimate is provisional.

Figure: `figures/fig4_estimate_vs_published.png`.

## RQ4: disclosure

What the documents opened show (latest annual report in the source log, and the sustainability report where one was obtained). "Not found" means not found in those documents, not that the bank does not disclose the item elsewhere. Passages are recorded as printed in `data/processed/disclosure_table.csv`.

| bank | financed_emissions | green_finance | pcaf_method | scope_1 | scope_2 | scope_3 |
|---|---|---|---|---|---|---|
| ACCESSCORP | statement (ACCESSCORP_2025_ir p. 65) | figure (ACCESSCORP_2025_ir p. 59) | statement (ACCESSCORP_2025_ir p. 65) | figure (ACCESSCORP_2025_ir p. 66) | figure (ACCESSCORP_2025_ir p. 66) | figure (ACCESSCORP_2025_ir p. 66) |
| ZENITHBANK | statement (ZENITHBANK_2025_ngx p. 88) | not found | not found | figure (ZENITHBANK_2025_ngx p. 61) | figure (ZENITHBANK_2025_ngx p. 61) | statement (ZENITHBANK_2025_ngx p. 26) |
| GTCO | statement (GTCO_2025_ir p. 101) | not found | not found | not found | not found | statement (GTCO_2025_ir p. 101) |
| UBA | figure (UBA_2024_sustainability p. 33) | not found | figure (UBA_2024_sustainability p. 38) | chart only (UBA_2024_sustainability p. 36) | chart only (UBA_2024_sustainability p. 36) | chart only (UBA_2024_sustainability p. 36) |
| FIRSTHOLDCO | statement (FIRSTHOLDCO_2025_ir p. 104) | not found | statement (FIRSTHOLDCO_2025_ir p. 104) | figure (FIRSTHOLDCO_2025_ir p. 104) | figure (FIRSTHOLDCO_2025_ir p. 104) | not found |
| FIDELITYBK | figure (FIDELITYBK_2025_ir p. 99) | figure (FIDELITYBK_2025_ir p. 100) | figure (FIDELITYBK_2025_ir p. 100) | figure (FIDELITYBK_2025_ir p. 99) | figure (FIDELITYBK_2025_ir p. 99) | figure (FIDELITYBK_2025_ir p. 99) |
| FCMB | not found | not found | not found | not found | not found | not found |
| STANBIC | not found | not found | not found | not found | not found | not found |
| STERLINGNG | statement (STERLINGNG_2024_sustainability p. 29) | statement (STERLINGNG_2024_sustainability p. 9) | statement (STERLINGNG_2024_sustainability p. 29) | figure (STERLINGNG_2025_ir p. 38) | figure (STERLINGNG_2025_ir p. 38) | figure (STERLINGNG_2025_ir p. 38) |
| WEMABANK | other unit (WEMABANK_2025_ngx p. 61) | figure (WEMABANK_2025_ngx p. 58) | not found | other unit (WEMABANK_2025_ngx p. 61) | not found | not found |
| UNITYBNK | not found | not found | not found | not found | not found | not found |
| JAIZBANK | not found | not found | not found | not found | not found | not found |
| ETI | not found | not found | not found | not found | not found | not found |

IFRS S2 requirements for commercial banks (paragraph B62, official text; ifrs.org):
- B62(a): absolute gross financed emissions, disaggregated by Scope 1, Scope 2 and Scope 3, for each industry by asset class (industry by GICS 6-digit code in the 2023 text; the December 2025 amendments let the entity choose the classification, B62A);
- B62(b): gross exposure to each industry by asset class (funded carrying amounts before the loss allowance);
- B62(c): the percentage of gross exposure included in the calculation;
- B62(d): the methodology, including the method of attributing emissions to the size of the exposure.
IFRS S2 applies to annual periods beginning on or after 1 January 2024 (C1); in the first year an entity need not disclose Scope 3, including financed emissions (C4(b)); the 2025 amendments (29A-29C, effective 1 January 2027) allow Category 15 to be limited to financed emissions.

Against B62, for the two banks with a financed-emissions figure (pages read):

| requirement | FIDELITYBK | UBA |
|---|---|---|
| B62(a) absolute gross financed emissions by Scope 1, 2 and 3 | total Category 15 only (p. 99) | partly: Scope 1&2 combined and Scope 3 (p. 33) |
| B62(a) for each industry by asset class | not found on the pages read | yes, 2024: by industry and by asset class (p. 37) |
| B62(b) gross exposure by industry and asset class | not found on the pages read | covered loans only: 'Total Outstanding' by industry and asset class (p. 37) |
| B62(c) percentage of gross exposure included | not found on the pages read | yes: 90% (2023), 52% (2024) (p. 33) |
| B62(d) methodology, including attribution | PCAF Standard (2020) named (p. 100) | PCAF Standard named; asset classes listed (p. 38); attribution method not read on the pages opened |

The other ten banks show no financed-emissions figure in the documents opened.

FRC Nigeria roadmap (amended 2026, PDF p. 19): early adopters for periods ending on or before 31 December 2023; voluntary adoption for periods beginning 1 January 2024 to periods ending 31 December 2027; mandatory adoption for all public interest entities, which include entities listed on a recognised Nigerian exchange (PDF p. 33), for accounting periods beginning on or after 1 January 2028. Zenith Bank's 2025 report states that it applies the IFRS S2 Scope 3 transition relief and plans to report baseline financed emissions in Q1 2028. Figure: `figures/fig5_disclosure_grid.png`.

## Limitations

- Sector-average intensities: within a sector every bank receives the same intensity; the estimates are not attributions of identified borrowers' emissions.
- Value added rather than revenue: intensities per naira of value added are higher than revenue-based factors; the size of the difference is not estimated.
- Production-based allocation: electricity emissions sit in the power sector; borrowers' purchased-electricity (Scope 2) and value-chain (Scope 3) emissions are not attributed; residential fuel combustion (about 17% of national emissions) is not attributed to any sector.
- Emissions after 2022 are held at 2022 (BTR1 ends in 2022); changes in 2023-2025 come from loans and nominal GDP only. 2025 is provisional (NBS 2025 GDP by activity not located).
- Stocks against flows: year-end loan balances are compared with annual value added; group exposures include foreign-currency loans translated at closing rates and loans booked outside Nigeria, to which Nigerian intensities apply poorly (plan section 3 lists the banks with foreign operations).
- Exposure basis: GTCO and UBA are on carrying amounts, First HoldCo is on carrying amounts in 2020-2021, Fidelity is at bank level in 2020-2022, and Stanbic 2023 uses the following year's comparative.
- Sector labels: undivided "Oil and gas" is split by the shares printed by Access and FCMB; combined categories are split by GDP shares; several labels ("General", "Others") take the economy-wide average.
- The oil-refining intensity is very sensitive to the small and falling refining value added (S3j).
- Climate Watch values (S6) are not redistributed (licence not confirmed); S6 financed emissions are reported.
- Disclosure findings cover the documents opened; operational emissions charts without text values (UBA) are not read.

## What the study cannot claim

- That the estimates are any bank's actual financed emissions; they are sector-average approximations of the emissions associated with each bank's loan mix.
- That the estimates follow the PCAF Standard or meet the IFRS S2 measurement requirements.
- That a difference between an estimate and a published figure shows that either is wrong; the methods, coverage and scopes differ.
- That differences between banks reflect differences in borrower emission efficiency; they arise from sector mix and loan volume.
- That changes over 2023-2025 reflect changes in physical emissions; they reflect loan values (including currency effects) and nominal GDP.
- That loans booked by foreign subsidiaries carry Nigerian emission intensities.
- That borrowers' purchased-electricity (Scope 2) and value-chain (Scope 3) emissions are included.
- That emissions from loans to individuals, government or financial institutions are measured; they are set by rules, and the sensitivities show how much the totals depend on them.
- That the results cover the whole Nigerian banking system; the sample is the NGX-listed banks with sector notes, and only loans and advances to customers.
- That value-added-based intensities are comparable to revenue-based factors.
- That a bank which shows no disclosure in the documents opened discloses nothing elsewhere.

## Recorded additions and deviations

Recorded additions to the plan (dated in `docs/analysis_plan.md`): S3f (2026-11-04); crosswalk and sector-map sign-off with S3g-S3l (2026-11-05); sensitivity flag rule, 2022-2024 decomposition and constant-2022-naira series (2026-11-05). Deviations are listed in each phase results document: Fidelity level change, Wema units from the loans note, Stanbic 2023 comparative, Access 2025 residual row, the re-read method, merged manufacturing/construction/mining intensity, S5 economy-wide with LULUCF, S6 values kept out of the repository, and the identity check replacing the GDP-weighted-average check.
