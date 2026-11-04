# Phase 0 plan: feasibility checks

## Purpose

Phase 0 establishes whether the data needed to estimate financed emissions of NGX-listed banks for 2020-2025 exist, can be obtained legally and reproducibly, and can be extracted from the source documents with acceptable effort. It does not produce estimates or interpret findings.

## Checks

### a. Bank list

- Retrieve the NGX company directory (the JSON endpoint used by ngxgroup.com) and confirm each candidate issuer: Access Holdings, Zenith Bank, GTCO, UBA, First HoldCo (formerly FBN Holdings), Fidelity Bank, FCMB Group, Stanbic IBTC Holdings, Sterling Financial Holdings, Wema Bank, Unity Bank, Jaiz Bank, Ecobank Transnational Incorporated.
- Record the NGX symbol, sub-sector, board, listing date and nature of business, and list any other issuer in the NGX "Banking" sub-sector that is not on the candidate list.
- Record whether the listed entity is a holding company or the bank itself, and symbol changes in 2020-2025 (holding-company restructurings).
- Record non-Nigerian operations from subsidiary disclosures in the latest annual report.

### b. Annual reports, 2020-2025

- For each bank and year, locate the official PDF on the bank's investor-relations site. Where the site blocks scripted access or lists documents only through JavaScript, use the audited financial statements filed on the NGX document library and record the reason.
- Download into `data/raw/annual_reports/` only; record URL, size and SHA-256.
- Locate the credit-risk concentration note (loans and advances by economic sector) and record page, gross or net basis, group or bank level, and the sector categories used. Page location is automated (text-layer search); basis, level and categories are first recorded automatically and then checked by hand for a sample.
- Flag reports without a text layer (scanned pages).

### c. Sustainability reports

- For each bank, find the latest standalone sustainability report; also scan the 2025 annual report, since IFRS S1/S2 disclosures may sit there.
- Record whether Scope 1, Scope 2, Scope 3, financed emissions (PCAF or other method) and green or sustainable loan amounts are disclosed, with page numbers. Automated page search distinguishes a mention from a page that also carries an emissions unit or currency amount; a sample is checked by hand.

### d. Emission-intensity sources

- Nigeria's latest national GHG inventory submitted to the UNFCCC (BUR or BTR): years, sectors, sub-categories, access and licence.
- NBS GDP by economic activity for 2020-2025: years, activity classification, access.
- Climate Watch and other open datasets for Nigeria: sectors, years, licence.
- PCAF emission factor database: cost, registration, coverage of Nigeria or proxies.

### e. Extraction test

- Choose two banks with clear, text-based sector tables for one year.
- Extract each table into `data/interim/extraction_test_<bank>_<year>.csv`.
- Check that the sum of sector rows equals the total in the same table, and compare that total with the loans-and-advances total reported elsewhere in the same report (statement of financial position or the loans note).
- Record difficulties: scanned pages, merged cells, tables split over pages, gross versus net columns.

## Outputs

- `src/bank_emissions/phase0_check.py` and helpers (`sources.py`, `ngx.py`, `fetch.py`, `pdfscan.py`, `extraction_test.py`, `phase0_report.py`).
- `data/interim/phase0_sources.csv`: one row per document checked.
- `docs/phase0_results.md`: results tables and a list of failures, without interpretation.

## Rules

- No figure is reported unless it comes from a file in the repository or a cited source opened during the check.
- Downloads are limited to the documents needed; PDFs stay in `data/raw/` and are not committed.
- If a site blocks downloads, this is recorded rather than worked around.
