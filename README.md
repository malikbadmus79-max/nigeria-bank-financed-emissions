# The emissions Nigerian banks don't report: estimating financed emissions of NGX-listed banks, 2020-2025

## Question

How large are the greenhouse-gas emissions financed through the loan books of the deposit-money banks and bank holding companies listed on the Nigerian Exchange (NGX), and how did they change between 2020 and 2025? Bank climate disclosures typically cover operational (Scope 1 and 2) emissions; the emissions of the borrowers a bank finances (Scope 3, category 15) are the subject of this project, and the extent to which the listed banks already disclose them is checked in Phase 0. The project estimates those financed emissions by combining the sector breakdown of loans and advances disclosed in each bank's audited annual report with sector emission intensities derived from Nigeria's national greenhouse-gas inventory and national accounts, following the attribution logic of the PCAF Global GHG Accounting and Reporting Standard where the data allow.

## Data sources

- Annual reports and audited financial statements of the listed banks, 2020-2025: credit-risk concentration notes (loans and advances by economic sector). Sources are the banks' investor-relations sites and the NGX document library.
- Bank sustainability reports and IFRS S1/S2 disclosures: Scope 1, 2 and 3 and any financed-emissions disclosures, used for comparison.
- Nigeria's First Biennial Transparency Report to the UNFCCC (December 2024): national inventory by IPCC sector, 2000-2022.
- National Bureau of Statistics (NBS): GDP by economic activity, rebased to 2019 prices.
- Climate Watch (World Resources Institute) historical emissions data for Nigeria.
- PCAF emission factor database: access restricted to PCAF signatories and accredited partners; not used.
- IFRS S2 (ifrs.org) and the FRC Nigeria roadmap for adopting IFRS sustainability standards (amended 2026), for the disclosure comparison.

Source URLs, file sizes and SHA-256 hashes are recorded in `data/interim/phase0_sources.csv`. Annual-report PDFs are copyrighted and large, so they are kept locally in `data/raw/` and are not tracked in git.

## Status and results

Phases 0-4 are complete (plan: `docs/analysis_plan.md`; full results: `docs/results.md`; method, checks and deviations by phase: `docs/phase*_results.md`).

- 12 banks, 70 bank-years, 2020-2025 (Ecobank Transnational excluded; Unity Bank 2020-2023). Sector loans are read from audited credit-concentration notes and multiplied by sector intensities (national inventory emissions / sector value added).
- Estimated financed emissions, main specification, balanced panel of 11 banks: 34.98 Mt CO2e (2020) to 78.34 Mt CO2e (2024); 248.9 Mt CO2e over 2020-2024. 2025 is provisional (77.39 Mt CO2e).
- After 2022 sector emissions are held at their 2022 level, so the rise in 2023-2024 reflects loan values (including currency effects) and nominal GDP, not measured physical emissions.
- Two banks publish a financed-emissions figure in the documents opened (Fidelity, UBA); against the published Category 15 or Scope 1&2 figures the estimates are 1.25 (UBA 2023, bank level) to 15.1 (Fidelity 2023) times larger; methods, scopes and coverage differ (RQ3 in `docs/results.md`).
- The estimates are sector-average approximations, not PCAF calculations; see "What the study cannot claim" in `docs/results.md`.

## Layout

```
data/raw/          downloaded source files (gitignored except README.md)
data/interim/      source log and intermediate extracts
data/processed/    analysis-ready tables
docs/              plans and results
figures/           charts
notebooks/         exploratory notebooks
src/bank_emissions source code
tests/             pytest tests
```

## Reproducing

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
set PYTHONPATH=src
.venv\Scripts\python -m bank_emissions.phase0_check          # downloads source PDFs into data/raw/ (about 80 files)
.venv\Scripts\python -m bank_emissions.phase1b_extract       # sector tables -> loans_by_sector.csv
.venv\Scripts\python -m bank_emissions.phase1b_build         # decisions, Jaiz 2024 OCR, exposures_by_sector.csv, sample.csv
.venv\Scripts\python -m bank_emissions.phase2a_btr1          # BTR1 / NID emissions (includes OCR of one image block)
.venv\Scripts\python -m bank_emissions.phase2a_nbs           # NBS GDP by activity
.venv\Scripts\python -m bank_emissions.phase2a_crosswalk     # signed-off crosswalk and splits
.venv\Scripts\python -m bank_emissions.phase2a_sector_map    # signed-off sector map
.venv\Scripts\python -m bank_emissions.phase2b_intensity     # sector intensities (S6 written to data/raw/derived/)
.venv\Scripts\python -m bank_emissions.phase3_estimate       # financed emissions and sensitivities
.venv\Scripts\python -m bank_emissions.phase4_compare        # comparison, decomposition, constant naira, national share
.venv\Scripts\python -m bank_emissions.phase4_disclosure     # disclosure table
.venv\Scripts\python -m bank_emissions.phase4_figures        # figures/
.venv\Scripts\python -m bank_emissions.phase4_report         # docs/results.md
.venv\Scripts\python -m pytest
```

OCR steps need the Tesseract binary (5.x) on PATH or at `C:\Program Files\Tesseract-OCR	esseract.exe`. The source PDFs, the Climate Watch API files and the S6 outputs stay in `data/raw/` (not tracked: copyright and an unconfirmed licence); their URLs and SHA-256 hashes are in `data/interim/phase0_sources.csv`. Tests check that each phase leaves the outputs of earlier phases unchanged (`data/interim/phase*_outputs_manifest.json`).

## Note on tooling

The code in this repository is AI-assisted: it was written with Claude Code (Anthropic) and reviewed by the author. All figures reported in the documentation come from files in this repository or from cited sources that were opened during the work.
