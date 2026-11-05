"""Phase 4 (part 1): comparison with published figures (RQ3), change over time,
constant-2022-naira series, and share of national emissions.

Published figures are read from the PDF pages named in PUBLISHED with a
pattern anchored on the printed label; a pattern that does not match stops the
run, so no figure is typed in by hand. Nothing is adjusted to close gaps; the
coverage-matched estimate applies the coverage share printed by the bank, as
plan section 8.5 sets out.

Outputs:
- data/processed/published_comparison.csv
- data/processed/change_decomposition_2022_2024.csv
- data/processed/constant_2022_naira.csv
- data/processed/national_share.csv

    python -m bank_emissions.phase4_compare
"""

from __future__ import annotations

import math
import re

import numpy as np
import pandas as pd

from .phase1b_extract import PROCESSED, ROOT
from .phase2a_crosswalk import ECONOMY_WIDE
from .phase3_estimate import PERIOD_YEARS, ZERO_GROUP

SUST = ROOT / "data" / "raw" / "sustainability"
AR = ROOT / "data" / "raw" / "annual_reports"
NBS = ROOT / "data" / "raw" / "intensity" / "nbs_microdata_147_1256.pdf"


def page_text(pdf, page: int) -> str:
    import pypdfium2

    t = pypdfium2.PdfDocument(str(pdf))[page - 1].get_textpage().get_text_range()
    return re.sub(r"\s+", " ", t.replace("‑", "-").replace("￾", ""))


def grab(pdf, page: int, pattern: str) -> tuple[str, ...]:
    m = re.search(pattern, page_text(pdf, page))
    if not m:
        raise LookupError(f"pattern not found on {pdf.name} p. {page}: {pattern}")
    return m.groups()


def num(s: str) -> float:
    return float(s.replace(",", ""))


# ---------------------------------------------------------------------------
# RQ3: published figures


def published() -> pd.DataFrame:
    rows = []
    f23 = SUST / "FIDELITYBK_2023_sustainability.pdf"
    (v,) = grab(f23, 27, r"Category 15 -financed emissions – ([\d,]+\.\d+) tCO2e")
    rows.append(dict(bank="FIDELITYBK", year=2023, item="Scope 3 Category 15 financed emissions (gross total scopes 1 and 2)",
                     published_tco2e=num(v), value_as_printed=v, unit_as_printed="tCO2e",
                     document=f23.relative_to(ROOT).as_posix(), pdf_page=27, printed_page="52-53 (two-page spread)",
                     level_published="bank: boundary is Fidelity Bank's offices and channels across Nigeria, excluding "
                                     "subsidiaries outside Nigeria (same page)",
                     coverage_published="not stated", method_published="not stated on this page (PCAF named on p. 30)",
                     borrower_scopes_published="Scopes 1 and 2 of borrowers"))
    f25 = AR / "FIDELITYBK_2025_ir.pdf"
    v25, v24, v23 = grab(f25, 99, r"Category 15 – Investments: Financed Emission ([\d,]+\.\d+) ([\d,]+\.\d+) ([\d,]+\.\d+)")
    (hdr,) = grab(f25, 99, r"Scope 3 emissions \((tCO2e)\)")
    for y, v in ((2024, v24), (2025, v25)):
        rows.append(dict(bank="FIDELITYBK", year=y, item="Scope 3 Category 15 - Investments: Financed Emission",
                         published_tco2e=num(v), value_as_printed=v, unit_as_printed=hdr,
                         document=f25.relative_to(ROOT).as_posix(), pdf_page=99, printed_page="99",
                         level_published="bank (Fidelity Bank; operational boundary 'all bank locations across Nigeria', "
                                         "p. 100); financed-emissions boundary not stated",
                         coverage_published="not stated",
                         method_published="PCAF Global GHG Accounting and Reporting Standard (2020), p. 100",
                         borrower_scopes_published="not stated"))
    rows.append(dict(bank="FIDELITYBK", year=2023, item="(consistency) 2023 column of the FY2025 table",
                     published_tco2e=num(v23), value_as_printed=v23, unit_as_printed=hdr,
                     document=f25.relative_to(ROOT).as_posix(), pdf_page=99, printed_page="99",
                     level_published="bank", coverage_published="not stated", method_published="PCAF (p. 100)",
                     borrower_scopes_published="not stated"))
    uba = SUST / "UBA_2024_sustainability.pdf"
    s12_23, s3_23, s12_24, s3_24 = grab(uba, 33, r"Scope1&2:\s?([\d,]+) tCO2eScope3: ([\d,]+) tCO2e Scope1&2: ([\d,]+) "
                                                 r"tCO2e Scope 3: ([\d,.]+) tCO2e")
    c23, c24 = grab(uba, 33, r"included in the financed emissions calculation (\d+)% (\d+)%")
    t_s12, t_s3, t_share = grab(uba, 37, r"Total 2,249,565\.50 ([\d,]+\.\d+) ([\d,]+\.\d+) (\d+)%")
    lvl = ("not stated; the same section (p. 32) describes UBA as operating in 24 countries")
    meth = "PCAF Standard and PCAF Database (p. 38); weighted data quality score 4.37 and 4.35 by asset class (p. 37, 2024)"
    for y, s12, s3, cov in ((2023, s12_23, s3_23, c23), (2024, s12_24, s3_24, c24)):
        for item, v, scopes in (("Absolute gross financed emissions, Scope 1&2 (SASB table)", s12, "Scopes 1 and 2 of borrowers"),
                                ("Absolute gross financed emissions, Scope 3 (SASB table)", s3, "Scope 3 of borrowers")):
            rows.append(dict(bank="UBA", year=y, item=item, published_tco2e=num(v), value_as_printed=v,
                             unit_as_printed="tCO2e", document=uba.relative_to(ROOT).as_posix(), pdf_page=33,
                             printed_page="33", level_published=lvl,
                             coverage_published=f"{cov}% of gross exposure (p. 33)",
                             coverage_share=int(cov) / 100, method_published=meth if y == 2024 else "PCAF (p. 38)",
                             borrower_scopes_published=scopes))
    rows.append(dict(bank="UBA", year=2024, item="Scope 1 + Scope 2 emissions, asset-class table total",
                     published_tco2e=num(t_s12), value_as_printed=t_s12, unit_as_printed="tCO2e",
                     document=uba.relative_to(ROOT).as_posix(), pdf_page=37, printed_page="37", level_published=lvl,
                     coverage_published=f"{t_share}% of loan portfolio (p. 37)", coverage_share=int(t_share) / 100,
                     method_published=meth, borrower_scopes_published="Scopes 1 and 2 of borrowers"))
    return pd.DataFrame(rows)


def comparison() -> pd.DataFrame:
    pub = published()
    sens = pd.read_csv(PROCESSED / "financed_emissions_sensitivities.csv")
    by = sens[sens.row_type == "bank-year"].copy()
    by["year"] = by.year.astype(int)
    est = by.set_index(["bank", "year"])
    bank_year = pd.read_csv(PROCESSED / "financed_emissions_bank_year.csv").set_index(["bank", "year"])
    out = []
    for r in pub.itertuples():
        main = est.loc[(r.bank, r.year), "main"]
        s1 = est.loc[(r.bank, r.year), "S1"]
        lv = bank_year.loc[(r.bank, r.year)]
        cov = getattr(r, "coverage_share", float("nan"))
        rec = r._asdict()
        rec.pop("Index")
        rec.update(
            estimate_main_tco2e=main, estimate_main_level_basis=f"{lv.level}/{lv.basis}",
            estimate_bank_level_tco2e=s1,
            estimate_provisional=r.year == 2025,
            ratio_main_to_published=main / r.published_tco2e,
            ratio_bank_level_to_published=s1 / r.published_tco2e if not pd.isna(s1) else float("nan"),
            estimate_main_x_coverage_tco2e=main * cov if not pd.isna(cov) else float("nan"),
            ratio_coverage_matched_to_published=main * cov / r.published_tco2e if not pd.isna(cov) else float("nan"),
            estimate_scope="direct (production-based) emissions of borrowers' sectors: national inventory by sector / "
                           "sector value added; electricity emissions in the power sector only",
            method_differences=(
                "estimate: sector-average intensity per naira of value added x exposure (comparable in kind to PCAF "
                "data-quality score 5; no attribution factor; value added gives higher intensities than revenue-based "
                "factors); published: PCAF attribution with borrower or proxy data. Exposure basis of the estimate: "
                f"{lv.basis}; published coverage: {r.coverage_published}"
                + ("; estimate for 2025 is provisional (2024 intensities)" if r.year == 2025 else "")),
        )
        out.append(rec)
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# change over time, 2022 -> 2024 (LMDI-I additive)


def _L(a: float, b: float) -> float:
    if a == b:
        return a
    return (a - b) / (math.log(a) - math.log(b))


def lmdi(e0: pd.Series, f0: pd.Series, e1: pd.Series, f1: pd.Series) -> dict:
    """Additive LMDI-I over intensity groups. FE = E_total x share_g x I_g.
    Groups with zero financed emissions in both years (zero rule) drop out;
    a group present in one year only contributes its whole change to the mix
    effect (its intensity is defined, its share goes from or to zero)."""
    groups = sorted(set(e0.index) | set(e1.index))
    E0, E1 = e0.sum(), e1.sum()
    vol = mix = inten = 0.0
    for g in groups:
        a0, a1 = f0.get(g, 0.0), f1.get(g, 0.0)
        if a0 == 0 and a1 == 0:
            continue
        if a0 == 0 or a1 == 0:
            mix += a1 - a0
            continue
        w = _L(a1, a0)
        s0, s1 = e0[g] / E0, e1[g] / E1
        i0, i1 = a0 / e0[g], a1 / e1[g]
        vol += w * math.log(E1 / E0)
        mix += w * math.log(s1 / s0)
        inten += w * math.log(i1 / i0)
    return dict(exposure_volume_effect=vol, exposure_mix_effect=mix, exposure_effect=vol + mix,
                intensity_effect=inten, total_change=f1.sum() - f0.sum(), residual=f1.sum() - f0.sum() - vol - mix - inten)


def decomposition(y0: int = 2022, y1: int = 2024) -> pd.DataFrame:
    m = pd.read_csv(PROCESSED / "financed_emissions_main.csv")
    bank_year = pd.read_csv(PROCESSED / "financed_emissions_bank_year.csv")
    panel = sorted(bank_year[bank_year.in_balanced_panel].bank.unique())
    agg = m.groupby(["bank", "year", "intensity_group"]).agg(e=("exposure_naira", "sum"), f=("tco2e", "sum"))
    rows = []
    for unit in panel + ["(balanced panel total)"]:
        sub = agg if unit.startswith("(") else agg.loc[[unit]]
        if unit.startswith("("):
            sub = sub.loc[[b for b in panel]]
        g = sub.groupby(["year", "intensity_group"]).sum()
        r = lmdi(g.loc[y0].e, g.loc[y0].f, g.loc[y1].e, g.loc[y1].f)
        r.update(bank=unit, year_from=y0, year_to=y1, exposure_from=g.loc[y0].e.sum(), exposure_to=g.loc[y1].e.sum(),
                 tco2e_from=g.loc[y0].f.sum(), tco2e_to=g.loc[y1].f.sum())
        rows.append(r)
    cols = ["bank", "year_from", "year_to", "exposure_from", "exposure_to", "tco2e_from", "tco2e_to", "total_change",
            "exposure_effect", "exposure_volume_effect", "exposure_mix_effect", "intensity_effect", "residual"]
    return pd.DataFrame(rows)[cols]


# ---------------------------------------------------------------------------
# constant 2022 naira


def deflator() -> pd.DataFrame:
    cur = grab(NBS, 7, r"GDP Current Basic Price " + r" ".join([r"([\d,]+\.\d{2})"] * 6))
    con = grab(NBS, 8, r"GDP Constant Basic Price " + r" ".join([r"([\d,]+\.\d{2})"] * 6))
    years = list(range(2019, 2025))
    d = pd.DataFrame({"year": years, "gdp_current_basic_million": [num(x) for x in cur],
                      "gdp_constant_2019_basic_million": [num(x) for x in con]})
    d["deflator_2019_100"] = d.gdp_current_basic_million / d.gdp_constant_2019_basic_million * 100
    d["deflator_2022_1"] = d.deflator_2019_100 / d.set_index("year").loc[2022, "deflator_2019_100"]
    return d


def constant_naira() -> pd.DataFrame:
    """Loans in constant 2022 naira (implicit GDP deflator at basic prices,
    NBS PDF pp. 7-8), and financed emissions with constant-2022-naira exposures
    and 2022 intensities (descriptive; recorded addition)."""
    d = deflator().set_index("year")
    m = pd.read_csv(PROCESSED / "financed_emissions_main.csv")
    bank_year = pd.read_csv(PROCESSED / "financed_emissions_bank_year.csv")
    panel = set(bank_year[bank_year.in_balanced_panel].bank)
    i22 = (m[m.year == 2022].groupby("intensity_group").apply(
        lambda g: (g.tco2e.sum() / g.exposure_naira.sum()) if g.exposure_naira.sum() else 0.0))
    si = pd.read_csv(PROCESSED / "sector_intensity.csv")
    i22 = si[(si.spec == "main") & (si.year == 2022)].set_index("intensity_group").intensity_t_per_naira
    rows = []
    for ttype, sub in (("all available banks", m), ("balanced panel", m[m.bank.isin(panel)])):
        for y in PERIOD_YEARS:
            g = sub[sub.year == y]
            f = d.loc[y, "deflator_2022_1"]
            real = g.exposure_naira / f
            fe22 = (real * g.intensity_group.map(lambda t: 0.0 if t == ZERO_GROUP else i22[t])).sum()
            rows.append(dict(total_type=ttype, year=y, deflator_2022_1=f, exposure_nominal_naira=g.exposure_naira.sum(),
                             exposure_constant_2022_naira=real.sum(), tco2e_main=g.tco2e.sum(),
                             tco2e_constant_2022_naira_2022_intensity=fe22))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# share of national emissions


def national_share() -> pd.DataFrame:
    si = pd.read_csv(PROCESSED / "sector_intensity.csv")
    nat = si[(si.spec == "main") & (si.intensity_group == ECONOMY_WIDE)].set_index("year").emissions_t_co2e
    tot = pd.read_csv(PROCESSED / "financed_emissions_totals.csv")
    tot = tot[tot.year.isin(["2020", "2021", "2022"])].copy()
    tot["year"] = tot.year.astype(int)
    tot["national_without_lulucf_tco2e"] = tot.year.map(nat)
    tot["share_of_national"] = tot.tco2e / tot.national_without_lulucf_tco2e
    return tot[["total_type", "year", "n_banks", "tco2e", "national_without_lulucf_tco2e", "share_of_national"]]


def main() -> int:
    comp = comparison()
    comp.to_csv(PROCESSED / "published_comparison.csv", index=False)
    dec = decomposition()
    dec.to_csv(PROCESSED / "change_decomposition_2022_2024.csv", index=False)
    cn = constant_naira()
    cn.to_csv(PROCESSED / "constant_2022_naira.csv", index=False)
    deflator().to_csv(PROCESSED / "gdp_deflator_basic_prices.csv", index=False)
    ns = national_share()
    ns.to_csv(PROCESSED / "national_share.csv", index=False)
    pd.set_option("display.width", 250)
    print(comp[["bank", "year", "item", "published_tco2e", "estimate_main_tco2e", "ratio_main_to_published",
                "ratio_bank_level_to_published", "ratio_coverage_matched_to_published"]].to_string())
    print(dec.to_string())
    print(cn.to_string())
    print(ns.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
