Context for the items above:

- ETI 2020-2025: the NGX filings are 47-52-page condensed consolidated statements (primary statements in USD and NGN, selected notes, five-year summary) without a credit-concentration note. The ecobank.com annual-reports page lists documents through JavaScript with opaque upload identifiers and timed out on later requests. A full 2023 Group annual report appeared in search results on a share registrar's site (greenwichregistrars.com); it is not an official ETI or NGX source and was not opened.
- Unity Bank 2024-2025: the latest audited statements on NGX are for FY2023 (posted 2025-02-26). NGX filings include a CBN approval notice for the Unity Bank and Providus Bank merger (2024-08-07) and resolutions of a court-ordered meeting (2025-09-29). unitybankng.com failed TLS negotiation (SSL error), so the bank's own site could not be checked.
- Jaiz Bank 2024: the NGX filing (143 pages) has no text layer; the sector table would need OCR.
- First HoldCo 2021: the IR URL found on first-holdco.com returned HTTP 404 at download time; the NGX copy was used. First HoldCo's 2024 sustainability report link points to firstbanknigeria.com, which failed certificate verification; the 2025 annual report (IR) contains a sustainability section that was scanned instead.
- Stanbic IBTC 2023 sustainability report: the URL returned by search on reporting.stanbicibtc.com returned HTTP 404.
- Zenith, FCMB, Jaiz, ETI: no standalone sustainability report was located; their 2025 annual report or NGX audited filing was scanned instead. The NGX filings for UBA and ETI contain financial statements only.
- NGX API: the filings endpoint dropped connections or timed out on some requests during parallel runs; queries are now retried and cached per day in `data/raw/ngx/`.
- Emission-intensity gaps: Climate Watch licence not confirmed on an opened page; NBS 2025 GDP by activity not located; PCAF database access restricted to signatories and accredited partners.
