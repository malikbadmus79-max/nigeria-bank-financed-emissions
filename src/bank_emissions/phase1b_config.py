"""Per-bank table specifications for Phase 1b extraction.

Each bank has a list of table specs. A spec says where the sector table is
(``page_re``: a regex searched in the page text to list candidate pages;
``start_re``: the line after which the rows begin, ``{year}`` is replaced by the
financial year), which layout parser to use, and which numeric column holds
which (level, basis). Candidate pages are tried in order and the first page on
which the parser succeeds is used.

Column indices are 0-based positions among the numeric columns of the table as
printed. Bases: ``gross`` or ``carrying``; ``not_stated`` where the page does
not say (resolved later against the loans note, plan section 3).

Levels: ``group`` = consolidated; ``bank`` = the Nigerian bank (or the
reporting entity where the reporting entity is a bank without a group table).
Holding-company ("Company") columns are not extracted: in holding-company
filings they describe the holding company, not the bank (plan section 3).

Sample (plan section 2): ETI excluded; Unity Bank 2020-2023; Jaiz 2024 needs
OCR and is handled separately.
"""

from __future__ import annotations

YEARS = range(2020, 2026)

SAMPLE_EXCLUSIONS = {
    ("ETI", y): "excluded: no credit-concentration-by-sector note in any NGX filing 2020-2025 (plan section 2)"
    for y in YEARS
}
SAMPLE_EXCLUSIONS.update({
    ("UNITYBNK", 2024): "not available: no audited statements on NGX after FY2023 (plan section 2)",
    ("UNITYBNK", 2025): "not available: no audited statements on NGX after FY2023 (plan section 2)",
})

# Tables whose printed figures do not add up, confirmed by reading the rendered
# page (not a parsing error). They are kept as printed and flagged (plan
# section 8.2: persistent failures are recorded and the bank-year flagged).
# Key: (bank, year, level, basis) -> what was seen.
PRINTED_INCONSISTENCIES = {
    ("UNITYBNK", 2023, "bank", "carrying"):
        "PDF p. 54: every row's gross less expected credit loss equals its net amount (within 1), but the printed "
        "ECL total 4,656,292 is the column sum without the Transportation ECL of 1,233 (full sum 4,657,526), so the "
        "printed net total 357,157,776 exceeds the net rows by 1,233; gross rows reconcile",
    ("WEMABANK", 2025, "group", "carrying"):
        "PDF p. 201: the Group carrying amount of 'Administrative and support service activities' is printed "
        "clipped as '7,178,47' (checked on the rendered page); the cell is left empty, so the carrying rows fall "
        "short of the printed total by that cell. Group gross and impairment, and the Bank columns, are complete",
    ("WEMABANK", 2023, "group", "carrying"): "PDF p. 156: the GENERAL row prints a carrying amount of 105,200,312 although its gross loans (111,868,986) less impairment (7,034,996) are 104,833,990; the 366,322 excess explains the 366,324 gap between the carrying rows and the printed carrying total 801,103,117 (gross and impairment columns reconcile). Same figures in the Group and Bank columns",
    ("WEMABANK", 2023, "bank", "carrying"): "PDF p. 156: the GENERAL row prints a carrying amount of 105,200,312 although its gross loans (111,868,986) less impairment (7,034,996) are 104,833,990; the 366,322 excess explains the 366,324 gap between the carrying rows and the printed carrying total 801,103,117 (gross and impairment columns reconcile). Same figures in the Group and Bank columns",
    ("ZENITHBANK", 2022, "group", "carrying"):
        "PDF p. 82: the printed Group total row is internally inconsistent: gross 4,123,974 less impairment 110,261 "
        "is 4,013,713, but the carrying total is printed 4,013,705; the 12 carrying rows sum to 4,013,713 (each row's "
        "gross less impairment equals its carrying amount within 1)",
    ("ACCESSCORP", 2025, "group", "gross"):
        "PDF p. 199: the table omits the 'Oil And Gas - downstream' row printed in every other year; the 22 printed "
        "rows sum to 249,219 below the printed total 13,694,446. The 2024 comparative column is short by 403,684, "
        "which equals the downstream row in the FY2024 report (403,683, PDF p. 209), so the gap is the omitted row",
    ("UBA", 2022, "group", "carrying"):
        "PDF p. 63: the Group 'Corporates - Others' row prints 11,012 (General Commerce) and blank cells elsewhere "
        "against a printed row total of 10,891 (difference 121; the Bank table on p. 64 prints a (121) cell that the "
        "Group table omits); text layer matches the rendered page",
    ("UBA", 2024, "group", "carrying"):
        "PDF p. 70: the Group 'Corporates - Term loans' row prints sector cells summing to 5,664,102 "
        "against a printed row total of 5,367,529 (difference 296,573); text layer matches the rendered page",
}

FILES = {
    # bank -> year -> file under data/raw/annual_reports (the copy logged in phase0_sources.csv)
}

GTCO_SECTORS = ["Agriculture", "Capital market & Financial institution", "Construction/ Real estate",
                "Education", "General Commerce", "Government", "Manufacturing", "Oil & gas",
                "Info.Telecoms & Transport", "Individual", "Others"]

UBA_SECTORS = ["Agriculture", "Construction and Real Estate", "Education", "Finance and Insurance",
               "General", "General Commerce", "Governments", "Information and Communication",
               "Manufacturing", "Oil and Gas", "Power and Energy", "Transportation and Storage"]

SPECS: dict[str, list[dict]] = {
    "ACCESSCORP": [
        dict(years=[2020, 2021], layout="rows", page_re=r"5\.1\.2 Gross loans and advances to customers per sector",
             start_re=r"5\.1\.2 Gross loans and advances", ncols=4,
             columns={("group", "gross"): 0, ("bank", "gross"): 2},
             note="Access Bank Plc was the listed entity; Bank columns are Access Bank Plc"),
        dict(years=[2022, 2023, 2024, 2025], layout="rows", page_re=r"5\.1\.2 Gross loans and advances to customers per sector",
             start_re=r"5\.1\.2 Gross loans and advances", ncols=4,
             columns={("group", "gross"): 0},
             note="Company columns (Access Holdings Plc) printed as dashes; not extracted"),
    ],
    "ZENITHBANK": [
        dict(years=list(YEARS), layout="rows", page_re=r"per industry sector as at",
             start_re=r"per industry sector as at .*{year}", ncols=6,
             columns={("group", "gross"): 0, ("group", "carrying"): 2, ("bank", "gross"): 3, ("bank", "carrying"): 5},
             skip_re=r"^(gross|impairment|carrying|loans and advances|in millions|allowance|amount|customers)"),
    ],
    "GTCO": [
        dict(years=list(YEARS), layout="columns", page_re=r"on-balance sheet items",
             start_re=r"^Dec-{year}$|Group Dec-{year}", sectors=GTCO_SECTORS,
             row_res=[r"Loans to individuals", r"Loans to non-individuals"],
             end_re=r"Financial assets at fair value|Investment securities", anchor_re=r"Loans to non-individuals",
             level_check_re=r"^Group$|^Group Dec-{year}", level_exclude_re=r"^Parent$|^Parent Dec-", columns={("group", "gross"): None}),
        dict(years=[2020], layout="columns", page_re=r"on-balance sheet items",
             start_re=r"^Dec-{year}$|Parent Dec-{year}", sectors=GTCO_SECTORS,
             row_res=[r"Loans to individuals", r"Loans to non-individuals"],
             end_re=r"Financial assets at fair value|Investment securities", anchor_re=r"Loans to non-individuals",
             level_check_re=r"^Parent$|^Parent Dec-{year}", level_exclude_re=r"^Group$|^Group Dec-", columns={("bank", "gross"): None},
             note="Parent = Guaranty Trust Bank Plc (listed entity for FY2020); from FY2021 the parent is the holding company"),
    ],
    "UBA": [
        dict(years=list(YEARS), layout="columns", page_re=r"Credit concentration . Industry",
             start_re=r"Loans and advances to customers", sectors=UBA_SECTORS,
             row_res=[r"^- ?(overdrafts?|term loans|others)"], end_re=r"^Investment securities",
             anchor_re=r"^Total financial assets", level_check_re=r"^Group(\s|$)", level_exclude_re=r"^Bank(\s|$)",
             year_check_re=r"31 December {year}|December 31, {year}", year_heading_first=True,
             columns={("group", "carrying"): None}),
        dict(years=list(YEARS), layout="columns", page_re=r"Credit concentration . Industry",
             start_re=r"Loans and advances to customers", sectors=UBA_SECTORS,
             row_res=[r"^- ?(overdrafts?|term loans|others)"], end_re=r"^Investment securities",
             anchor_re=r"^Total financial assets", level_check_re=r"^Bank(\s|$)", level_exclude_re=r"^Group(\s|$)",
             year_check_re=r"31 December {year}|December 31, {year}", year_heading_first=True,
             columns={("bank", "carrying"): None}),
    ],
    "FIRSTHOLDCO": [
        dict(years=list(YEARS), layout="blocks", page_re=r"Overdraft.{0,25}Term\s*loans",
             blocks=[dict(start_re=r"Overdraft Term ?loans Credit Cards Mortgage Total", ncols=5, value_col=4,
                          name="retail portfolio"),
                     dict(start_re=r"Overdraft Term ?loans Project finance", ncols=4, value_col=3,
                          name="corporate portfolio", after_previous=True)],
             skip_re=r"^(loans and advances|overdraft|n 'million)",
             total_re=r"^total at 31 december {year}", columns={("group", "carrying"): None}),
    ],
    # Credit-concentration table with five asset classes as columns; column 2 is
    # loans and advances to customers. Figures and dashes are centred rather than
    # right-aligned, so the column tolerance is widened; dashes are zero.
    # FY2020-FY2022 print one table (the reporting entity, Fidelity Bank Plc);
    # from FY2023 Group and Bank tables are printed on separate pages, the level
    # word heading the column-heading line ("Group balances with ...", "Group 31
    # December 2024"). The FY2021 filing prints two report pages per PDF page; the
    # sector table is on the right-hand half.
    "FIDELITYBK": [
        dict(years=[2020, 2021, 2022], layout="rows", page_re=r"Concentration by sector",
             start_re=r"^sector$|Concentration by sector", ncols=5, total_re=r"^total gross amount",
             year_check_re=r"31 Dec(ember)? {year}", columns={("bank", "gross"): 2}, col_tol=25.0,
             crop_frac={2021: (0.5, 0.0, 1.0, 1.0)},
             skip_re=r"^(concentration|financial assets)",
             note="single table; reporting entity Fidelity Bank Plc (no Group table printed)"),
        dict(years=[2023, 2024, 2025], layout="rows", page_re=r"Concentration by sector",
             start_re=r"^sector$|Concentration by sector", ncols=5, total_re=r"^total gross amount",
             year_check_re=r"31 Dec(ember)? {year}", columns={("group", "gross"): 2}, col_tol=25.0,
             level_check_re=r"^Group (balances|31 Dec)", level_exclude_re=r"^Bank (balances|31 Dec)",
             skip_re=r"^(concentration|financial assets)"),
        dict(years=[2023, 2024, 2025], layout="rows", page_re=r"Concentration by sector",
             start_re=r"^sector$|Concentration by sector", ncols=5, total_re=r"^total gross amount",
             year_check_re=r"31 Dec(ember)? {year}", columns={("bank", "gross"): 2}, col_tol=25.0,
             level_check_re=r"^Bank (balances|31 Dec)", level_exclude_re=r"^Group (balances|31 Dec)",
             skip_re=r"^(concentration|financial assets)"),
    ],
    "FCMB": [
        dict(years=list(YEARS), layout="rows", page_re=r"Concentration by sector",
             start_re=r"^GROUP$", ncols=6, columns={("group", "gross"): 3},
             skip_re=r"^(stage|in thousands|loan|non performing|commitments|gross lending|loans and advances)",
             space_thousands_years=[2025]),
    ],
    "STANBIC": [
        dict(years=list(YEARS), layout="rows", page_re=r"\(b\) Industry sectors",
             start_re=r"\(b\) Industry sectors", ncols=7, total_re=r"^carrying amount",
             year_check_re=r"December {year}", columns={("group", "carrying"): 4},
             skip_re=r"^(at 31 december|trading|assets|derivative|pledged|financial|investments|loans and|advances to|customers|banks|equity|\(excluding)"),
    ],
    "STERLINGNG": [
        dict(years=[2020, 2021, 2022], layout="rows", page_re=r"loans and advances by sector",
             start_re=r"loans and advances by sector", ncols=4,
             columns={("group", "not_stated"): 0, ("bank", "not_stated"): 2},
             note="columns printed Group Group Bank Bank; Bank = Sterling Bank Plc"),
        dict(years=[2023, 2024, 2025], layout="rows", page_re=r"loans and advances by sector",
             start_re=r"loans and advances by sector", ncols=4,
             columns={("group", "not_stated"): 0},
             note="columns printed Group Group Company Company; Company (holding company) not extracted"),
    ],
    "WEMABANK": [
        dict(years=list(YEARS), layout="rows", page_re=r"per industry sector",
             start_re=r"Loans and advances to customers\s+Loans and advances to customers|^Group Bank$|In (millions|thousands) of Naira",
             ncols=8, columns={("group", "gross"): 0, ("group", "carrying"): 3, ("bank", "gross"): 4, ("bank", "carrying"): 7},
             join_first=True, skip_re=r"^(loans and advances|in (millions|thousands)|group|gross|impairment|allowance|npl|amount)",
             year_check_re=r"as at (December 31, ?{year}|31 December, ?{year})",  # the table heading, not the running header
             align={2021: "left"}),  # FY2021 figures are left-aligned in their columns
    ],
    "UNITYBNK": [
        dict(years=[2020, 2021, 2022, 2023], layout="rows", page_re=r"Concentration of credit risk by Industry",
             start_re=r"^N'000", ncols=3, total_re=r"^total", columns={("bank", "gross"): 0, ("bank", "carrying"): 2},
             note="no Group/Bank split printed; reporting entity is Unity Bank Plc"),
    ],
    "JAIZBANK": [
        dict(years=[2020, 2021, 2022, 2023, 2025], layout="rows", page_re=r"By ?sector",
             start_re=r"By ?sector", ncols=2, total_re=r"^total", columns={("bank", "not_stated"): 0},
             # FY2020: the PDF page carries text of the facing page outside its page box
             # (x beyond the page width); cropping to the page box removes it
             crop_frac={2020: (0.0, 0.0, 1.0, 1.0)},
             note="no Group/Bank split printed; basis not stated on page"),
    ],
}
