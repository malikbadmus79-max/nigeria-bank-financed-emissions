# The emissions Nigerian banks don't report

Estimating the financed emissions of NGX-listed banks, 2020-2024, ahead of mandatory IFRS S2 reporting

Policy paper, November 2026. Malik Kolawole Badmus.

Data, code and full results: [github.com/malikbadmus79-max/nigeria-bank-financed-emissions](https://github.com/malikbadmus79-max/nigeria-bank-financed-emissions). Technical results: `docs/results.md`. Two-page summary: `docs/policy_brief.md`.

## Summary

From accounting periods beginning on or after 1 January 2028, every company listed on a recognised Nigerian exchange must report under the IFRS Sustainability Disclosure Standards (FRC Nigeria roadmap, amended 2026). For commercial banks, IFRS S2 requires the disclosure of financed emissions: the greenhouse-gas emissions of the borrowers and investees a bank finances, broken down by industry and asset class. For most banks these emissions are far larger than those of their own operations. In 2023, Fidelity Bank reported 18,977 tCO2e of Scope 1 and 2 emissions and 682,300 tCO2e of financed emissions, 36 times more.

This paper estimates the financed emissions of 12 banks listed on the Nigerian Exchange (NGX) for 2020-2025 using only public data. Each bank's audited loans and advances to customers by sector are multiplied by a sector emission intensity derived from Nigeria's national greenhouse-gas inventory and NBS national accounts. The estimates are sector averages, not any bank's actual financed emissions, and are comparable in kind to the lowest data-quality score in the Partnership for Carbon Accounting Financials (PCAF) Standard.

The main findings are:

1. Scale. The 12 banks' loan books are associated with an estimated 35 to 40 MtCO2e a year in 2020-2022, equal to 11-12% of Nigeria's national emissions excluding land use. If passenger-car fuel is removed from the transport sector, the estimate is 27 to 30 Mt (8-9%).
2. Concentration. About 17% of loans, to transport and storage, power and upstream oil and gas, account for 73-79% of estimated financed emissions. Services take 47.5% of loans and 0.7% of estimated emissions.
3. Variation between banks. In 2022 the estimated emissions per million naira of loans range from 0.70 t (GTCO) to 3.80 t (Fidelity), a more than fivefold difference driven by sector mix.
4. The 2024 rise is not new pollution. Estimated financed emissions roughly double between 2022 and 2024, from 39 to 78 Mt for the 11 banks present in every year. Loan growth in naira accounts for 42.0 Mt of the 39.0 Mt change, offset by falling sector intensities (-16.2 Mt). A further 9.4 Mt is a method effect from how undivided oil-and-gas loans are split.
5. Disclosure. In the documents reviewed, 2 of the 12 banks (Fidelity and UBA) publish a financed-emissions figure. Five publish a statement or plan without a figure, one reports a different measure, and four show nothing. Where a figure is published, the estimates are 2.5 to 15 times higher, which reflects differences in method, scope and coverage rather than an error on either side.

Six recommendations follow. Banks should start their baselines with the three high-intensity sectors, split "oil and gas" and combined categories in their credit-concentration notes, and publish boundary, coverage and method beside any figure. The Central Bank of Nigeria (CBN) and the Financial Reporting Council of Nigeria (FRC) should set a common sector classification for loan disclosures. The National Council on Climate Change should publish Nigerian sector emission factors and update the inventory beyond 2022. The Securities and Exchange Commission (SEC) and NGX should use the voluntary window to review draft disclosures before 2028.

## 1. Why financed emissions matter now

A bank's direct emissions come from its buildings, generators and vehicles (Scope 1) and the electricity it buys (Scope 2). Its largest climate exposure, however, sits in its loan book: the power plants, haulage fleets, oil fields and factories it finances. These financed emissions belong to Scope 3, Category 15 (investments) of the Greenhouse Gas Protocol.

Financed emissions matter for three reasons.

- Transition risk. Loans to high-emission sectors are exposed to carbon pricing, changes in demand and stranded assets. Financed emissions are the most direct indicator of that exposure.
- Comparability. Investors, development finance institutions and international correspondent banks increasingly ask for financed-emissions data. A bank that cannot provide it faces higher due-diligence costs and may lose access to some funding.
- Regulation. IFRS S2 makes the disclosure mandatory in Nigeria from 2028.

### 1.1 What IFRS S2 requires of banks

IFRS S2 (Climate-related Disclosures) applies to annual periods beginning on or after 1 January 2024 (paragraph C1). For commercial banks, paragraph B62 requires:

- B62(a): absolute gross financed emissions, disaggregated by Scope 1, Scope 2 and Scope 3, for each industry by asset class;
- B62(b): gross exposure to each industry by asset class (funded carrying amounts before the loss allowance);
- B62(c): the percentage of gross exposure included in the calculation;
- B62(d): the methodology, including how emissions are attributed to the size of the exposure.

In the first year of application an entity need not disclose Scope 3 emissions, including financed emissions (C4(b)). The December 2025 amendments, effective from 1 January 2027, allow banks to choose the industry classification (B62A) and to limit Category 15 to financed emissions (29A-29C).

### 1.2 The Nigerian timeline

The FRC roadmap (amended 2026, PDF p. 19) sets three stages: early adoption for periods ending on or before 31 December 2023; voluntary adoption for periods beginning 1 January 2024 to periods ending 31 December 2027; and mandatory adoption for all public interest entities, which include companies listed on a recognised Nigerian exchange (PDF p. 33), for periods beginning on or after 1 January 2028. With the first-year Scope 3 relief, a bank could defer financed emissions until its second mandatory year, but the data systems needed take years to build. Zenith Bank's 2025 annual report states that it applies the relief and plans to report baseline financed emissions in the first quarter of 2028.

### 1.3 How banks measure financed emissions

The PCAF Global GHG Accounting and Reporting Standard, which both Fidelity and UBA cite, attributes to a bank a share of each borrower's emissions in proportion to the bank's share of the borrower's financing. Where borrower data are missing, banks use sector-average emission factors per unit of revenue or assets. PCAF grades the result from data-quality score 1 (verified borrower emissions) to score 5 (sector averages applied to the amount lent). PCAF's emission-factor database is available only to signatories and accredited partners (PCAF database information sheet, September 2025), which raises the cost for banks that have not joined.

## 2. Data and method

### 2.1 Sample

The sample is the 12 deposit-money banks and bank holding companies listed on NGX with a sector breakdown of loans in their audited annual reports: Access Holdings, Zenith Bank, GTCO, UBA, First HoldCo, Fidelity Bank, FCMB Group, Stanbic IBTC Holdings, Sterling Financial Holdings, Wema Bank, Unity Bank and Jaiz Bank. Ecobank Transnational Incorporated is excluded because its NGX filings carry no sector note. Unity Bank is covered for 2020-2023 only; no audited statements after FY2023 were found. The result is 70 bank-years, 2020-2025.

### 2.2 Loans by sector

Each bank's credit-concentration note (loans and advances to customers by economic sector) was extracted from the PDF of its annual report by script, without manual typing. Every table was checked in two ways: the sector rows must sum to the printed total, and the total must reappear elsewhere in the same report, for example in the loans note or the statement of financial position. Eight tables (seven bank-years) in which the bank's own printed figures do not add up are kept as printed and flagged. The main specification uses group-level gross loans where printed and carrying amounts otherwise (GTCO, UBA, and First HoldCo in 2020-2021).

### 2.3 Sector emission intensities

Sector emissions come from Nigeria's First Biennial Transparency Report and National Inventory Document to the UNFCCC (December 2024), which cover 2000-2022. Sector output is gross value added at current basic prices from the NBS rebased national accounts (2019-2024). Dividing one by the other gives tonnes of CO2e per naira of output for each sector.

| Sector group | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| Transport and storage | 23.98 | 25.97 | 23.67 | 20.65 | 15.62 |
| Power (electricity and gas supply) | 15.30 | 8.99 | 9.28 | 6.82 | 6.01 |
| Oil and gas, upstream | 4.30 | 4.15 | 3.34 | 3.05 | 2.73 |
| Agriculture, forestry and fishing | 1.34 | 1.14 | 1.07 | 0.96 | 0.87 |
| Manufacturing, construction and non-oil mining | 0.95 | 0.89 | 0.71 | 0.62 | 0.55 |
| Services | 0.02 | 0.02 | 0.03 | 0.02 | 0.02 |
| Economy-wide average | 1.47 | 1.34 | 1.21 | 1.06 | 0.90 |

Table 1. Main sector intensities, tCO2e per million naira of value added. Oil refining and water and waste have very high intensities because their value added is small; together they carry 0.1% of loans. Source: `data/processed/sector_intensity.csv`.

The inventory ends in 2022. For 2023 and 2024, sector emissions are held at their 2022 level and divided by each year's value added. Intensities therefore fall after 2022 as nominal GDP rises, and changes in estimated financed emissions after 2022 come from loans and GDP only. 2025 uses the 2024 intensities and is treated as provisional.

### 2.4 Calculation and judgement calls

Financed emissions are loans to each sector multiplied by that sector's intensity, summed by bank and year. Several bank categories do not map to a single sector. The rules, fixed in writing before any estimate was computed, are:

- Undivided "oil and gas" loans, printed by nine banks as one line, are split into upstream, downstream and services using the shares printed by Access and FCMB in the same year. These shares move from 21.2% upstream in 2022 to 48.9% in 2024.
- Combined categories (construction and real estate; information, telecoms and transport) are split by the GDP shares of the two activities.
- "General" and "Others" take the economy-wide average intensity. Loans to individuals take zero. Commerce, government and finance take the services intensity.
- Oil-and-gas services and downstream lending are treated as services.

Every rule has at least one alternative, and each alternative was run as a sensitivity: 17 in total, plus one added after the results (Section 3.6).

## 3. Findings

### 3.1 Scale

| | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| Banks | 12 | 12 | 12 | 12 | 11 |
| Loans to customers (naira trillion) | 16.91 | 20.53 | 24.70 | 39.19 | 54.27 |
| Estimated financed emissions (MtCO2e) | 35.24 | 37.74 | 39.61 | 59.17 | 78.34 |
| National emissions excluding land use (Mt) | 310.75 | 321.58 | 328.50 | | |
| Share of national emissions | 11.3% | 11.7% | 12.1% | | |

Table 2. Main estimates, all banks in the sample. The national comparison is a scale reference, not a share of emissions the banks cause.

Over 2020-2024 the main estimate for the 11 banks present in every year totals 248.9 Mt.

### 3.2 Concentration in three sectors

| Sector | Share of loans | Share of estimated emissions | Share excluding passenger cars |
|---|---|---|---|
| Transport and storage | 3.2% | 40.1% | 22.1% |
| Power (electricity and gas supply) | 3.9% | 20.0% | 26.0% |
| Oil and gas, upstream | 10.0% | 19.1% | 24.9% |
| Three sectors combined | 17.1% | 79.2% | 73.0% |
| Manufacturing | 16.7% | 7.1% | |
| Services | 47.5% | 0.7% | |

Table 3. Pooled 2020-2024, 11 banks present every year. Source: `results.md`, `postresults_s7_sector_shares.csv`.

The concentration is the central policy finding. A bank does not need borrower-level data for its whole book to produce a credible first estimate: borrower data for its transport, power and upstream oil-and-gas clients, combined with sector averages for the rest, would cover most of its exposure.

### 3.3 Differences between banks

| Bank | Loans 2022 (naira tn) | Estimated emissions 2022 (Mt) | tCO2e per million naira of loans | Largest sector (share of the bank's estimated emissions) |
|---|---|---|---|---|
| Fidelity | 2.20 | 8.34 | 3.80 | Transport and storage (65%) |
| Sterling | 0.76 | 1.62 | 2.13 | Transport and storage (59%) |
| Wema | 0.54 | 1.10 | 2.03 | Transport and storage (52%) |
| Access | 5.20 | 9.95 | 1.91 | Transport and storage (46%) |
| Stanbic IBTC | 1.24 | 1.84 | 1.49 | Oil and gas, upstream (46%) |
| Zenith | 4.12 | 5.31 | 1.29 | Transport and storage (52%) |
| First HoldCo | 3.93 | 4.75 | 1.21 | Power (52%) |
| UBA | 3.14 | 3.55 | 1.13 | Power (41%) |
| FCMB | 1.25 | 1.39 | 1.11 | Power (38%) |
| Jaiz | 0.15 | 0.16 | 1.05 | Transport and storage (46%) |
| Unity | 0.29 | 0.28 | 0.96 | Agriculture, forestry and fishing (93%) |
| GTCO | 1.89 | 1.32 | 0.70 | Oil and gas, upstream (37%) |

Table 4. 2022, main specification. Source: `bank_intensity_2022.csv`.

Over 2020-2024 the largest estimates are for Access (60.3 Mt), Fidelity (48.0 Mt) and Zenith (38.6 Mt). Because every bank receives the same intensity within a sector, these differences come entirely from loan size and sector mix, not from how clean any bank's borrowers are. Where transport lending makes up most of a bank's estimate, as at Fidelity, Sterling, Zenith and Wema, the estimate depends heavily on how transport emissions are measured (Section 3.6).

### 3.4 The 2022-2024 rise

| Component | MtCO2e |
|---|---|
| 2022 estimate | 39.33 |
| Loan volume (growth in naira) | +42.05 |
| Printed sector mix | +3.75 |
| Oil and gas split shares (method effect) | +9.37 |
| Sector intensity | -16.16 |
| 2024 estimate | 78.34 |

Table 5. Decomposition of the change, 11 banks present every year (additive LMDI with a counterfactual for the split shares). Source: `change_decomposition_2022_2024.csv`.

The rise reflects the naira value of loans, which grew from ₦24.4 trillion to ₦54.3 trillion for these banks (₦43.0 trillion in constant 2022 naira). Group loan books include foreign-currency loans translated at year-end exchange rates and loans booked by subsidiaries abroad, both of which grow in naira terms when the currency weakens. Because sector emissions after 2022 are held at 2022, the estimate cannot show whether physical emissions rose or fell. The split-share effect is 9.37 Mt at 2024 values and 3.83 Mt at 2022 values. Either way, part of the rise comes from how two banks happen to classify their oil-and-gas lending.

The practical lesson for disclosure is that financed emissions measured against naira exposures will move with the exchange rate. Banks should report intensity measures alongside absolute figures and explain currency effects when they publish year-on-year changes.

### 3.5 Comparison with published figures

| Bank and year | Published (tCO2e) | Estimate (tCO2e) | Estimate ÷ published |
|---|---|---|---|
| Fidelity 2023, Category 15 | 682,300 | 10,287,459 | 15.1 |
| Fidelity 2024, Category 15 | 4,606,362 | 14,368,761 | 3.1 |
| Fidelity 2025, Category 15 (estimate provisional) | 5,704,318 | 14,411,548 | 2.5 |
| UBA 2023, borrowers' Scope 1 and 2 | 2,258,646 | 5,565,773 | 2.5 (1.3 at bank level) |
| UBA 2024, borrowers' Scope 1 and 2 | 602,146 | 7,389,761 | 12.3 |

Table 6. Sources: Fidelity 2023 Sustainability Report p. 27 and 2025 Annual Report p. 99; UBA 2024 Sustainability Report p. 33. UBA's 2024 report also prints 620,146.98 tCO2e for the same item on p. 37.

The gaps have identifiable causes, none of which is resolved here. The estimate attributes sector-average emissions to every naira lent, while PCAF attributes a share of each borrower's emissions in proportion to its total financing. Value added is smaller than revenue, so value-added intensities are higher than the revenue-based factors banks use. UBA's figures cover 90% (2023) and 52% (2024) of its gross exposure. Fidelity's 2023 boundary excludes its subsidiaries outside Nigeria. Fidelity's own figure rises nearly sevenfold between 2023 and 2024, which suggests a change in method or coverage that the report does not explain on the pages reviewed.

The comparison shows that published figures from different banks, and from the same bank in different years, are not yet comparable. That is a problem for investors and supervisors regardless of which number is closer to the truth.

### 3.6 How robust are the findings?

| Specification | 2020-2024 total (Mt), 11 banks |
|---|---|
| Main | 248.9 |
| Lowest pre-specified alternative (undivided oil and gas all downstream) | 216.5 |
| Highest pre-specified alternative excluding refining (undivided oil and gas all upstream) | 316.4 |
| Passenger cars excluded from transport (added after the results) | 191.3 |
| Downstream lending treated as oil refining | 763.5 |

Table 7. Selected sensitivities. Full table in `results.md`.

Apart from the refining case, the pre-specified alternatives range from 13% below to 27% above the main estimate, with the treatment of undivided oil-and-gas loans setting both ends. Two further cases need explanation. Treating downstream lending as refining multiplies the total because Nigeria's refining value added was close to zero (₦11.8 billion in 2024), which makes the refining intensity extreme; it is reported separately and not used for conclusions. Excluding passenger cars matters because cars are about 60% of road-transport emissions in the inventory, and transport carries the largest share of estimated financed emissions. The inventory does not separate private from commercial cars, so the truth for transport lending lies between the two figures. The central finding holds outside the refining case: under the other 16 pre-specified alternatives the three sectors carry 71-84% of estimated emissions, and 73% without passenger cars. Only the refining case, set aside above, breaks the pattern.

## 4. Disclosure readiness

| Disclosure of financed emissions in the documents reviewed | Banks |
|---|---|
| Figure published | Fidelity, UBA |
| Statement or plan, no figure | Access, Zenith, GTCO, First HoldCo, Sterling |
| Different measure (share of loans to impact sectors) | Wema |
| Nothing found | FCMB, Stanbic IBTC, Unity, Jaiz |

Table 8. Documents reviewed: each bank's latest annual report and, where obtained, its sustainability report. A bank may disclose elsewhere.

Against IFRS S2 B62, UBA comes closest: it reports borrowers' Scope 1 and 2 and Scope 3 separately, by industry and asset class for 2024, with the share of exposure covered and PCAF named as its method. Fidelity reports a Category 15 total and names the PCAF Standard, but the pages reviewed show no breakdown by industry, no gross exposure and no coverage share. Five banks publish Scope 1 and 2 figures for their own operations and UBA shows them in a chart, which shows that reporting systems exist; the gap is in the loan book.

Two features of current loan disclosures make the transition harder than it needs to be. First, nine of the 12 banks print oil and gas as a single line, although upstream, downstream and services lending carry very different emissions. Second, categories differ from bank to bank ("General", "Others", combined construction and real estate), so sector exposures cannot be compared without judgement calls.

## 5. Recommendations

### For banks

1. Build the baseline from the top down. Start with borrower-level data for transport, power and upstream oil-and-gas clients, which hold under one-fifth of loans and 73-79% of estimated emissions, and use sector averages for the rest. This follows PCAF's approach of improving data quality over time and puts effort where it matters most. Timing: during the 2026-2027 voluntary window.
2. Split "oil and gas" and combined categories in the credit-concentration note. Reporting upstream, downstream and services separately, and real estate apart from construction, costs little, partly meets IFRS S2 B62(b) and removes the largest source of uncertainty in outside estimates. Timing: FY2026 annual reports.
3. Publish boundary, coverage and method beside every figure. A financed-emissions number without its scope, coverage share and method cannot be compared across banks or years. Large changes, including those caused by exchange rates, should be explained. Timing: immediately, for banks already publishing.

### For regulators and public bodies

4. CBN and FRC: a common sector classification for loan disclosures. A shared list of sectors for credit-concentration notes, aligned with emission-relevant activities and with the classification banks will use under IFRS S2, would make exposures comparable before 2028.
5. National Council on Climate Change: Nigerian emission factors and a current inventory. Sector emission factors per naira of output, derived from the national inventory and published openly, would give smaller banks a Nigerian alternative to restricted international databases. Updating the inventory beyond 2022 would let banks and analysts track change rather than hold emissions constant.
6. SEC and NGX: a readiness review. Collecting draft financed-emissions disclosures during the voluntary window and publishing an anonymised review of common gaps would help banks meet the 2028 requirement consistently.

## 6. Limitations

- The estimates are sector averages, not any bank's actual financed emissions, and do not follow the PCAF Standard's attribution method.
- Value-added intensities are higher than revenue-based factors; the size of the difference is not estimated.
- Emissions are allocated by producing sector: electricity emissions sit in power, and borrowers' purchased electricity and value-chain emissions are not counted. Residential fuel use (about 17% of national emissions) is not attributed to any sector.
- Sector emissions after 2022 are held at their 2022 level; 2025 is provisional.
- Year-end loan balances are compared with annual value added. Group loans include foreign-currency loans and loans booked abroad, to which Nigerian intensities apply imperfectly.
- GTCO and UBA are on carrying amounts; Fidelity is at bank level in 2020-2022; Stanbic 2023 uses the following year's comparative.
- Disclosure findings cover the documents reviewed.

## 7. Further research

- Borrower-level estimates for the largest transport, power and upstream exposures, using company reports where available, to test the sector averages.
- Revenue-based intensities from NBS or company data, to compare with the value-added approach and with PCAF factors.
- Splitting road transport between private and commercial use, which would narrow the widest remaining uncertainty.
- Extending the series once Nigeria's next inventory is published.

## References

- Bank annual reports and audited financial statements, 2020-2025, and sustainability reports where available: Access Holdings, Zenith Bank, GTCO, UBA, First HoldCo, Fidelity Bank, FCMB Group, Stanbic IBTC Holdings, Sterling Financial Holdings, Wema Bank, Unity Bank, Jaiz Bank. URLs, file sizes and SHA-256 hashes in `data/interim/phase0_sources.csv`.
- Federal Republic of Nigeria (2024). First Biennial Transparency Report and National Inventory Document. UNFCCC.
- National Bureau of Statistics. Rebasing of Gross Domestic Product: Key Highlights (rebased series, 2019-2024).
- IFRS Foundation (2023). IFRS S2 Climate-related Disclosures; Amendments to IFRS S2 (December 2025).
- Financial Reporting Council of Nigeria (2026). Roadmap Report for the Adoption of IFRS Sustainability Disclosure Standards in Nigeria (amended).
- Partnership for Carbon Accounting Financials. The Global GHG Accounting and Reporting Standard for the Financial Industry; PCAF Database information sheet (September 2025).

Every figure in this paper is generated from, or can be traced to, the files in the repository. The analysis plan was committed before any estimate was computed; deviations are recorded in each phase's results document, and the checks added after the results, including the passenger-car case, are labelled as such in `docs/results.md`.
