"""Phase 2b: sector emission intensities (plan section 5) and the intensity
inputs of sensitivities S4, S5 and S6 (plan section 7).

Intensity(group, year) = emissions of the group's inventory categories (t CO2e)
/ NBS GDP of the group's activities at current basic prices (naira). Groups,
categories and activities come from the signed-off sector map
(data/processed/btr1_nbs_sector_map.csv). No financed emissions are computed.

Specifications written:
- main:   2020-2022 same-year BTR1 / same-year NBS; 2023-2024 Option A (2022
          emissions / that year's GDP); 2025 provisional = 2024 intensity,
          flagged and outside the period totals.
- S4_PIK: Option B for 2023-2024: each BTR1 2022 category extended with the
          growth of its IPCC top-level sector in the PIK series (Climate Watch
          API); 2020-2022 as main; 2025 provisional = S4 2024 intensity.
- S5_LULUCF: LULUCF (BTR1 category 4, net) added to agriculture; the
          economy-wide average then uses the national total with LULUCF.
- S6_ClimateWatch: Climate Watch sector emissions (source 'Climate Watch',
          all GHG) mapped to the groups, same GDP. The Climate Watch licence
          is not confirmed on an opened page (plan section 7), so S6 rows are
          written only to data/raw/derived/ (git-ignored), not to
          data/processed.

    python -m bank_emissions.phase2b_intensity
"""

from __future__ import annotations

import json

import pandas as pd

from .phase1b_extract import INTERIM, PROCESSED, ROOT
from .phase2a_crosswalk import AGRI, ECONOMY_WIDE, OIL_UP, POWER, REFINING, SERVICES, TRANSPORT, WATER
from .phase2a_sector_map import MCM, _codes, _nbs

YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
INVENTORY_LAST = 2022  # BTR1 ends in 2022
GDP_LAST = 2024  # NBS GDP by activity located to 2024 (2025 not located, Phase 2a)
RESIDENTIAL = "1.A.4.b"
TOTAL_WITHOUT = "Total CO2 equivalent emissions without LULUCF"
TOTAL_WITH = "Total CO2 equivalent emissions with LULUCF"
NBS_PAGE = 7
RAW_DERIVED = ROOT / "data" / "raw" / "derived"  # git-ignored (licence not confirmed)

PIK_FILE = ROOT / "data" / "raw" / "intensity" / "climatewatch_NGA_PIK_2026-11-03.json"
CW_FILE = ROOT / "data" / "raw" / "intensity" / "climatewatch_NGA_Climate Watch_2026-11-03.json"
# IPCC top-level sector of a BTR1 code, as named in the PIK series
PIK_TOP = {"1": "Energy", "2": "Industrial Processes and Product Use", "3": "Agriculture", "5": "Waste"}


# ---------------------------------------------------------------------------
# inputs


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    btr = pd.read_csv(PROCESSED / "btr1_emissions_by_category.csv")
    nbs = pd.read_csv(PROCESSED / "nbs_gdp_by_activity.csv")
    smap = pd.read_csv(PROCESSED / "btr1_nbs_sector_map.csv")
    return btr, nbs, smap


def groups(smap: pd.DataFrame) -> dict[str, dict]:
    """intensity group -> {'codes': [...], 'activities': [...]} from the sector map."""
    out: dict[str, dict] = {}
    rows = smap[(smap.row_type == "common sector") & (smap.common_sector != ECONOMY_WIDE)]
    for r in rows.itertuples():
        g = out.setdefault(r.intensity_group, {"codes": [], "activities": []})
        g["codes"] += [c for c in _codes(str(r.btr1_codes)) if c not in g["codes"]]
        g["activities"] += [a for a in _nbs(str(r.nbs_activities)) if a not in g["activities"]]
    return out


def emission_lookup(btr: pd.DataFrame) -> tuple[dict, dict, dict]:
    """(code, year) -> kt and source page. Table 2.10 values are used where the
    code is printed there (two decimals); NID values only for sub-categories
    that Table 2.10 does not print. Notation keys count as zero."""
    t210 = btr[btr.level == "Table 2.10"]
    nid = btr[btr.level == "NID sub-category"]
    val, page = {}, {}
    for r in nid.itertuples():
        val[(r.category_code, r.year)] = 0.0 if pd.isna(r.kt_co2e) else r.kt_co2e
        page[(r.category_code, r.year)] = f"NID {r.source.split(', ')[-1]} p. {r.pdf_page}"
    for r in t210.itertuples():
        if pd.isna(r.category_code):
            continue
        val[(r.category_code, r.year)] = 0.0 if pd.isna(r.kt_co2e) else r.kt_co2e
        page[(r.category_code, r.year)] = f"BTR1 Table 2.10 p. {r.pdf_page}"
    totals = {(r.category, r.year): r.kt_co2e for r in t210.itertuples() if pd.isna(r.category_code)}
    return val, page, totals


def gdp_lookup(nbs: pd.DataFrame) -> dict:
    return {(r.activity_no, r.year): r.gdp_current_basic_naira for r in nbs.itertuples()}


def pik_ratios() -> pd.DataFrame:
    """PIK (Kyoto GHG) growth of each IPCC top-level sector relative to 2022."""
    rows = json.loads(PIK_FILE.read_text(encoding="utf-8"))
    out = []
    for sector in PIK_TOP.values():
        r = next(x for x in rows if x["sector"] == sector and x["gas"] == "KYOTOGHG")
        v = {e["year"]: e["value"] for e in r["emissions"]}
        for y in (2023, 2024):
            out.append(dict(pik_sector=sector, year=y, ratio_to_2022=v[y] / v[2022],
                            pik_value_year=v[y], pik_value_2022=v[2022], unit=r["unit"]))
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# intensity table


def _row(spec, group, year, e_kt, gdp, e_year, g_year, method, e_src, g_src, provisional=False, flag=""):
    t = e_kt * 1000.0
    return dict(spec=spec, intensity_group=group, year=year, emissions_kt_co2e=e_kt, emissions_t_co2e=t,
                gdp_naira=gdp, intensity_t_per_naira=t / gdp if gdp else float("nan"),
                intensity_t_per_million_naira=t / gdp * 1e6 if gdp else float("nan"),
                emissions_year=e_year, gdp_year=g_year, method=method, provisional=provisional,
                in_period_totals=not provisional, emissions_source=e_src, gdp_source=g_src, flag=flag)


def _method(year: int, spec: str) -> str:
    if year <= INVENTORY_LAST:
        return "same-year emissions / same-year GDP"
    if year <= GDP_LAST:
        return ("Option B: 2022 emissions extended with PIK top-level growth / that year's GDP" if spec == "S4_PIK"
                else "Option A: 2022 emissions / that year's GDP")
    return "provisional: 2024 intensity (NBS 2025 GDP by activity not located)"


def build_table(spec: str, emissions_by_group, econ_emissions, gdp_by_group, gdp_total, sources) -> list[dict]:
    """emissions_by_group(group, emissions_year, target_year) -> kt; econ_emissions(year, target_year) -> kt."""
    rows = []
    for year in YEARS:
        if year <= INVENTORY_LAST:
            ey, gy = year, year
        elif year <= GDP_LAST:
            ey, gy = INVENTORY_LAST, year
        else:
            ey, gy = INVENTORY_LAST, GDP_LAST
        target = min(year, GDP_LAST)  # S4 extends emissions to the target year
        prov = year > GDP_LAST
        flag = ("provisional: carries the inflation bias of applying the 2024 per-naira intensity to 2025 "
                "nominal exposures (plan section 5); outside period totals and the balanced-panel trend" if prov else "")
        for g in sources["groups"]:
            e = emissions_by_group(g, ey, target)
            rows.append(_row(spec, g, year, e, gdp_by_group(g, gy), ey if spec != "S4_PIK" or year <= INVENTORY_LAST
                             else f"{ey} extended to {target}", gy, _method(year, spec),
                             sources["e_src"](g, ey), sources["g_src"](g, gy), prov, flag or sources["flag"](g)))
        e = econ_emissions(ey, target)
        rows.append(_row(spec, ECONOMY_WIDE, year, e, gdp_total(gy), ey if spec != "S4_PIK" or year <= INVENTORY_LAST
                         else f"{ey} extended to {target}", gy, _method(year, spec),
                         sources["econ_src"], f"NBS GDP at current basic prices, all 46 activities, {gy} (PDF p. {NBS_PAGE})",
                         prov, flag))
    return rows


def compute(btr=None, nbs=None, smap=None) -> dict[str, pd.DataFrame]:
    if btr is None:
        btr, nbs, smap = load_inputs()
    grp = groups(smap)
    val, page, totals = emission_lookup(btr)
    gdp = gdp_lookup(nbs)

    def g_gdp(g, y):
        return sum(gdp[(a, y)] for a in grp[g]["activities"])

    def total_gdp(y):
        return sum(v for (a, yy), v in gdp.items() if yy == y)

    def e_src(g, y):
        return "; ".join(f"{c} ({page.get((c, y), 'n/a')})" for c in grp[g]["codes"])

    def g_src(g, y):
        acts = grp[g]["activities"]
        return f"NBS activities {','.join(map(str, acts))}, {y} (PDF p. {NBS_PAGE})"

    base = dict(groups=list(grp), e_src=e_src, g_src=g_src, flag=lambda g: "",
                econ_src=f"BTR1 Table 2.10, {TOTAL_WITHOUT} (p. 62)")

    def e_main(g, ey, target):
        return sum(val.get((c, ey), 0.0) for c in grp[g]["codes"])

    def econ_main(ey, target):
        return totals[(TOTAL_WITHOUT, ey)]

    out = {"main": pd.DataFrame(build_table("main", e_main, econ_main, g_gdp, total_gdp, base))}

    # S4: Option B with PIK top-level growth
    pr = pik_ratios()
    ratio = {(r.pik_sector, r.year): r.ratio_to_2022 for r in pr.itertuples()}

    def ext(code, ey, target):
        v = val.get((code, ey), 0.0)
        if ey < INVENTORY_LAST or target <= INVENTORY_LAST:
            return v
        return v * ratio[(PIK_TOP[code[0]], target)]

    def e_s4(g, ey, target):
        return sum(ext(c, ey, target) for c in grp[g]["codes"])

    def econ_s4(ey, target):
        if target <= INVENTORY_LAST:
            return totals[(TOTAL_WITHOUT, ey)]
        return sum(ext(c, ey, target) for c in ["1", "2", "3", "5"])  # 6 'Other' is not estimated (FX)

    out["S4_PIK"] = pd.DataFrame(build_table("S4_PIK", e_s4, econ_s4, g_gdp, total_gdp, dict(
        base, econ_src="BTR1 Table 2.10 categories 1, 2, 3, 5 (2022) x PIK top-level growth")))

    # S5: LULUCF added to agriculture; economy-wide with LULUCF
    def e_s5(g, ey, target):
        return e_main(g, ey, target) + (val.get(("4", ey), 0.0) if g == AGRI else 0.0)

    def econ_s5(ey, target):
        return totals[(TOTAL_WITH, ey)]

    out["S5_LULUCF"] = pd.DataFrame(build_table("S5_LULUCF", e_s5, econ_s5, g_gdp, total_gdp, dict(
        base, econ_src=f"BTR1 Table 2.10, {TOTAL_WITH} (p. 62)",
        e_src=lambda g, y: e_src(g, y) + ("; 4 LULUCF (BTR1 Table 2.10 p. 61)" if g == AGRI else ""))))

    # S6: Climate Watch sectors
    cw, cw_map = climate_watch(btr)
    s6_flag = {REFINING: "no Climate Watch counterpart: BTR1 refining emissions retained",
               SERVICES: "Climate Watch 'Building' x BTR1 commercial share of 1.A.4 (a / (a + b)) of the same year"}

    def e_s6(g, ey, target):
        if g == REFINING:
            return e_main(g, ey, target)
        return cw_map(g, ey)

    def econ_s6(ey, target):
        return cw[("Total excluding LULUCF", ey)]

    out["S6_ClimateWatch"] = pd.DataFrame(build_table("S6_ClimateWatch", e_s6, econ_s6, g_gdp, total_gdp, dict(
        base, flag=lambda g: s6_flag.get(g, ""),
        e_src=lambda g, y: S6_SOURCES.get(g, "") if g != REFINING else e_src(g, y),
        econ_src="Climate Watch 'Total excluding LULUCF', all GHG (API, source 'Climate Watch')")))
    out["pik_ratios"] = pr
    return out


# Climate Watch sector -> intensity group (S6). Mapped at the level of detail the
# Climate Watch sectors allow (plan section 7).
S6_MAP = {
    "Agriculture": AGRI, "Other Fuel Combustion": AGRI,
    "Electricity/Heat": POWER,
    "Fugitive Emissions": OIL_UP,
    "Manufacturing/Construction": MCM, "Industrial Processes": MCM,
    "Transportation": TRANSPORT,
    "Waste": WATER,
    "Building": SERVICES,  # commercial share only; the residential share is not attributed
}
S6_SOURCES = {g: "Climate Watch (API, source 'Climate Watch', all GHG): "
                 + ", ".join(k for k, v in S6_MAP.items() if v == g) for g in set(S6_MAP.values())}


def climate_watch(btr: pd.DataFrame):
    rows = json.loads(CW_FILE.read_text(encoding="utf-8"))
    cw = {}
    for r in rows:
        if r["gas"] != "All GHG":
            continue
        for e in r["emissions"]:
            cw[(r["sector"], e["year"])] = e["value"] * 1000.0  # Mt -> kt
    val, _, _ = emission_lookup(btr)

    def commercial_share(y):
        a, b = val[("1.A.4.a", y)], val[(RESIDENTIAL, y)]
        return a / (a + b)

    def cw_map(g, y):
        tot = 0.0
        for sector, grp in S6_MAP.items():
            if grp != g:
                continue
            v = cw[(sector, y)]
            tot += v * commercial_share(y) if sector == "Building" else v
        return tot

    cw_map.commercial_share = commercial_share
    cw_map.cw = cw
    return cw, cw_map


# ---------------------------------------------------------------------------
# independent recomputation and checks


def recompute(btr: pd.DataFrame, nbs: pd.DataFrame, smap: pd.DataFrame) -> pd.DataFrame:
    """Main-specification intensities recomputed by a separate path: emissions
    by direct filtering of the input CSV, GDP by direct filtering of the NBS
    CSV, year rule written out explicitly."""
    t210 = btr[btr.level == "Table 2.10"].dropna(subset=["category_code"])
    nid = btr[btr.level == "NID sub-category"]
    out = []
    rows = smap[smap.row_type == "common sector"]
    for g, gr in rows.groupby("intensity_group"):
        codes = sorted({c for s in gr.btr1_codes for c in _codes(str(s))}) if g != ECONOMY_WIDE else []
        acts = sorted({a for s in gr.nbs_activities for a in _nbs(str(s))})
        for year in YEARS:
            ey = year if year <= 2022 else 2022
            gy = year if year <= 2024 else 2024
            if g == ECONOMY_WIDE:
                e = btr[(btr.category == TOTAL_WITHOUT) & (btr.year == ey)].kt_co2e.iloc[0]
            else:
                e = 0.0
                for c in codes:
                    hit = t210[(t210.category_code == c) & (t210.year == ey)]
                    if hit.empty:
                        hit = nid[(nid.category_code == c) & (nid.year == ey)]
                    e += 0.0 if pd.isna(hit.kt_co2e.iloc[0]) else hit.kt_co2e.iloc[0]
            gdp = nbs[(nbs.year == gy) & nbs.activity_no.isin(acts)].gdp_current_basic_naira.sum()
            out.append(dict(intensity_group=g, year=year, recomputed_t_per_naira=e * 1000.0 / gdp))
    return pd.DataFrame(out)


def checks(res: dict[str, pd.DataFrame], btr, nbs, smap) -> pd.DataFrame:
    out = []
    main = res["main"]
    rc = recompute(btr, nbs, smap).merge(main, on=["intensity_group", "year"])
    import numpy as np

    same = np.isclose(rc.recomputed_t_per_naira, rc.intensity_t_per_naira, rtol=1e-12, atol=0.0)
    worst = (rc.recomputed_t_per_naira - rc.intensity_t_per_naira).abs().max()
    out.append(dict(check="recompute_main", spec="main", year="", result="pass" if same.all() else "fail",
                    detail=f"{len(rc)} intensities recomputed by a separate function; {int(same.sum())} identical "
                           f"within 1e-12 relative (zero values compared exactly); largest absolute difference "
                           f"{worst:.1e} t per naira"))
    val, _, totals = emission_lookup(btr)
    for spec, df in res.items():
        if spec == "pik_ratios":
            continue
        for year in YEARS:
            d = df[df.year == year]
            grp = d[d.intensity_group != ECONOMY_WIDE]
            econ = d[d.intensity_group == ECONOMY_WIDE].iloc[0]
            ey = min(year, INVENTORY_LAST)
            # residential (unattributed) in the same specification
            if spec == "S6_ClimateWatch":
                cw, cw_map = climate_watch(btr)
                resid = cw[("Building", ey)] * (1 - cw_map.commercial_share(ey))
                assigned = grp[grp.intensity_group != REFINING].emissions_kt_co2e.sum()
                note = " (refining excluded: BTR1 value retained, no Climate Watch counterpart)"
            elif spec == "S4_PIK" and year > INVENTORY_LAST:
                pr = res["pik_ratios"]
                r = pr[(pr.pik_sector == "Energy") & (pr.year == min(year, GDP_LAST))].ratio_to_2022.iloc[0]
                resid = val[(RESIDENTIAL, ey)] * r
                assigned = grp.emissions_kt_co2e.sum()
                note = ""
            else:
                resid = val[(RESIDENTIAL, ey)]
                assigned = grp.emissions_kt_co2e.sum()
                note = ""
            total = econ.emissions_kt_co2e
            if spec == "S6_ClimateWatch":
                # Climate Watch publishes Mt to two decimals (10 kt): 5 kt per summed term
                # (9 sector terms) and 5 kt for the published total
                tol = 5.0 * 10
            else:
                # NID sub-categories are whole kt: allow 0.5 kt per NID term used (9 terms)
                tol = 0.5 * 9 + 0.01
            diff = assigned + resid - total
            out.append(dict(check="assigned_plus_residential_equals_national", spec=spec, year=year,
                            result="pass" if abs(diff) <= tol else "fail",
                            detail=f"assigned {assigned:,.2f} + residential {resid:,.2f} = {assigned + resid:,.2f} kt vs "
                                   f"national {total:,.2f} kt (diff {diff:,.2f}; tolerance {tol:.2f} kt, "
                                   f"{'Climate Watch 0.01 Mt' if spec == 'S6_ClimateWatch' else 'NID whole-kt'} "
                                   f"rounding){note}"))
            gdp_tot = grp.gdp_naira.sum()
            out.append(dict(check="groups_gdp_equals_total", spec=spec, year=year,
                            result="pass" if abs(gdp_tot / econ.gdp_naira - 1) < 1e-12 else "fail",
                            detail=f"group GDP {gdp_tot:,.0f} vs total {econ.gdp_naira:,.0f}"))
            if spec == "S6_ClimateWatch":
                continue
            wavg = (grp.intensity_t_per_naira * grp.gdp_naira).sum() / gdp_tot
            gap = resid * 1000.0 / econ.gdp_naira
            out.append(dict(check="gdp_weighted_average_vs_economy_wide", spec=spec, year=year, result="info",
                            detail=f"GDP-weighted average of group intensities {wavg * 1e6:.4f} vs economy-wide "
                                   f"{econ.intensity_t_per_naira * 1e6:.4f} t per million naira; difference "
                                   f"{(econ.intensity_t_per_naira - wavg) * 1e6:.4f} = unattributed residential "
                                   f"combustion / total GDP ({gap * 1e6:.4f})"))
            lhs = wavg + gap
            rel = abs(lhs / econ.intensity_t_per_naira - 1)
            out.append(dict(check="weighted_average_plus_residential_equals_economy_wide", spec=spec, year=year,
                            result="pass" if rel < 5e-5 else "fail",
                            detail=f"{lhs * 1e6:.6f} vs {econ.intensity_t_per_naira * 1e6:.6f} t per million naira "
                                   f"(relative difference {rel:.1e}; NID whole-kt rounding)"))
    return pd.DataFrame(out)


COLUMNS = ["spec", "intensity_group", "year", "emissions_kt_co2e", "emissions_t_co2e", "gdp_naira",
           "intensity_t_per_naira", "intensity_t_per_million_naira", "emissions_year", "gdp_year", "method",
           "provisional", "in_period_totals", "emissions_source", "gdp_source", "flag"]


def main() -> int:
    btr, nbs, smap = load_inputs()
    res = compute(btr, nbs, smap)
    ch = checks(res, btr, nbs, smap)
    committed = pd.concat([res[s] for s in ("main", "S4_PIK", "S5_LULUCF")], ignore_index=True)[COLUMNS]
    committed.to_csv(PROCESSED / "sector_intensity.csv", index=False)
    pr = res["pik_ratios"][["pik_sector", "year", "ratio_to_2022"]]
    pr.to_csv(INTERIM / "pik_growth_ratios.csv", index=False)
    RAW_DERIVED.mkdir(parents=True, exist_ok=True)
    res["S6_ClimateWatch"][COLUMNS].to_csv(RAW_DERIVED / "sector_intensity_s6_climatewatch.csv", index=False)
    # the S6 checks are written without Climate Watch values (pass/fail only)
    s6 = ch.spec == "S6_ClimateWatch"
    ch.loc[s6, "detail"] = "values not committed (Climate Watch licence not confirmed); see data/raw/derived/"
    ch.to_csv(INTERIM / "intensity_checks.csv", index=False)
    full = checks(res, btr, nbs, smap)
    full[full.spec == "S6_ClimateWatch"].to_csv(RAW_DERIVED / "intensity_checks_s6.csv", index=False)
    print(f"{len(committed)} committed rows; checks: {ch.result.value_counts().to_dict()}")
    bad = full[full.result == "fail"]
    if len(bad):
        print(bad.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
