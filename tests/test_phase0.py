"""Offline tests for the Phase 0 helpers (no network, no PDFs needed)."""

from bank_emissions import ngx, pdfscan
from bank_emissions.extraction_test import _to_num, parse_text_table
from bank_emissions.sources import BANKS, IR_ANNUAL_REPORTS, YEARS


def test_registry_consistency():
    assert len(BANKS) == 13
    for (sym, year) in IR_ANNUAL_REPORTS:
        assert sym in BANKS
        assert year in YEARS


def test_audited_fy_filter_excludes_interim():
    rows = [
        {"posted": "2026-04-07", "description": "ZENITH BANK PLC - AUDITED FINANCIAL STATEMENTS FOR THE YEAR ENDED 31 DECEMBER 2025", "url": "a"},
        {"posted": "2025-08-19", "description": "UNITED BANK FOR AFRICA PLC - APPROVAL OF GROUP AUDITED HALF YEAR 2025 FINANCIAL STATEMENT", "url": "b"},
        {"posted": "2022-12-07", "description": "ECOBANK TRANSNATIONAL INCORPORATED - AUDITED FINANCIAL STATEMENTS FOR Q3 2022", "url": "c"},
        {"posted": "2023-11-03", "description": "UNITY BANK PLC- QUARTER 3 - FINANCIAL STATEMENT FOR 2023", "url": "d"},
        {"posted": "2025-02-26", "description": "UNITY BANK PLC- AUSITED  FINANCIAL STATEMENT FOR FOR THE YEAR ENDED 31 DEC 2023", "url": "e"},
        {"posted": "2023-06-05", "description": "X PLC- UNAUDITED FINANCIAL STATEMENT FOR 2022", "url": "f"},
    ]
    got = ngx.audited_fy_filings(rows)
    assert {k: v["url"] for k, v in got.items()} == {2025: "a", 2023: "e"}


def test_to_num_handles_brackets_and_commas():
    assert _to_num("1,234,567") == 1234567
    assert _to_num("(145,042,183)") == -145042183


def test_parse_text_table_sums_to_total():
    text = """5.1.2 Gross loans and advances to customers per sector
Group Group Bank Bank
In thousands of Naira
Agriculture 10 20 30 40
Oil And Gas - upstream 1,000 2,000 3,000 4,000
Others 5 5 5 5
 1,015 2,025 3,035 4,045
"""
    df, total, notes = parse_text_table(text, 4)
    assert list(df["sector"]) == ["Agriculture", "Oil And Gas - upstream", "Others"]
    assert total == [1015, 2025, 3035, 4045]
    assert [df[c].sum() for c in df.columns[1:]] == total
    assert notes == []


def test_sector_scan_finds_page():
    filler = "\n".join(f"Line {i} 1,000 2,000" for i in range(12))
    page = ("Credit concentration: loans and advances by sector\n"
            "Agriculture 1,000\nOil and gas 2,000\nManufacturing 3,000\nGeneral commerce 4,000\n"
            "Government 5,000\nConstruction 6,000\nReal estate 7,000\nTransport 8,000\n" + filler)
    res = pdfscan.scan_sector_table(["cover page", page, "notes"])
    assert res.best_page == 2
    assert res.best_sector_hits >= 6


def test_disclosure_scan_distinguishes_mentions():
    texts = ["We will report Scope 3 financed emissions in future.",
             "Scope 1 emissions were 1,234 tCO2e in 2025."]
    d = pdfscan.scan_disclosures(texts)
    assert d["scope3"]["mention_pages"] == [1] and d["scope3"]["quantified_pages"] == []
    assert d["scope1"]["quantified_pages"] == [2]
