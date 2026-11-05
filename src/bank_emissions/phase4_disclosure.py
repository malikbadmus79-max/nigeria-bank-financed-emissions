"""Phase 4 (part 2): disclosure table (RQ4).

For each sampled bank (and ETI, which stays in the RQ4 table, plan section 2)
and each item - Scope 1, Scope 2, Scope 3 (operational), financed emissions,
PCAF method, green-finance amounts - the table records what the documents
opened show, with document and page. Each finding is an EVIDENCE entry: the
passage is re-read from the page with its pattern (the run stops if it does not
match) and stored as printed. Items without an entry are 'not found in the
documents opened', with those documents listed; that is not a statement that
the bank does not disclose the item elsewhere.

Documents opened per bank: the latest annual report in the source log and the
sustainability report in data/raw/sustainability/ where one was obtained in
Phase 0. A keyword scan of those documents (scope 1-3 with figures, financed
emissions, PCAF, green/sustainable finance amounts) located the pages; each
entry below was then read on the page.

Writes data/processed/disclosure_table.csv and data/processed/ifrs_s2_b62_assessment.csv.

    python -m bank_emissions.phase4_disclosure
"""

from __future__ import annotations

import re

import pandas as pd

from .phase1b_extract import INTERIM, PROCESSED, ROOT
from .phase4_compare import page_text

ITEMS = ["scope_1", "scope_2", "scope_3", "financed_emissions", "pcaf_method", "green_finance"]
BANKS = ["ACCESSCORP", "ZENITHBANK", "GTCO", "UBA", "FIRSTHOLDCO", "FIDELITYBK", "FCMB", "STANBIC", "STERLINGNG",
         "WEMABANK", "UNITYBNK", "JAIZBANK", "ETI"]

AR = "data/raw/annual_reports/"
SU = "data/raw/sustainability/"
FIG = "figure disclosed"
STMT = "statement only, no figure"
CHART = "figure in a chart only (values not in the text layer)"
OTHER = "metric disclosed in another unit"

# (bank, item, status, document, pdf page, pattern whose first group is stored as printed, note)
EVIDENCE = [
    ("ACCESSCORP", "scope_1", FIG, AR + "ACCESSCORP_2025_ir.pdf", 66,
     r"(Table 18: Greenhouse Gas Emissions by Scope - Mtco2e Scope 2024 Performance 2025 Performance Scope 1 [\d,.]+ [\d,.]+)",
     "Group; table header prints 'Mtco2e' but the assurance appendix of the sustainability report (p. 55) gives the same values in tCO2e"),
    ("ACCESSCORP", "scope_2", FIG, AR + "ACCESSCORP_2025_ir.pdf", 66, r"(Scope 2 [\d,.]+ [\d,.]+)", "2024, 2025"),
    ("ACCESSCORP", "scope_3", FIG, AR + "ACCESSCORP_2025_ir.pdf", 66, r"(Scope 37 [\d,.]+ [\d,.]+)",
     "'Scope 3' with footnote 7; business travel (air travel and ride-hailing), p. 66"),
    ("ACCESSCORP", "financed_emissions", STMT, AR + "ACCESSCORP_2025_ir.pdf", 65,
     r"(For financed emissions across our lending and investment portfolio, we plan to adopt the Partnership for Carbon Accounting Financials \(PCAF\) methodology)", ""),
    ("ACCESSCORP", "pcaf_method", STMT, AR + "ACCESSCORP_2025_ir.pdf", 65, r"(we plan to adopt the Partnership for Carbon Accounting Financials \(PCAF\) methodology)", "planned"),
    ("ACCESSCORP", "green_finance", FIG, AR + "ACCESSCORP_2025_ir.pdf", 59,
     r"(Green Asset Portfolio N92\.14 billion As of 31 December 2025)", "also: N72.3 billion deployed under the Sustainable Finance Framework in 2025 (same page); target N475 billion"),
    ("ZENITHBANK", "scope_1", FIG, AR + "ZENITHBANK_2025_ngx.pdf", 61, r"(Direct GHG emissions \(Scope 1\) in mtCO₂e Indicators 2024 2025 .{0,80}?Scope 1 [\d,.]+ [\d,.]+)",
     "Group; vehicles only; 2025 value printed '52,475.'"),
    ("ZENITHBANK", "scope_2", FIG, AR + "ZENITHBANK_2025_ngx.pdf", 61, r"(Purchased electricity-scope 2 [\d,.]+ [\d,.]+)", "2024, 2025; location-based"),
    ("ZENITHBANK", "scope_3", STMT, AR + "ZENITHBANK_2025_ngx.pdf", 26,
     r"(In accordance with IFRS S2 transition relief, Scope 3 greenhouse gas emissions have not been disclosed in this reporting period\.)", "IFRS S2 C4(b) relief"),
    ("ZENITHBANK", "financed_emissions", STMT, AR + "ZENITHBANK_2025_ngx.pdf", 88,
     r"(Measure value of financed emissions \(Q1-Q4 2027\)\. • Report baseline financed emissions \(Q1 2028\)\.)", "planned"),
    ("GTCO", "scope_3", STMT, AR + "GTCO_2025_ir.pdf", 101,
     r"(our Scope 3 \(financed emissions\) remain the highest source of carbon emissions from our operations)", "no figure"),
    ("GTCO", "financed_emissions", STMT, AR + "GTCO_2025_ir.pdf", 101,
     r"(our Scope 3 \(financed emissions\) remain the highest source of carbon emissions from our operations)", "no figure"),
    ("UBA", "scope_1", CHART, SU + "UBA_2024_sustainability.pdf", 36,
     r"(UBA Nigeria’s Scope 1, 2 and 3\(excluding financed emissions\) emissions decreased by 4\.48% in 2024 compared to 2023\.)", "UBA Nigeria; chart of Scope 1, 2 and 3 by FY 2021-2024"),
    ("UBA", "scope_2", CHART, SU + "UBA_2024_sustainability.pdf", 36,
     r"(UBA Nigeria’s Scope 1, 2 and 3\(excluding financed emissions\) emissions decreased by 4\.48%)", "UBA Nigeria; chart"),
    ("UBA", "scope_3", CHART, SU + "UBA_2024_sustainability.pdf", 36,
     r"(Scope 1, 2 and 3\(excluding financed emissions\))", "UBA Nigeria; chart; upstream Scope 3"),
    ("UBA", "financed_emissions", FIG, SU + "UBA_2024_sustainability.pdf", 33,
     r"(Absolute gross financed emissions, disaggregated by\(1\) Scope 1& 2\(2\) Scope 3 Scope1&2:2,258,646 tCO2eScope3: 804,727 tCO2e Scope1&2: 602,146 tCO2e Scope 3: 378,879\.66 tCO2e)",
     "2023 and 2024; 90% and 52% of gross exposure included (same page); p. 37 asset-class table gives 2024 Scope 1 + 2 as 620,146.98"),
    ("UBA", "pcaf_method", FIG, SU + "UBA_2024_sustainability.pdf", 38, r"(We adopted the PCAF Standard” - the most widely accepted, GHG Protocol-compliant standard for financed emissions calculations\.)",
     "method applied; weighted data quality scores on p. 37"),
    ("FIRSTHOLDCO", "scope_1", FIG, AR + "FIRSTHOLDCO_2025_ir.pdf", 104, r"(Scope 1 \(Direct, e\.g\., diesel use\) [\d,.]+ [\d,.]+ [\d,.]+)",
     "FirstBank 2025; original, median-normalised and outlier-removed values (tCO2e)"),
    ("FIRSTHOLDCO", "scope_2", FIG, AR + "FIRSTHOLDCO_2025_ir.pdf", 104, r"(Scope 2 \(Purchased electricity\) [\d,.]+ [\d,.]+ [\d,.]+)", "as Scope 1"),
    ("FIRSTHOLDCO", "financed_emissions", STMT, AR + "FIRSTHOLDCO_2025_ir.pdf", 104,
     r"(FirstBank has been calculating financed emissions since 2024 and, as a member of the Partnership for Carbon Accounting Financials \(PCAF\), continues to strengthen its methodology to establish a reliable baseline for reporting and target setting\.)", ""),
    ("FIRSTHOLDCO", "pcaf_method", STMT, AR + "FIRSTHOLDCO_2025_ir.pdf", 104, r"(as a member of the Partnership for Carbon Accounting Financials \(PCAF\))", "member; no figure"),
    ("FIDELITYBK", "scope_1", FIG, AR + "FIDELITYBK_2025_ir.pdf", 99, r"(Scope 1 [\d,.]+ [\d,.]+ [\d,.]+)", "2025, 2024, 2023; tCO2e"),
    ("FIDELITYBK", "scope_2", FIG, AR + "FIDELITYBK_2025_ir.pdf", 99, r"(Scope 2 [\d,.]+ [\d,.]+ [\d,.]+)", "2025, 2024, 2023; location-based"),
    ("FIDELITYBK", "scope_3", FIG, AR + "FIDELITYBK_2025_ir.pdf", 99, r"(Scope 3 [\d,.]+ [\d,.]+ [\d,.]+)", "includes Category 15"),
    ("FIDELITYBK", "financed_emissions", FIG, AR + "FIDELITYBK_2025_ir.pdf", 99,
     r"(Category 15 – Investments: Financed Emission [\d,.]+ [\d,.]+ [\d,.]+)", "2025, 2024, 2023 (tCO2e)"),
    ("FIDELITYBK", "pcaf_method", FIG, AR + "FIDELITYBK_2025_ir.pdf", 100,
     r"(Our approach follows the Partnership for Carbon Accounting Financials \(PCAF\) Global GHG Accounting and Reporting Standard for the Financial Industry \(2020\))", "method applied"),
    ("FIDELITYBK", "green_finance", FIG, AR + "FIDELITYBK_2025_ir.pdf", 100,
     r"(with 612 transactions valued at N929\.10 million)", "green financing 2025; N512.92 million (2023) and N509.01 million (2024) on the same page"),
    ("STERLINGNG", "scope_1", FIG, AR + "STERLINGNG_2025_ir.pdf", 38, r"(Scope 1 Direct GHG Emissions Diesel [\d,.]+ [\d,.]+ -?[\d.]+% Petrol [\d,.]+ [\d,.]+)", "Group, 2024 and 2025, by driver"),
    ("STERLINGNG", "scope_2", FIG, AR + "STERLINGNG_2025_ir.pdf", 38, r"(Scope 2 Indirect Emissions \(Energy\) Electricity [\d,.]+ [\d,.]+)", "2024, 2025"),
    ("STERLINGNG", "scope_3", FIG, AR + "STERLINGNG_2025_ir.pdf", 38, r"(Scope 3 Indirect Emissions \(All other Indirect Emissions\) Air Travel [\d,.]+ [\d,.]+)", "air travel; total 6,692.79 tCO2e in 2025"),
    ("STERLINGNG", "financed_emissions", STMT, SU + "STERLINGNG_2024_sustainability.pdf", 29,
     r"(we continue to estimate our financed emissions using the Partnership for Carbon Accounting Financials \(PCAF\) methodology)", "no figure"),
    ("STERLINGNG", "pcaf_method", STMT, SU + "STERLINGNG_2024_sustainability.pdf", 29, r"(Partnership for Carbon Accounting Financials \(PCAF\) methodology)", "stated; no figure"),
    ("STERLINGNG", "green_finance", STMT, SU + "STERLINGNG_2024_sustainability.pdf", 9, r"(scaling our green finance portfolio to N150 billion by 2030)", "target, not a portfolio amount"),
    ("WEMABANK", "scope_1", OTHER, AR + "WEMABANK_2025_ngx.pdf", 61, r"(Year 1 \(2024\) ≤ 8,567\.5 7,582\.2 ≥7% 13% Year 2 \(2025\) ≤ 7,203\.09 6,234 18% 22%)",
     "'Internal emissions' in tCO2e (achieved 7,582.2 in 2024, 6,234 in 2025); scopes not separated"),
    ("WEMABANK", "financed_emissions", OTHER, AR + "WEMABANK_2025_ngx.pdf", 61, r"(Financed Emissions \(Increase in impact sector of the loan portfolio\))",
     "KPI is the impact-sector share of the loan portfolio (13% in 2024, 22% in 2025), not tCO2e"),
    ("WEMABANK", "green_finance", FIG, AR + "WEMABANK_2025_ngx.pdf", 58, r"(invest in the renewable segments by building the portfolio from N43bn to N100bn over the next 5 years)", "renewables portfolio N43bn; target N100bn"),
]


def documents_opened() -> dict[str, list[str]]:
    src = pd.read_csv(INTERIM / "phase0_sources.csv", dtype=str, keep_default_na=False)
    ar = src[(src.doc_type == "annual_report") & (src.local_path != "")]
    out = {}
    for b in BANKS:
        g = ar[ar.symbol == b].sort_values("year")
        docs = [g.local_path.iloc[-1]] if len(g) else []
        docs += [p.relative_to(ROOT).as_posix() for p in (ROOT / SU).glob(f"{b}_*.pdf")]
        out[b] = docs
    return out


def build() -> pd.DataFrame:
    opened = documents_opened()
    rows = []
    seen = set()
    for bank, item, status, doc, page, pat, note in EVIDENCE:
        t = page_text(ROOT / doc, page)
        m = re.search(pat, t)
        if not m:
            raise LookupError(f"{bank} {item}: pattern not found on {doc} p. {page}")
        rows.append(dict(bank=bank, item=item, status=status, as_printed=m.group(1), document=doc, pdf_page=page,
                         note=note, documents_opened="; ".join(opened[bank])))
        seen.add((bank, item))
    for b in BANKS:
        for it in ITEMS:
            if (b, it) not in seen:
                rows.append(dict(bank=b, item=it, status="not found in the documents opened", as_printed="",
                                 document="", pdf_page="", note="",
                                 documents_opened="; ".join(opened[b]) or "none with a text layer"))
    df = pd.DataFrame(rows)
    df["bank"] = pd.Categorical(df.bank, BANKS, ordered=True)
    df["item"] = pd.Categorical(df["item"], ITEMS, ordered=True)
    return df.sort_values(["bank", "item"]).reset_index(drop=True)


# IFRS S2 B62 (commercial banking) against what the pages read show
B62 = {
    "B62(a) absolute gross financed emissions by Scope 1, 2 and 3": "a",
    "B62(a) for each industry by asset class": "a_ind",
    "B62(b) gross exposure by industry and asset class": "b",
    "B62(c) percentage of gross exposure included": "c",
    "B62(d) methodology, including attribution": "d",
}
ASSESS = {
    "UBA": {"a": "partly: Scope 1&2 combined and Scope 3 (p. 33)", "a_ind": "yes, 2024: by industry and by asset class (p. 37)",
            "b": "covered loans only: 'Total Outstanding' by industry and asset class (p. 37)",
            "c": "yes: 90% (2023), 52% (2024) (p. 33)", "d": "PCAF Standard named; asset classes listed (p. 38); attribution method not read on the pages opened"},
    "FIDELITYBK": {"a": "total Category 15 only (p. 99)", "a_ind": "not found on the pages read", "b": "not found on the pages read",
                   "c": "not found on the pages read", "d": "PCAF Standard (2020) named (p. 100)"},
}


def assessment(dt: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for b in BANKS:
        fe = dt[(dt.bank == b) & (dt["item"] == "financed_emissions")].status.iloc[0]
        for label, k in B62.items():
            val = ASSESS.get(b, {}).get(k) or ("no financed-emissions figure found" if fe != FIG else "")
            rows.append(dict(bank=b, requirement=label, finding=val))
    return pd.DataFrame(rows)


def main() -> int:
    dt = build()
    dt.to_csv(PROCESSED / "disclosure_table.csv", index=False)
    a = assessment(dt)
    a.to_csv(PROCESSED / "ifrs_s2_b62_assessment.csv", index=False)
    print(dt.pivot(index="bank", columns="item", values="status").to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
