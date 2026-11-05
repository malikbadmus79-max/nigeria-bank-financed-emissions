"""Phase 4 (part 4): docs/results.md, generated from the processed CSVs so that
every number in the tables comes from the outputs.

    python -m bank_emissions.phase4_report
"""

from __future__ import annotations

import pandas as pd

from .phase1b_extract import PROCESSED, ROOT
from .phase3_estimate import PERIOD_YEARS, SENSITIVITIES
from .phase4_figures import period_sensitivities

DOCS = ROOT / "docs"


def md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for r in df.itertuples(index=False):
        out.append("| " + " | ".join("" if (isinstance(v, float) and pd.isna(v)) else str(v) for v in r) + " |")
    return "\n".join(out)


def mt(v, nd=2):
    return "" if pd.isna(v) else f"{v / 1e6:,.{nd}f}"


def tables() -> dict:
    T = {}
    t = pd.read_csv(PROCESSED / "financed_emissions_totals.csv")
    T["totals"] = md(pd.DataFrame({
        "Total": t.total_type, "Year": t.year.astype(str) + t.provisional.map({True: " (provisional)", False: ""}),
        "Banks": t.n_banks, "Loans (naira trillion)": (t.exposure_naira / 1e12).map("{:,.2f}".format),
        "Financed emissions (Mt CO2e)": t.tco2e.map(lambda v: mt(v))}))
    b = pd.read_csv(PROCESSED / "financed_emissions_bank_year.csv")
    p = b.pivot_table(index="bank", columns="year", values="tco2e")
    df = pd.DataFrame({"Bank": p.index})
    for y in p.columns:
        df[str(y) + (" (prov.)" if y == 2025 else "")] = [mt(v) for v in p[y]]
    T["bank_year"] = md(df)
    ns = pd.read_csv(PROCESSED / "national_share.csv")
    T["national"] = md(pd.DataFrame({"Total": ns.total_type, "Year": ns.year, "Financed emissions (Mt)": ns.tco2e.map(mt),
                                     "National total without LULUCF (Mt)": ns.national_without_lulucf_tco2e.map(mt),
                                     "Share": (ns.share_of_national * 100).map("{:.1f}%".format)}))
    sy = pd.read_csv(PROCESSED / "financed_emissions_sector_year.csv")
    g = sy[(sy.total_type == "balanced panel")]
    x = g.pivot_table(index="reporting_sector", columns="year", values="share_of_year_tco2e") * 100
    pooled = g[g.year.isin(PERIOD_YEARS)].groupby("reporting_sector")[["exposure_naira", "tco2e"]].sum()
    d2 = pd.DataFrame({"Sector": x.index,
                       "Loan share 2020-2024": [f"{v:.1f}" for v in (pooled.exposure_naira / pooled.exposure_naira.sum() * 100).reindex(x.index)],
                       "Emissions share 2020-2024": [f"{v:.1f}" for v in (pooled.tco2e / pooled.tco2e.sum() * 100).reindex(x.index)]})
    for y in x.columns:
        d2[f"{y}" + (" (prov.)" if y == 2025 else "")] = [("" if pd.isna(v) else f"{v:.1f}") for v in x[y]]
    T["sectors"] = md(d2.sort_values("Emissions share 2020-2024", key=lambda s: s.astype(float), ascending=False))
    s = pd.read_csv(PROCESSED / "financed_emissions_sensitivities.csv")
    tot = s[(s.row_type == "total: balanced panel")]
    rows = []
    for c in ["main"] + SENSITIVITIES:
        r = {"Specification": c}
        for _, z in tot.iterrows():
            r[str(z.year) + (" (prov.)" if str(z.year) == "2025" else "")] = mt(z[c], 1)
        rows.append(r)
    T["sens_totals"] = md(pd.DataFrame(rows))
    ps = period_sensitivities()
    others = [c for c in SENSITIVITIES if c != "S3j"]
    T["sens_banks"] = md(pd.DataFrame({
        "Bank": ps.index, "Main 2020-2024 (Mt)": ps["main"].map(mt),
        "Min excl. S3j": ps[others].min(axis=1).map(mt), "Set by": ps[others].idxmin(axis=1),
        "Max excl. S3j": ps[others].max(axis=1).map(mt), "Set by ": ps[others].idxmax(axis=1),
        "S3j": ps["S3j"].map(mt)}))
    dec = pd.read_csv(PROCESSED / "change_decomposition_2022_2024.csv")
    T["decomp"] = md(pd.DataFrame({
        "Bank": dec.bank, "2022 (Mt)": dec.tco2e_from.map(mt), "2024 (Mt)": dec.tco2e_to.map(mt),
        "Change (Mt)": dec.total_change.map(mt), "Loan volume": dec.exposure_volume_effect.map(mt),
        "Printed sector mix": dec.printed_mix_effect.map(mt),
        "Oil and gas split shares": dec.oil_gas_split_share_effect.map(mt),
        "Intensity": dec.intensity_effect.map(mt),
        "(info) O&G split shares at 2022 values": dec.info_oil_gas_split_share_effect_at_2022_values.map(mt),
        "Loans 2022 (naira tn)": (dec.exposure_from / 1e12).map("{:,.2f}".format),
        "Loans 2024 (naira tn)": (dec.exposure_to / 1e12).map("{:,.2f}".format)}))
    cn = pd.read_csv(PROCESSED / "constant_2022_naira.csv")
    T["constant"] = md(pd.DataFrame({
        "Total": cn.total_type, "Year": cn.year, "Deflator (2022 = 1)": cn.deflator_2022_1.map("{:.3f}".format),
        "Loans, nominal (naira tn)": (cn.exposure_nominal_naira / 1e12).map("{:,.2f}".format),
        "Loans, constant 2022 naira (tn)": (cn.exposure_constant_2022_naira / 1e12).map("{:,.2f}".format),
        "Financed emissions, main (Mt)": cn.tco2e_main.map(mt),
        "Constant-2022-naira loans x 2022 intensities (Mt)": cn.tco2e_constant_2022_naira_2022_intensity.map(mt)}))
    c = pd.read_csv(PROCESSED / "published_comparison.csv")
    T["compare"] = md(pd.DataFrame({
        "Bank": c.bank, "Year": c.year, "Published item": c["item"],
        "Published (t CO2e)": c.published_tco2e.map("{:,.0f}".format), "Source": c.document.str.split("/").str[-1] + " p. " + c.pdf_page.astype(str),
        "Estimate main (t)": c.estimate_main_tco2e.map("{:,.0f}".format),
        "Main / published": c.ratio_main_to_published.map("{:.2f}".format),
        "Bank level / published": c.ratio_bank_level_to_published.map(lambda v: "" if pd.isna(v) else f"{v:.2f}"),
        "Main x coverage / published": c.ratio_coverage_matched_to_published.map(lambda v: "" if pd.isna(v) else f"{v:.2f}")}))
    T["compare_ctx"] = md(c.drop_duplicates(["bank", "year"])[["bank", "year", "level_published", "coverage_published",
                                                               "method_published", "estimate_main_level_basis"]].rename(columns={
        "bank": "Bank", "year": "Year", "level_published": "Level (published)", "coverage_published": "Coverage (published)",
        "method_published": "Method (published)", "estimate_main_level_basis": "Estimate level/basis"}))
    d = pd.read_csv(PROCESSED / "disclosure_table.csv")
    short = {"figure disclosed": "figure", "statement only, no figure": "statement", "not found in the documents opened": "not found",
             "figure in a chart only (values not in the text layer)": "chart only", "metric disclosed in another unit": "other unit"}
    grid = d.assign(s=d.status.map(short), where=lambda z: z.document.fillna("").str.split("/").str[-1].str.replace(".pdf", "", regex=False)
                    + z.pdf_page.map(lambda p: "" if pd.isna(p) or p == "" else f" p. {int(float(p))}"))
    grid["cell"] = grid.s + grid["where"].map(lambda w: f" ({w})" if w.strip() else "")
    order = list(dict.fromkeys(d.bank))
    gp = grid.pivot(index="bank", columns="item", values="cell").loc[order].reset_index()
    T["disclosure"] = md(gp)
    a = pd.read_csv(PROCESSED / "ifrs_s2_b62_assessment.csv")
    T["b62"] = md(a[a.bank.isin(["UBA", "FIDELITYBK"])].pivot(index="requirement", columns="bank", values="finding").reset_index())
    f = pd.read_csv(ROOT / "data" / "interim" / "sensitivity_flags.csv")
    T["flags"] = md(f.groupby(["sensitivity", "driver"]).size().reset_index(name="bank-years flagged"))
    return T


def write():
    T = tables()
    dec = pd.read_csv(PROCESSED / "change_decomposition_2022_2024.csv").set_index("bank").loc["(balanced panel total)"]
    cn = pd.read_csv(PROCESSED / "constant_2022_naira.csv")
    cnb = cn[cn.total_type == "balanced panel"].set_index("year")
    ogs = pd.read_csv(ROOT / "data" / "interim" / "oil_gas_split_shares.csv")
    sh = ogs[ogs.used].groupby("year")[["share_upstream", "share_downstream", "share_services"]].mean().to_dict("index")
    doc = f"""# Results: financed emissions of NGX-listed banks, 2020-2025

Date: 2026-11-05. This document reports the results for research questions RQ1-RQ4 of `docs/analysis_plan.md`. Method details, checks and deviations by phase are in `docs/phase1b_results.md`, `docs/phase2a_results.md`, `docs/phase2b_results.md` and `docs/phase3_results.md`. All tables below are generated from the processed CSV files by `python -m bank_emissions.phase4_report`.

## What is estimated

Financed emissions are estimated as each bank's loans and advances to customers by sector (audited credit-concentration notes, 2020-2025) multiplied by a sector emission intensity: Nigeria's national inventory emissions of the sector (BTR1 and its National Inventory Document, 2020-2022) divided by the sector's gross value added at current basic prices (NBS). For 2023-2024, emissions are held at 2022 and divided by each year's value added (Option A, plan section 5). 2025 uses the 2024 intensities, is labelled provisional and is kept out of period totals and trends. The estimate is a sector-average approximation of the direct emissions associated with each bank's loan mix, comparable in kind to PCAF data-quality score 5 but without PCAF's attribution factor.

Sample: 12 banks (Ecobank Transnational excluded; Unity Bank 2020-2023 only), 70 bank-years. Main specification: group level where printed, gross loans where printed, else carrying amount (GTCO, UBA and First HoldCo 2020-2021 are on a carrying basis; Fidelity 2020-2022 is at bank level; plan section 3 and recorded deviations). The balanced panel is the 11 banks present in every year (all except Unity Bank).

## RQ1: financed emissions by bank and year

{T["totals"]}

From 2024 the two total types coincide (Unity Bank has no 2024-2025 figures).

Main specification by bank, Mt CO2e:

{T["bank_year"]}

Share of national emissions (BTR1 total without LULUCF), 2020-2022:

{T["national"]}

The share compares financed emissions, which apply national sector intensities to bank loans, with the national inventory total; it is a scale reference, not a share of emissions that the banks cause.

### Change 2022-2024

The rise in estimated financed emissions from 2023 onwards reflects the growth of loan values in naira, including the naira value of foreign-currency loans and of loans booked by subsidiaries outside Nigeria, set against each year's nominal GDP. It does not reflect measured physical emissions: sector emissions after 2022 are held at their 2022 level (Option A), so the intensity of every sector falls as nominal value added rises, and every change after 2022 comes from loan values and GDP.

Decomposition, Mt CO2e. Method: a counterfactual 2024 is formed in which undivided "Oil and gas" loans are split into upstream, downstream and services with the 2022 split shares (Access/FCMB averages) instead of the 2024 shares. The change from 2022 to that counterfactual is decomposed by additive LMDI-I over intensity groups into loan volume (change in total loans), printed sector mix (change in the shares of the banks' printed categories) and intensity (change in sector intensity, which under Option A is the change in nominal value added). The oil-and-gas split-share effect is actual 2024 minus the counterfactual, i.e. the effect of the year-varying split shares at 2024 loans and intensities. The four effects sum to the change; the residual is zero to rounding in every row.

{T["decomp"]}

For the balanced panel the change of {mt(dec.total_change)} Mt combines {mt(dec.exposure_volume_effect)} Mt from loan volume, {mt(dec.printed_mix_effect)} Mt from printed sector mix, {mt(dec.oil_gas_split_share_effect)} Mt from the oil-and-gas split shares and {mt(dec.intensity_effect)} Mt from intensity. The split shares move from {sh[2022]['share_upstream']:.1%} upstream, {sh[2022]['share_downstream']:.1%} downstream and {sh[2022]['share_services']:.1%} services in 2022 to {sh[2024]['share_upstream']:.1%}, {sh[2024]['share_downstream']:.1%} and {sh[2024]['share_services']:.1%} in 2024 (`data/interim/oil_gas_split_shares.csv`), shifting undivided oil-and-gas loans from the services intensity to the upstream intensity; the effect is zero for Access and FCMB (which print the split themselves) and Stanbic (no undivided oil-and-gas label). The size of this effect depends on where it is evaluated: at 2022 loans and intensities it is {mt(dec.info_oil_gas_split_share_effect_at_2022_values)} Mt (last column, for information; that ordering does not enter the sum). The combined categories (construction and real estate; information, telecoms and transport) are also split with year-varying NBS GDP shares; their effect, {mt(dec.info_combined_category_share_effect_in_mix)} Mt for the balanced panel, is left inside the printed-mix effect.

Loans and financed emissions in constant 2022 naira (implicit GDP deflator at basic prices, NBS rebasing annex pp. 7-8; recorded addition to the plan, descriptive):

{T["constant"]}

The last column applies the 2022 intensities to loans in constant 2022 naira. Balanced panel: {mt(cnb.loc[2022, "tco2e_constant_2022_naira_2022_intensity"])} Mt in 2022 and {mt(cnb.loc[2024, "tco2e_constant_2022_naira_2022_intensity"])} Mt in 2024 on that basis, against {mt(cnb.loc[2024, "tco2e_main"])} Mt in 2024 in the main specification. Loans in constant 2022 naira: {cnb.loc[2022, "exposure_constant_2022_naira"] / 1e12:,.2f} trillion (2022) and {cnb.loc[2024, "exposure_constant_2022_naira"] / 1e12:,.2f} trillion (2024). The aggregate deflator does not capture exchange-rate effects on foreign-currency loans or the different price movements of individual sectors.

## RQ2: sectors

Share of financed emissions by reporting sector, balanced panel (%), with the pooled 2020-2024 shares of loans and of financed emissions:

{T["sectors"]}

"Services" includes the lines placed in services by rule (general commerce, government, finance and insurance). "Other (economy-wide average rule)" includes "General", "Others" and the Access 2025 residual. Construction, manufacturing and non-oil mining share one intensity (the merged group). Within a sector every bank receives the same intensity, so differences between banks arise from loan mix and loan volume only. Figure: `figures/fig1_loan_vs_emission_share.png`.

## Sensitivities

Totals by specification, balanced panel, Mt CO2e (bank-years where a sensitivity does not apply keep the main value):

{T["sens_totals"]}

By bank, 2020-2024 totals, Mt CO2e (range over the sensitivities other than S3j; S3j shown separately):

{T["sens_banks"]}

Flags (reporting rule: the change from oil-refining, or water-and-waste, lines is at least half of the net change):

{T["flags"]}

S3j (downstream lending treated as oil refining) is driven entirely by the oil-refining intensity, which rises to 82.9 t CO2e per million naira in 2024 as refining value added falls to N11.8 billion; S3j sets the maximum of the totals from 2021. Figure: `figures/fig3_estimate_ranges.png`.

## RQ3: comparison with published financed emissions

Published figures as printed, with the estimate for the same bank and year. Ratios are estimate / published; nothing is adjusted to close the gaps. "Main x coverage" applies UBA's printed share of gross exposure included (90% in 2023, 52% in 2024).

{T["compare"]}

{T["compare_ctx"]}

Known sources of divergence (plan section 8.5), none quantified here:
- Attribution: PCAF attributes a borrower's emissions in proportion to the loan's share of the borrower's equity and debt; the estimate attributes sector-average emissions per naira of value added to each naira lent.
- Emission factors: the estimate uses value added (smaller than revenue), which gives higher intensities than revenue-based factors; the published figures use borrower or proxy data (UBA weighted data quality scores 4.35-4.37).
- Scopes: the estimate covers the direct emissions of the borrowers' sectors (production-based, electricity emissions in the power sector only); UBA reports borrowers' Scope 1 and 2 and Scope 3 separately; Fidelity 2023 reports borrowers' Scopes 1 and 2.
- Coverage and level: UBA covers 90% and 52% of gross exposure; Fidelity's 2023 boundary excludes subsidiaries outside Nigeria; the estimate's main specification is at group level (Fidelity's 2023 Bank and Group tables differ only in consumer credit, which takes zero intensity, so the bank-level estimate equals the main one that year).
- Exposure basis: the UBA estimate is on carrying amounts (gross not printed by sector).
- UBA's 2024 report prints 2024 Scope 1&2 financed emissions as 602,146 tCO2e in the SASB table (p. 33) and 620,146.98 tCO2e in the asset-class table (p. 37); both are listed.
- The Fidelity 2025 estimate is provisional.

Figure: `figures/fig4_estimate_vs_published.png`.

## RQ4: disclosure

What the documents opened show (latest annual report in the source log, and the sustainability report where one was obtained). "Not found" means not found in those documents, not that the bank does not disclose the item elsewhere. Passages are recorded as printed in `data/processed/disclosure_table.csv`.

{T["disclosure"]}

IFRS S2 requirements for commercial banks (paragraph B62, official text; ifrs.org):
- B62(a): absolute gross financed emissions, disaggregated by Scope 1, Scope 2 and Scope 3, for each industry by asset class (industry by GICS 6-digit code in the 2023 text; the December 2025 amendments let the entity choose the classification, B62A);
- B62(b): gross exposure to each industry by asset class (funded carrying amounts before the loss allowance);
- B62(c): the percentage of gross exposure included in the calculation;
- B62(d): the methodology, including the method of attributing emissions to the size of the exposure.
IFRS S2 applies to annual periods beginning on or after 1 January 2024 (C1); in the first year an entity need not disclose Scope 3, including financed emissions (C4(b)); the 2025 amendments (29A-29C, effective 1 January 2027) allow Category 15 to be limited to financed emissions.

Against B62, for the two banks with a financed-emissions figure (pages read):

{T["b62"]}

The other ten banks show no financed-emissions figure in the documents opened.

FRC Nigeria roadmap (amended 2026, PDF p. 19): early adopters for periods ending on or before 31 December 2023; voluntary adoption for periods beginning 1 January 2024 to periods ending 31 December 2027; mandatory adoption for all public interest entities, which include entities listed on a recognised Nigerian exchange (PDF p. 33), for accounting periods beginning on or after 1 January 2028. Zenith Bank's 2025 report states that it applies the IFRS S2 Scope 3 transition relief and plans to report baseline financed emissions in Q1 2028. Figure: `figures/fig5_disclosure_grid.png`.

## Limitations

- Sector-average intensities: within a sector every bank receives the same intensity; the estimates are not attributions of identified borrowers' emissions.
- Value added rather than revenue: intensities per naira of value added are higher than revenue-based factors; the size of the difference is not estimated.
- Production-based allocation: electricity emissions sit in the power sector; borrowers' purchased-electricity (Scope 2) and value-chain (Scope 3) emissions are not attributed; residential fuel combustion (about 17% of national emissions) is not attributed to any sector.
- Emissions after 2022 are held at 2022 (BTR1 ends in 2022); changes in 2023-2025 come from loans and nominal GDP only. 2025 is provisional (NBS 2025 GDP by activity not located).
- Stocks against flows: year-end loan balances are compared with annual value added; group exposures include foreign-currency loans translated at closing rates and loans booked outside Nigeria, to which Nigerian intensities apply poorly (plan section 3 lists the banks with foreign operations).
- Exposure basis: GTCO and UBA are on carrying amounts, First HoldCo is on carrying amounts in 2020-2021, Fidelity is at bank level in 2020-2022, and Stanbic 2023 uses the following year's comparative.
- Sector labels: undivided "Oil and gas" is split by the shares printed by Access and FCMB; combined categories are split by GDP shares; several labels ("General", "Others") take the economy-wide average.
- The oil-refining intensity is very sensitive to the small and falling refining value added (S3j).
- Climate Watch values (S6) are not redistributed (licence not confirmed); S6 financed emissions are reported.
- Disclosure findings cover the documents opened; operational emissions charts without text values (UBA) are not read.

## What the study cannot claim

- That the estimates are any bank's actual financed emissions; they are sector-average approximations of the emissions associated with each bank's loan mix.
- That the estimates follow the PCAF Standard or meet the IFRS S2 measurement requirements.
- That a difference between an estimate and a published figure shows that either is wrong; the methods, coverage and scopes differ.
- That differences between banks reflect differences in borrower emission efficiency; they arise from sector mix and loan volume.
- That changes over 2023-2025 reflect changes in physical emissions; they reflect loan values (including currency effects) and nominal GDP.
- That loans booked by foreign subsidiaries carry Nigerian emission intensities.
- That borrowers' purchased-electricity (Scope 2) and value-chain (Scope 3) emissions are included.
- That emissions from loans to individuals, government or financial institutions are measured; they are set by rules, and the sensitivities show how much the totals depend on them.
- That the results cover the whole Nigerian banking system; the sample is the NGX-listed banks with sector notes, and only loans and advances to customers.
- That value-added-based intensities are comparable to revenue-based factors.
- That a bank which shows no disclosure in the documents opened discloses nothing elsewhere.

## Recorded additions and deviations

Recorded additions to the plan (dated in `docs/analysis_plan.md`): S3f (2026-11-04); crosswalk and sector-map sign-off with S3g-S3l (2026-11-05); sensitivity flag rule, 2022-2024 decomposition and constant-2022-naira series (2026-11-05). Deviations are listed in each phase results document: Fidelity level change, Wema units from the loans note, Stanbic 2023 comparative, Access 2025 residual row, the re-read method, merged manufacturing/construction/mining intensity, S5 economy-wide with LULUCF, S6 values kept out of the repository, and the identity check replacing the GDP-weighted-average check.
"""
    (DOCS / "results.md").write_text(doc, encoding="utf-8")
    return doc


def main() -> int:
    doc = write()
    print(f"docs/results.md written ({len(doc):,} characters)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
