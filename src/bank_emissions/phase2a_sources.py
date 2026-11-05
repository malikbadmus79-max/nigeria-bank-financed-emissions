"""Phase 2a, step 5 (and the 2025 GDP search of step 4): log the documents
opened in Phase 2a in data/interim/phase0_sources.csv.

Each document gets one row with its URL, local path, size, SHA-256, page
count, the pages or paragraphs used (column pages_used) and the licence or
copyright statement read in the document (column licence_note). Existing
rows are read and written back as text, unchanged. Rows are keyed on
(doc_type, symbol, url), so re-running replaces them.

    python -m bank_emissions.phase2a_sources
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import pandas as pd

from .phase1b_extract import INTERIM, ROOT

SOURCES = INTERIM / "phase0_sources.csv"

DOCS = [
    dict(doc_type="disclosure_standard", symbol="IFRS_S2", bank="IFRS Foundation (ISSB)", year="2023",
         source_used="ifrs.org",
         url="https://www.ifrs.org/content/dam/ifrs/publications/html-standards-issb/english/2023/issued/issbs2.html",
         local_path="data/raw/disclosure/IFRS_S2_2023_issued.html",
         pages_used="paragraphs 29(a)(i)(3) (Scope 3), 29(a)(vi) and B58-B63 (financed emissions; B62 commercial "
                    "banking: absolute gross financed emissions by Scope 1, 2 and 3, by industry (GICS 6-digit) and "
                    "asset class), C1 (effective for annual periods beginning on or after 1 January 2024), C4(b) "
                    "(first-year relief from Scope 3 including financed emissions). HTML: no page numbers",
         licence_note="'IFRS Sustainability Disclosure Standards can be used for free for personal non-commercial "
                      "use ... All other uses ... not permitted without a separate licence'; (c) IFRS Foundation "
                      "2023. Not redistributed (data/raw is not committed)",
         ir_note="Official HTML of the issued standard (June 2023). The ifrs.org PDF of the standard returned an HTML "
                 "registration page to a scripted request. A PDF copy published by Cambodia's Accounting and Auditing "
                 "Regulator (acar.gov.kh) was also saved as a cross-check, not as the cited source"),
    dict(doc_type="disclosure_standard", symbol="IFRS_S2_ACAR_COPY", bank="IFRS Foundation (ISSB), copy on acar.gov.kh",
         year="2023", source_used="acar.gov.kh",
         url="https://www.acar.gov.kh/Resources/Document/20230627040217_IFRS-S2-climate-related-disclosures.pdf",
         local_path="data/raw/disclosure/IFRS_S2_2023_issued_acar_copy.pdf",
         pages_used="not cited; kept as a cross-check of the ifrs.org HTML",
         licence_note="(c) IFRS Foundation", ir_note="third-party copy of the IFRS Foundation PDF"),
    dict(doc_type="disclosure_standard", symbol="IFRS_S2_AMEND_2025", bank="IFRS Foundation (ISSB)", year="2025",
         source_used="ifrs.org",
         url="https://www.ifrs.org/content/dam/ifrs/publications/amendments/english/2025/issb-2025-1-amendments-ifrs-s2.pdf",
         local_path="data/raw/disclosure/IFRS_S2_amendments_2025.pdf",
         pages_used="PDF pp. 5-6 (29(a)(vi)(2) amended; 29A-29C: Category 15 may be limited to financed emissions, "
                    "defined over loans, project finance, bonds, equity and undrawn commitments); pp. 9-10 (B62, "
                    "B62A: gross exposure for funded amounts is the carrying amount before the loss allowance; "
                    "industry classification chosen by the entity); p. 13 (C1A-C1B: amendments effective for annual "
                    "periods beginning on or after 1 January 2027)",
         licence_note="(c) IFRS Foundation", ir_note="Amendments to Greenhouse Gas Emissions Disclosures, December 2025"),
    dict(doc_type="regulator_roadmap", symbol="FRC_NIGERIA", bank="Financial Reporting Council of Nigeria", year="2026",
         source_used="frcnigeria.gov.ng",
         url="https://frcnigeria.gov.ng/wp-content/uploads/2026/03/Roadmap-Report-for-the-Adoption-of-IFRS-"
             "Sustainability-Disclosure-Standards-in-Nigeria-Amended-2026-.pdf",
         local_path="data/raw/disclosure/FRC_Nigeria_ISSB_roadmap_amended_2026.pdf",
         pages_used="PDF p. 19 (printed p. 16), section 6.1: phased adoption; Phase 1 early adopters (FY2023), "
                    "Phase 2 voluntary (periods beginning 1 January 2024 to periods ending 31 December 2027), "
                    "Phase 3 mandatory for all entities except government from periods beginning on or after "
                    "1 January 2028 (all PIEs 2028, SMEs 2030); PDF p. 20 (printed p. 17): summary of phases and "
                    "readiness test assessment; PDF p. 33 (printed p. 30): PIE definition, including listed "
                    "entities on any recognised exchange in Nigeria",
         licence_note="no licence statement read on the pages used",
         ir_note="Roadmap Report for the Adoption of IFRS Sustainability Disclosure Standards in Nigeria (Amended "
                 "2026), unveiled 23 February 2026. Downloaded with a resumable request after two broken transfers"),
    dict(doc_type="intensity_source_search", symbol="NBS_GDP_2025", bank="National Bureau of Statistics", year="2025",
         source_used="search", url="https://microdata.nigerianstat.gov.ng/index.php/catalog/147",
         local_path="",
         pages_used="",
         licence_note="",
         download_note="not located",
         ir_note="Search 2026-11-04/05 for NBS 2025 GDP by activity at current basic prices: not located. The Q4 "
                 "2025 GDP release (27 February 2026) is reported in the press (real growth 4.07%; nominal Q4 GDP "
                 "N122.81 trillion; 2025 real growth 3.87%), but no NBS document with 2025 activity-level GDP at "
                 "current basic prices was found; the NBS microdata catalog for the rebased series (catalog 147) "
                 "lists Q1-Q3 2025 reports only. Two nigerianstat.gov.ng/download links returned by the search were "
                 "opened and are not 2025 data (logged separately). Plan section 5 rule applies: 2025 uses the 2024 "
                 "intensity, labelled provisional"),
    dict(doc_type="intensity_source_search", symbol="NBS_DOWNLOAD_1241460", bank="National Bureau of Statistics",
         year="2023", source_used="nigerianstat.gov.ng", url="https://www.nigerianstat.gov.ng/download/1241460",
         local_path="data/raw/intensity/nbs_2025/nbs_download_1241460.pdf",
         pages_used="PDF pp. 3, 25 read to identify the document: GDP report Q4 2023 (2022 and 2023 quarters, "
                    "pre-rebasing series). Not used",
         licence_note="", ir_note="returned by a search for 2025 GDP; not 2025 data"),
    dict(doc_type="intensity_source_search", symbol="NBS_DOWNLOAD_1241549", bank="National Bureau of Statistics",
         year="2024", source_used="nigerianstat.gov.ng", url="https://www.nigerianstat.gov.ng/download/1241549",
         local_path="data/raw/intensity/nbs_2025/nbs_download_1241549.pdf",
         pages_used="PDF pp. 3, 25 read to identify the document: GDP report Q2 2024 (2023 quarters and Q1-Q2 "
                    "2024, pre-rebasing series). Not used",
         licence_note="", ir_note="returned by a search for 2025 GDP; not 2025 data"),
]


def _file_info(rel: str) -> dict:
    p = ROOT / rel
    if not rel or not p.is_file():
        return dict(local_path="", file_size_bytes="", sha256="", n_pages="")
    b = p.read_bytes()
    n = ""
    if b[:4] == b"%PDF":
        import pypdfium2

        n = str(len(pypdfium2.PdfDocument(str(p))))
    return dict(local_path=rel, file_size_bytes=str(len(b)), sha256=hashlib.sha256(b).hexdigest(), n_pages=n)


def log(docs: list[dict]) -> pd.DataFrame:
    s = pd.read_csv(SOURCES, dtype=str, keep_default_na=False)
    for col in ("pages_used", "licence_note"):
        if col not in s:
            s[col] = ""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for d in docs:
        row = {c: "" for c in s.columns}
        row.update({k: v for k, v in d.items() if k not in ("local_path", "download_note")})
        row.update(_file_info(d["local_path"]))
        if not row["local_path"]:
            row["download_attempts"] = "failed: " + d.get("download_note", "not obtained")
        else:
            row["download_attempts"] = "ok"
        row["checked_utc"] = now
        key = (s.doc_type == d["doc_type"]) & (s.symbol == d["symbol"]) & (s.url == d["url"])
        s = s[~key]
        s = pd.concat([s, pd.DataFrame([row])], ignore_index=True)
    s.to_csv(SOURCES, index=False)
    return s


def main() -> int:
    s = log(DOCS)
    new = s[s.doc_type.isin(["disclosure_standard", "regulator_roadmap", "intensity_source_search"])]
    print(new[["doc_type", "symbol", "local_path", "n_pages", "download_attempts"]].to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
