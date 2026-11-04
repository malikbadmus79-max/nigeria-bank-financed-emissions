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
        "PDF p. 82: the 12 Group carrying rows sum to 4,013,713 against a printed carrying total of 4,013,705. The "
        "printed carrying total is the one confirmed elsewhere (statement of financial position p. 39 and loans note "
        "p. 72: 4,013,705); the table's gross total 4,123,974 is likewise 8 above the loans-note gross 4,123,966 "
        "(p. 72). The excess sits in the rows: General Commerce is printed 588,655 gross / 578,268 carrying here and "
        "588,646 gross in the FY2023 report's comparative. Rows kept as printed",
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

# ---------------------------------------------------------------------------
# Step 1 decisions (loans-note check, plan sections 3 and 8.3). Each decision
# names the page of the same report that supports it and the figure printed
# there, as printed; phase1b_build re-checks that the figure is on that page.
# The figures are evidence references only; no extracted value is taken from
# here.

# Basis resolved from the loans note. Key (bank, year) ->
# (basis as printed on the sector page, resolved basis, evidence page, figure printed there, reason).
_STERLING = {2020: (82, "613,359"), 2021: (78, "726,080"), 2022: (181, "758,183"), 2023: (198, "926,466"),
             2024: (229, "1,141,444"), 2025: (170, "1,468,632")}
_JAIZ = {2020: (48, "77,272,708"), 2021: (72, "124,185,609"), 2022: (91, "151,709,228"),
         2023: (110, "223,075,150"), 2024: (109, "289311930"), 2025: (98, "329,475,188")}
_GTCO = {2020: (78, "1,662,731,699"), 2021: (83, "1,802,587,381"), 2022: (84, "1,885,798,639"),
         2023: (89, "2,480,183,368"), 2024: (127, "2,785,664,040"), 2025: (125, "3,132,215,466")}
_STANBIC = {2020: (73, "655,292"), 2021: (73, "946,259"), 2022: (72, "1,238,195"), 2023: (82, "2,091,138"),
            2024: (80, "2,470,693"), 2025: (91, "2,460,336")}
_FBN = {2020: (124, "2,217,268", "carrying"), 2021: (125, "2,881,916", "carrying"), 2022: (109, "3,929,209", "gross"),
        2023: (121, "6,633,833", "gross"), 2024: (135, "9,262,953", "gross"), 2025: (246, "9,228,797", "gross")}

BASIS_DECISIONS: dict[tuple[str, int], tuple[str, str, int, str, str]] = {}
for _y, (_p, _f) in _STERLING.items():
    BASIS_DECISIONS[("STERLINGNG", _y)] = (
        "not_stated", "gross", _p, _f,
        "sector total equals the loans-note total of loans to corporates and individuals printed before "
        "'Less: Impairment'")
for _y, (_p, _f) in _JAIZ.items():
    BASIS_DECISIONS[("JAIZBANK", _y)] = (
        "not_stated", "gross", _p, _f,
        "sector total equals gross financing (Stage 1 + 2 + 3 before impairment) in the financing note"
        + ("; the FY2023 staging total 223,075,150 is 499 below the sector total 223,075,649 (flagged)"
           if _y == 2023 else "")
        + ("; FY2024 (OCR): equals the total of the collateral analysis of customer financing "
           "(not individually impaired plus individually impaired)" if _y == 2024 else ""))
for _y, (_p, _f) in _GTCO.items():
    BASIS_DECISIONS[("GTCO", _y)] = (
        "gross", "carrying", _p, _f,
        "sector total equals 'Loans and advances to customers' in the statement of financial position (net of "
        "impairment); the FY2023 categorisation note (p. 154, 156) prints total loans 2,614,624,821 gross and "
        "2,480,250,303 net including 66,935 of loans to banks")
for _y, (_p, _f) in _STANBIC.items():
    BASIS_DECISIONS[("STANBIC", _y)] = (
        "carrying", "gross", _p, _f,
        "the total row is labelled 'Carrying amount' but equals 'Gross loans and advances to customers' in the "
        "loans note" + {2022: " (within 1)", 2023: "; the FY2023 sector table is defective (see the STANBIC 2023 flag)",
                        2025: "; loans-note gross 2,460,336 is 600 above the sector total 2,459,736 (flagged)"}
        .get(_y, ""))
for _y, (_p, _f, _b) in _FBN.items():
    BASIS_DECISIONS[("FIRSTHOLDCO", _y)] = (
        "carrying", _b, _p, _f,
        ("sector total equals the net loans after ECL in the loans note and the statement of financial position "
         "(within 2)" if _b == "carrying" else
         "sector total equals the 'Total Loans and advances to customers' gross column before the ECL columns "
         "in the loans note") + "; the basis of the First HoldCo sector tables changes from carrying to gross in FY2022")

# Units resolved from the loans note and statement of financial position.
# Key (bank, year) -> (multiplier, units applied, evidence).
WEMA_UNIT_EVIDENCE_PAGES = {2020: (34, 70), 2021: (77, 128), 2022: (123, 123), 2023: (72, 123), 2024: (72, 119)}
UNIT_DECISIONS: dict[tuple[str, int], tuple[float, str, str]] = {}
for _y, (_sofp, _note) in WEMA_UNIT_EVIDENCE_PAGES.items():
    UNIT_DECISIONS[("WEMABANK", _y)] = (
        1e3, "thousands of naira",
        f"sector page heading prints 'In millions of Naira', but the sector totals equal exactly the loans note "
        f"(p. {_note}) and the statement of financial position (p. {_sofp}), both printed 'In thousands of "
        f"Nigerian Naira' (gross and carrying; carrying for 2022 differs, see flag); a millions reading would put "
        f"the loan book above 300 trillion naira. No conflicting evidence found")

# External-check findings not resolved by the rounding rule (plan section 8.3).
# Key (bank, year, level) or (bank, year, level, basis as printed) -> note.
EXTERNAL_FLAGS = {
    ("STANBIC", 2023, "group"):
        "FY2023 sector table defective: the loans column totals 4,182,275, twice the loans-note gross 2,091,138 "
        "(p. 82). From 'Hotels, restaurants and tourism' down the printed labels are one row out of step with the "
        "figures, and the last row ('Wholesale & retail trade', 2,091,138) carries the loan-book total. The FY2024 "
        "report's 2023 comparative (p. 159) prints the column without a Hotels row and sums to 2,091,137. The FY2023 rows "
        "are kept as printed outside the main specification; the comparative replaces them (author decision "
        "2026-11-04)",
    ("ZENITHBANK", 2022, "group", "gross"):
        "sector gross total 4,123,974 vs loans-note gross 4,123,966 (p. 72): 8 above, the same excess as in the "
        "carrying rows (see the ZENITHBANK 2022 printed-inconsistency note)",
    ("STANBIC", 2025, "group"): "sector total 2,459,736 vs loans-note gross 2,460,336 (p. 91): 600 unexplained",
    ("JAIZBANK", 2023, "bank"): "sector total 223,075,649 vs staging total 223,075,150 (p. 110): 499 unexplained",
    ("UBA", 2022, "bank"):
        "Bank sector total 2,133,989 vs Bank 'Loans and advances to customers' 2,123,097 in the statement of "
        "financial position (p. 31): 10,892 unexplained; the Group total matches",
    ("WEMABANK", 2022, "group", "carrying"):
        "carrying total 521,197,356 vs net loans 521,430,696 in the loans note (p. 123): 233,340 unexplained; "
        "gross matches",
    ("WEMABANK", 2022, "bank", "carrying"):
        "carrying total 521,197,356 vs net loans 521,430,696 in the loans note (p. 123): 233,340 unexplained; "
        "gross matches",
    ("ACCESSCORP", 2024, "group"):
        "no gross loans figure equal to the sector total found elsewhere in the report; the total exceeds net "
        "loans in the statement of financial position (11,487,710, p. 146) by 278,382, consistent with an ECL "
        "allowance",
    ("ACCESSCORP", 2025, "group"):
        "no gross loans figure equal to the printed sector total found elsewhere in the report; the total exceeds "
        "net loans in the statement of financial position (13,341,190, p. 141) by 353,256",
    ("FIDELITYBK", 2023, "group"):
        "no Group gross figure equal to the sector total found in the FY2023 report (Group net 3,092,419, p. 145); "
        "the FY2024 report prints FY2023 Group gross loans as 3,236,389 (43 above)",
}

# Replacement source for a defective table. Author decision 2026-11-04: the
# FY2024 report's 2023 comparative is used in the main specification for
# Stanbic 2023 (deviation from plan section 3, which does not use comparatives).
ALTERNATIVE_SOURCES = {
    ("STANBIC", 2023, "group"): dict(file="STANBIC_2024_ngx.pdf", page=159, start_re=r"At 31 December 2023",
                                     ncols=7, value_col=4, total_re=r"^carrying amount", basis="gross",
                                     main_spec=True,
                                     note="FY2024 report, 2023 comparative of the industry-sector table; used in "
                                          "the main specification because the FY2023 table (p. 158) is misaligned "
                                          "(author decision 2026-11-04)"),
}

# Printed-total residuals carried as a sector row. Author decision 2026-11-04.
# Key (bank, year, level, basis as printed) -> note. The amount is computed as
# the printed total less the printed sector rows; it is not typed.
RESIDUAL_ROWS = {
    ("ACCESSCORP", 2025, "group", "gross"):
        "the FY2025 table omits the 'Oil And Gas - downstream' row; the residual is the printed total less the 22 "
        "printed rows. Phase 2: the plan's 'Other' rule (economy-wide average intensity); sensitivity: assign it to "
        "oil and gas downstream (author decision 2026-11-04)",
}
RESIDUAL_LABEL = "unallocated (printed total residual)"

# Plan departures recorded in sample.csv and docs/phase1b_results.md.
LEVEL_DEVIATIONS = {
    ("FIDELITYBK", _y): "bank level: the FY2020-FY2022 filings print one sector table, for Fidelity Bank Plc; "
                        "Group tables are printed from FY2023, so the main specification (group where printed, "
                        "plan section 3) changes level in 2023"
    for _y in (2020, 2021, 2022)
}

SOURCE_DEVIATIONS = {
    ("STANBIC", 2023): "source: the FY2024 report's 2023 comparative (p. 159) replaces the FY2023 sector table "
                       "(p. 158), whose labels from 'Hotels, restaurants and tourism' down are one row out of step "
                       "with the figures and whose loans column totals twice the loan book (author decision "
                       "2026-11-04; plan section 3 does not use comparatives)",
    ("ACCESSCORP", 2025): "residual row: the printed total less the printed sector rows (249,219 million naira, the "
                          "omitted 'Oil And Gas - downstream' row) is carried as 'unallocated (printed total "
                          "residual)' (author decision 2026-11-04)",
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
