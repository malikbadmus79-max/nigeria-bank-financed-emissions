# data/raw

This folder holds downloaded source files. Everything here except this README is gitignored: annual-report PDFs are large and copyrighted, so they stay on the local machine.

The source log `data/interim/phase0_sources.csv` records, for each file, the URL it came from, the file size in bytes and its SHA-256 hash, so that the same files can be downloaded again and verified.

Subfolders created by `python -m bank_emissions.phase0_check`:

- `annual_reports/`: `<NGX symbol>_<year>_<ir|ngx>.pdf`, where `ir` is the bank's investor-relations site and `ngx` is the NGX document library.
- `sustainability/`: `<NGX symbol>_<year>_sustainability.pdf`.
- `intensity/`: national inventory, NBS GDP and PCAF documents, and Climate Watch API extracts (JSON).
- `ngx/`: dated snapshots of the NGX company directory (JSON).
