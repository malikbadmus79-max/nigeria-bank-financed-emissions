# The emissions Nigerian banks don't report: estimating financed emissions of NGX-listed banks, 2020-2025

## Question

How large are the greenhouse-gas emissions financed through the loan books of the deposit-money banks and bank holding companies listed on the Nigerian Exchange (NGX), and how did they change between 2020 and 2025? Bank climate disclosures typically cover operational (Scope 1 and 2) emissions; the emissions of the borrowers a bank finances (Scope 3, category 15) are the subject of this project, and the extent to which the listed banks already disclose them is checked in Phase 0. The project estimates those financed emissions by combining the sector breakdown of loans and advances disclosed in each bank's audited annual report with sector emission intensities derived from Nigeria's national greenhouse-gas inventory and national accounts, following the attribution logic of the PCAF Global GHG Accounting and Reporting Standard where the data allow.

## Data sources (to be confirmed)

- Annual reports and audited financial statements of the listed banks, 2020-2025: credit-risk concentration notes (loans and advances by economic sector). Sources are the banks' investor-relations sites and the NGX document library.
- Bank sustainability reports and IFRS S1/S2 disclosures: Scope 1, 2 and 3 and any financed-emissions disclosures, used for comparison.
- Nigeria's First Biennial Transparency Report to the UNFCCC (December 2024): national inventory by IPCC sector, 2000-2022.
- National Bureau of Statistics (NBS): GDP by economic activity, rebased to 2019 prices.
- Climate Watch (World Resources Institute) historical emissions data for Nigeria.
- PCAF emission factor database (access restricted to PCAF signatories; availability to be confirmed).

Source URLs, file sizes and SHA-256 hashes are recorded in `data/interim/phase0_sources.csv`. Annual-report PDFs are copyrighted and large, so they are kept locally in `data/raw/` and are not tracked in git.

## Status

Phase 0: feasibility. See `docs/phase0_plan.md` and `docs/phase0_results.md`.

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

## Reproducing Phase 0

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
set PYTHONPATH=src
.venv\Scripts\python -m bank_emissions.phase0_check
.venv\Scripts\python -m bank_emissions.extraction_test
.venv\Scripts\python -m pytest
```

The check downloads roughly 80 PDFs into `data/raw/` and re-uses local copies on later runs.

## Note on tooling

The code in this repository is AI-assisted: it was written with Claude Code (Anthropic) and reviewed by the author. All figures reported in the documentation come from files in this repository or from cited sources that were opened during the work.
