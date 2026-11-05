"""Phase 3: financed-emissions estimation (plan sections 6 and 7).

financed emissions (bank, year, line) = exposure (naira) x intensity (t CO2e per
naira) of the line's target intensity group in that year.

Inputs (all read-only): exposures_by_sector.csv (Phase 1b), sector_crosswalk.csv
and sector_crosswalk_splits.csv (Phase 2a, signed off), btr1_nbs_sector_map.csv
(Phase 2a), sector_intensity.csv (Phase 2b), and for S6 the git-ignored
data/raw/derived/sector_intensity_s6_climatewatch.csv (Phase 2b).

Each exposure row is expanded into lines: one line for an unsplit label, one
line per component (with its share) for a split label. A line's target is the
intensity group of its common sector ('mapped'), the services group (services
rule), the economy-wide average (economy-wide rule) or zero (zero rule, not a
loan). Sensitivities change one element: the target of tagged lines (S3a-S3l),
the exposure set (S1 level, S2 basis) or the intensity table (S4, S5, S6).

Outputs:
- data/processed/financed_emissions_main.csv            line level, main specification
- data/processed/financed_emissions_bank_year.csv       totals by bank-year
- data/processed/financed_emissions_totals.csv          totals by year: all available banks; balanced panel
- data/processed/financed_emissions_sector_year.csv     by reporting sector and year, with shares
- data/processed/financed_emissions_bank_sector.csv     by bank-year and reporting sector, with shares
- data/processed/financed_emissions_sensitivities.csv   by bank-year (and totals): main, every
                                                        sensitivity, min/max and the sensitivity setting each
- data/interim/estimation_checks.csv, sensitivity_flags.csv

    python -m bank_emissions.phase3_estimate
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .phase1b_extract import INTERIM, PROCESSED, ROOT
from .phase2a_crosswalk import (AGRI, CONSTR, ECONOMY_WIDE, MANUF, MINING, NOT_LOAN, OIL_UP, POWER, REFINING,
                                SERVICES, TRANSPORT, WATER, ZERO)
from .phase2a_sector_map import MCM

YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
PROVISIONAL = {2025}
PERIOD_YEARS = [y for y in YEARS if y not in PROVISIONAL]
ZERO_GROUP = "(zero)"
S6_FILE = ROOT / "data" / "raw" / "derived" / "sector_intensity_s6_climatewatch.csv"

GROUP_OF = {AGRI: AGRI, OIL_UP: OIL_UP, REFINING: REFINING, POWER: POWER, MANUF: MCM, CONSTR: MCM, MINING: MCM,
            TRANSPORT: TRANSPORT, WATER: WATER, SERVICES: SERVICES}

# reporting sector for shares (RQ2): common sectors, plus the rule categories
REPORTING = {"economy-wide": "Other (economy-wide average rule)", "zero": "Individuals and other zero-rule",
             "not a loan": "Not a loan exposure"}

SENSITIVITIES = ["S1", "S2", "S3a", "S3b", "S3c", "S3d", "S3e", "S3f", "S3g", "S3h", "S3i", "S3j", "S3k", "S3l",
                 "S4", "S5", "S6"]
SENS_DESC = {
    "S1": "bank (Nigeria) level where a bank-level table is printed",
    "S2": "carrying amount where printed at the main level",
    "S3a": "commerce and trade: economy-wide average instead of services",
    "S3b": "'Other' and product labels: zero instead of economy-wide",
    "S3c": "individuals and retail: economy-wide instead of zero",
    "S3d": "government: zero instead of services",
    "S3e": "finance and insurance: zero instead of services",
    "S3f": "Access 2025 residual: services (target of Access downstream)",
    "S3g": "undivided oil and gas: all upstream",
    "S3h": "undivided oil and gas: all downstream (services, commerce rule)",
    "S3i": "oil and gas services: upstream",
    "S3j": "oil and gas downstream: oil refining",
    "S3k": "combined categories: single mapping (construction; transport)",
    "S3l": "Stanbic 'Mining': non-oil mining",
    "S4": "2023-2024 intensities: Option B (PIK growth)",
    "S5": "LULUCF added to agriculture (economy-wide with LULUCF)",
    "S6": "Climate Watch sector emissions",
}
# S3 tag -> new target for tagged lines
S3_TARGET = {"S3a": ECONOMY_WIDE, "S3b": ZERO_GROUP, "S3c": ECONOMY_WIDE, "S3d": ZERO_GROUP, "S3e": ZERO_GROUP,
             "S3f": SERVICES, "S3g": OIL_UP, "S3h": SERVICES, "S3i": OIL_UP, "S3j": REFINING, "S3l": MCM}
S3K_TARGET = {"infotelecomsandtransport": TRANSPORT}  # other S3k keys (construction and real estate) -> MCM


# ---------------------------------------------------------------------------
# inputs


def load() -> dict:
    d = dict(
        exp=pd.read_csv(PROCESSED / "exposures_by_sector.csv"),
        cw=pd.read_csv(PROCESSED / "sector_crosswalk.csv", keep_default_na=False),
        splits=pd.read_csv(PROCESSED / "sector_crosswalk_splits.csv", keep_default_na=False),
        si=pd.read_csv(PROCESSED / "sector_intensity.csv"),
        sample=pd.read_csv(PROCESSED / "sample.csv"),
    )
    d["s6"] = pd.read_csv(S6_FILE) if S6_FILE.exists() else None
    return d


def intensity_table(si: pd.DataFrame, spec: str) -> dict:
    t = si[si.spec == spec]
    return {(r.intensity_group, r.year): r.intensity_t_per_naira for r in t.itertuples()}


def target_of(rule: str, common_sector: str) -> str:
    if rule == "mapped":
        return GROUP_OF[common_sector]
    if rule == "services":
        return SERVICES
    if rule == "economy-wide":
        return ECONOMY_WIDE
    return ZERO_GROUP  # zero, not a loan


def reporting_sector(rule: str, common_sector: str) -> str:
    return REPORTING.get(rule, common_sector)


def _tags(*s: str) -> set:
    return {t for x in s for t in str(x).split(";") if t}


def expand(rows: pd.DataFrame, cw: pd.DataFrame, splits: pd.DataFrame) -> pd.DataFrame:
    """Exposure rows -> lines (one per row, or one per split component)."""
    cwi = cw.set_index(["bank", "printed_category"])
    spl = {k: g for k, g in splits.groupby(["bank", "printed_category", "year"])}
    out = []
    for r in rows.itertuples():
        c = cwi.loc[(r.bank, r.printed_category)]
        base = dict(bank=r.bank, year=int(r.year), level=r.level, basis=r.basis, printed_category=r.printed_category,
                    label_key=c.label_key, row_tags=c.sensitivity_group, source_role=r.source_role,
                    exposure_row_naira=r.amount_naira)
        if c.rule == "split":
            for s in spl[(r.bank, r.printed_category, int(r.year))].itertuples():
                out.append(dict(base, component=s.component, share=s.share, rule=s.rule, common_sector=s.common_sector,
                                comp_tags=s.sensitivity_group, exposure_naira=r.amount_naira * s.share))
        else:
            out.append(dict(base, component="", share=1.0, rule=c.rule, common_sector=c.common_sector,
                            comp_tags="", exposure_naira=r.amount_naira))
    lines = pd.DataFrame(out)
    lines["target"] = [target_of(r, s) for r, s in zip(lines.rule, lines.common_sector)]
    lines["reporting_sector"] = [reporting_sector(r, s) for r, s in zip(lines.rule, lines.common_sector)]
    lines["tags"] = [_tags(a, b) for a, b in zip(lines.row_tags, lines.comp_tags)]
    return lines


def apply_intensity(lines: pd.DataFrame, table: dict) -> pd.DataFrame:
    lines = lines.copy()
    lines["intensity_t_per_naira"] = [0.0 if t == ZERO_GROUP else table[(t, y)]
                                      for t, y in zip(lines.target, lines.year)]
    lines["tco2e"] = lines.exposure_naira * lines.intensity_t_per_naira
    return lines


# ---------------------------------------------------------------------------
# exposure sets


def main_rows(exp: pd.DataFrame) -> pd.DataFrame:
    return exp[exp.main_spec]


def s1_rows(exp: pd.DataFrame) -> pd.DataFrame:
    """Bank (Nigeria) level: gross where printed, else carrying. Bank-years
    whose main specification is already bank level keep their main rows."""
    m = main_rows(exp)
    out = []
    for (b, y), g in m.groupby(["bank", "year"]):
        if (g.level == "bank").all():
            out.append(g)
            continue
        alt = exp[(exp.bank == b) & (exp.year == y) & (exp.level == "bank") & (exp.source_role == "extracted")]
        if alt.empty:
            continue
        basis = "gross" if (alt.basis == "gross").any() else "carrying"
        out.append(alt[alt.basis == basis])
    return pd.concat(out, ignore_index=True)


def s2_rows(exp: pd.DataFrame) -> pd.DataFrame:
    """Carrying amount at the main level where printed; bank-years whose main
    basis is already carrying keep their main rows."""
    m = main_rows(exp)
    out = []
    for (b, y), g in m.groupby(["bank", "year"]):
        if (g.basis == "carrying").all():
            out.append(g)
            continue
        lv = g.level.iloc[0]
        alt = exp[(exp.bank == b) & (exp.year == y) & (exp.level == lv) & (exp.basis == "carrying")
                  & (exp.source_role == "extracted")]
        if not alt.empty:
            out.append(alt)
    return pd.concat(out, ignore_index=True)


# ---------------------------------------------------------------------------
# sensitivities


def retarget(lines: pd.DataFrame, tag: str) -> pd.DataFrame:
    lines = lines.copy()
    hit = lines.tags.map(lambda t: tag in t)
    if tag == "S3k":
        lines.loc[hit, "target"] = [S3K_TARGET.get(k, MCM) for k in lines.loc[hit, "label_key"]]
    else:
        lines.loc[hit, "target"] = S3_TARGET[tag]
    return lines


def by_bank_year(lines: pd.DataFrame) -> pd.Series:
    return lines.groupby(["bank", "year"]).tco2e.sum()


def run_sensitivities(d: dict, main_lines: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Returns bank-year values per sensitivity (NaN where not applicable) and
    the line tables used (for decomposition)."""
    exp, cw, splits, si = d["exp"], d["cw"], d["splits"], d["si"]
    main_tab = intensity_table(si, "main")
    res, used = {}, {}
    for s in SENSITIVITIES:
        if s == "S1":
            ln = apply_intensity(expand(s1_rows(exp), cw, splits), main_tab)
        elif s == "S2":
            ln = apply_intensity(expand(s2_rows(exp), cw, splits), main_tab)
        elif s in ("S4", "S5"):
            ln = apply_intensity(main_lines, intensity_table(si, {"S4": "S4_PIK", "S5": "S5_LULUCF"}[s]))
        elif s == "S6":
            if d["s6"] is None:
                continue
            ln = apply_intensity(main_lines, intensity_table(d["s6"], "S6_ClimateWatch"))
        else:
            ln = apply_intensity(retarget(main_lines, s), main_tab)
        res[s] = by_bank_year(ln)
        used[s] = ln
    return pd.DataFrame(res), used


def applicability(main_lines: pd.DataFrame, sens: pd.DataFrame) -> pd.DataFrame:
    """A sensitivity applies to a bank-year if it has a value there and, for the
    S3 rules, the bank-year has a tagged line; S4 applies to 2023 onwards."""
    app = pd.DataFrame(index=sens.index)
    tagged = main_lines.groupby(["bank", "year"]).tags.apply(lambda ts: set().union(*ts))
    for s in sens.columns:
        if s.startswith("S3"):
            app[s] = [s in tagged.get(i, set()) for i in sens.index]
        elif s == "S4":
            app[s] = [i[1] >= 2023 for i in sens.index]
        else:
            app[s] = sens[s].notna()
    return app


# ---------------------------------------------------------------------------
# decomposition flags (refining, water and waste)


def driver_flags(main_lines: pd.DataFrame, used: dict, sens: pd.DataFrame, app: pd.DataFrame) -> pd.DataFrame:
    """For each sensitivity and bank-year, the share of the change against the
    main value that comes from lines targeted at oil refining or at water and
    waste (in either version). Flagged when that share is 50% or more."""
    rows = []
    main_by = main_lines.groupby(["bank", "year", "target"]).tco2e.sum()
    for s, ln in used.items():
        alt_by = ln.groupby(["bank", "year", "target"]).tco2e.sum()
        for (b, y) in sens.index:
            if not app.loc[(b, y), s]:
                continue
            total_delta = sens.loc[(b, y), s] - sens.loc[(b, y), "main"]
            if abs(total_delta) < 1e-6:
                continue
            for grp, name in ((REFINING, "oil refining"), (WATER, "water and waste")):
                d_grp = alt_by.get((b, y, grp), 0.0) - main_by.get((b, y, grp), 0.0)
                share = d_grp / total_delta
                if abs(share) >= 0.5:
                    rows.append(dict(sensitivity=s, bank=b, year=y, driver=name, change_tco2e=total_delta,
                                     change_from_driver_tco2e=d_grp, share_of_change=share))
    return pd.DataFrame(rows, columns=["sensitivity", "bank", "year", "driver", "change_tco2e",
                                       "change_from_driver_tco2e", "share_of_change"])


# ---------------------------------------------------------------------------
# totals


def balanced_banks(bank_year: pd.DataFrame) -> list[str]:
    have = bank_year.groupby("bank").year.apply(set)
    return sorted(b for b, ys in have.items() if set(YEARS) <= ys)


def totals(bank_year: pd.DataFrame, value_cols: list[str]) -> pd.DataFrame:
    bal = balanced_banks(bank_year)
    rows = []
    for ttype, sub in (("all available banks", bank_year), ("balanced panel", bank_year[bank_year.bank.isin(bal)])):
        for y in YEARS:
            g = sub[sub.year == y]
            rows.append(dict(total_type=ttype, year=str(y), n_banks=g.bank.nunique(), provisional=y in PROVISIONAL,
                             banks=";".join(sorted(g.bank.unique())), **{c: g[c].sum() for c in value_cols}))
        g = sub[sub.year.isin(PERIOD_YEARS)]
        rows.append(dict(total_type=ttype, year=f"{PERIOD_YEARS[0]}-{PERIOD_YEARS[-1]}", n_banks=g.bank.nunique(),
                         provisional=False, banks="", **{c: g[c].sum() for c in value_cols}))
    return pd.DataFrame(rows)


def sector_tables(lines: pd.DataFrame, bal: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    bs = lines.groupby(["bank", "year", "reporting_sector"]).agg(exposure_naira=("exposure_naira", "sum"),
                                                                 tco2e=("tco2e", "sum")).reset_index()
    bs["share_of_bank_year_tco2e"] = bs.tco2e / bs.groupby(["bank", "year"]).tco2e.transform("sum")
    bs["provisional"] = bs.year.isin(PROVISIONAL)
    rows = []
    for ttype, sub in (("all available banks", lines), ("balanced panel", lines[lines.bank.isin(bal)])):
        g = sub.groupby(["year", "reporting_sector"]).agg(exposure_naira=("exposure_naira", "sum"),
                                                          tco2e=("tco2e", "sum")).reset_index()
        g["share_of_year_tco2e"] = g.tco2e / g.groupby("year").tco2e.transform("sum")
        g.insert(0, "total_type", ttype)
        g["provisional"] = g.year.isin(PROVISIONAL)
        rows.append(g)
    return bs, pd.concat(rows, ignore_index=True)


# ---------------------------------------------------------------------------
# independent recomputation and checks


def recompute_bank_year(d: dict) -> pd.Series:
    """Main-specification bank-year totals by a separate path: loop over the
    main-spec rows, look up the crosswalk and splits directly, and read the
    intensity from the CSV for each line."""
    exp, cw, splits, si = d["exp"], d["cw"], d["splits"], d["si"]
    smap = pd.read_csv(PROCESSED / "btr1_nbs_sector_map.csv")
    group_of = dict(zip(smap.common_sector.fillna(""), smap.intensity_group.fillna("")))
    inten = si[si.spec == "main"].set_index(["intensity_group", "year"]).intensity_t_per_naira

    def i_of(rule, sector, year):
        if rule in ("zero", "not a loan"):
            return 0.0
        if rule == "economy-wide":
            return inten[(ECONOMY_WIDE, year)]
        if rule == "services":
            return inten[(SERVICES, year)]
        return inten[(group_of[sector], year)]

    total: dict = {}
    for r in exp[exp.main_spec].itertuples():
        c = cw[(cw.bank == r.bank) & (cw.printed_category == r.printed_category)].iloc[0]
        if c.rule == "split":
            comp = splits[(splits.bank == r.bank) & (splits.printed_category == r.printed_category)
                          & (splits.year == r.year)]
            v = sum(r.amount_naira * s.share * i_of(s.rule, s.common_sector, r.year) for s in comp.itertuples())
        else:
            v = r.amount_naira * i_of(c.rule, c.common_sector, r.year)
        total[(r.bank, int(r.year))] = total.get((r.bank, int(r.year)), 0.0) + v
    return pd.Series(total)


def checks(d: dict, lines: pd.DataFrame, bank_year: pd.DataFrame, bank_sector: pd.DataFrame,
           sector_year: pd.DataFrame) -> pd.DataFrame:
    out = []
    rc = recompute_bank_year(d)
    by = bank_year.set_index(["bank", "year"]).tco2e
    same = np.isclose(rc.reindex(by.index), by, rtol=1e-12, atol=0.0)
    out.append(dict(check="recompute_bank_year", item="all", result="pass" if same.all() else "fail",
                    detail=f"{int(same.sum())}/{len(by)} bank-years identical within 1e-12 (separate function)"))
    s = d["sample"].set_index(["bank", "year"]).main_total_naira
    ex = bank_year.set_index(["bank", "year"]).exposure_naira
    diff = (ex - s.reindex(ex.index)).abs() / s.reindex(ex.index)
    out.append(dict(check="exposure_equals_phase1b_total", item="all", result="pass" if (diff < 1e-12).all() else "fail",
                    detail=f"{int((diff < 1e-12).sum())}/{len(ex)} bank-years: expanded exposure equals the Phase 1b "
                           f"main-specification total (sample.csv); largest relative difference {diff.max():.1e}"))
    missing = set(s[s.notna()].index) - set(ex.index)
    out.append(dict(check="every_included_bank_year_estimated", item="all", result="pass" if not missing else "fail",
                    detail=f"{len(ex)} bank-years estimated; missing: {sorted(missing)}"))
    sh = bank_sector.groupby(["bank", "year"]).share_of_bank_year_tco2e.sum()
    out.append(dict(check="bank_year_sector_shares_sum_to_1", item="all",
                    result="pass" if ((sh - 1).abs() < 1e-12).all() else "fail",
                    detail=f"{len(sh)} bank-years; largest deviation {(sh - 1).abs().max():.1e}"))
    sy = sector_year.groupby(["total_type", "year"]).share_of_year_tco2e.sum()
    out.append(dict(check="year_sector_shares_sum_to_1", item="all",
                    result="pass" if ((sy - 1).abs() < 1e-12).all() else "fail",
                    detail=f"{len(sy)} total-type years; largest deviation {(sy - 1).abs().max():.1e}"))
    neg = (lines.tco2e < 0).sum()
    out.append(dict(check="no_negative_line_values", item="all", result="pass" if neg == 0 else "fail",
                    detail=f"{neg} negative lines"))
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------


def main() -> int:
    d = load()
    main_lines = apply_intensity(expand(main_rows(d["exp"]), d["cw"], d["splits"]), intensity_table(d["si"], "main"))
    main_lines["provisional"] = main_lines.year.isin(PROVISIONAL)
    out_main = main_lines[["bank", "year", "level", "basis", "printed_category", "component", "share", "rule",
                           "common_sector", "target", "reporting_sector", "exposure_row_naira", "exposure_naira",
                           "intensity_t_per_naira", "tco2e", "provisional", "source_role"]].rename(
        columns={"target": "intensity_group"})
    bank_year = main_lines.groupby(["bank", "year"]).agg(level=("level", "first"), basis=("basis", "first"),
                                                         exposure_naira=("exposure_naira", "sum"),
                                                         tco2e=("tco2e", "sum")).reset_index()
    bal = balanced_banks(bank_year)
    bank_year["provisional"] = bank_year.year.isin(PROVISIONAL)
    bank_year["in_balanced_panel"] = bank_year.bank.isin(bal)
    tot = totals(bank_year, ["exposure_naira", "tco2e"])
    bank_sector, sector_year = sector_tables(main_lines, bal)

    sens, used = run_sensitivities(d, main_lines)
    sens.insert(0, "main", by_bank_year(main_lines))
    app = applicability(main_lines, sens[[c for c in sens.columns if c != "main"]])
    vals = sens.copy()
    for s in app.columns:
        vals.loc[~app[s], s] = np.nan
    sc = [c for c in vals.columns if c != "main"]
    vals["min"] = vals[sc].min(axis=1)
    vals["min_sensitivity"] = vals[sc].idxmin(axis=1)
    vals["max"] = vals[sc].max(axis=1)
    vals["max_sensitivity"] = vals[sc].idxmax(axis=1)
    flags = driver_flags(main_lines, used, sens, app)
    fl = flags.groupby(["bank", "year"]).apply(
        lambda g: "; ".join(f"{r.sensitivity}: {r.driver} ({r.share_of_change:.0%} of change)" for r in g.itertuples()))
    vals["driver_flags"] = [fl.get(i, "") for i in vals.index]
    vals = vals.reset_index().rename(columns={"level_0": "bank", "level_1": "year"})
    vals.insert(0, "row_type", "bank-year")
    vals["provisional"] = vals.year.isin(PROVISIONAL)
    # totals per sensitivity (all available banks; balanced panel), main-spec bank set; NaN -> main
    filled = sens.copy()
    for s in app.columns:
        filled.loc[~app[s], s] = filled.loc[~app[s], "main"]
    filled = filled.reset_index().rename(columns={"level_0": "bank", "level_1": "year"})
    trows = []
    for ttype, sub in (("total: all available banks", filled), ("total: balanced panel", filled[filled.bank.isin(bal)])):
        for y in YEARS + ["2020-2024"]:
            g = sub[sub.year.isin(PERIOD_YEARS)] if y == "2020-2024" else sub[sub.year == y]
            r = dict(row_type=ttype, bank="", year=y, provisional=y in PROVISIONAL,
                     **{c: g[c].sum() for c in ["main"] + sc})
            v = pd.Series({c: r[c] for c in sc})
            r.update(min=v.min(), min_sensitivity=v.idxmin(), max=v.max(), max_sensitivity=v.idxmax(), driver_flags="")
            trows.append(r)
    sens_out = pd.concat([vals, pd.DataFrame(trows)], ignore_index=True)

    ch = checks(d, main_lines, bank_year, bank_sector, sector_year)
    out_main.to_csv(PROCESSED / "financed_emissions_main.csv", index=False)
    bank_year.to_csv(PROCESSED / "financed_emissions_bank_year.csv", index=False)
    tot.to_csv(PROCESSED / "financed_emissions_totals.csv", index=False)
    sector_year.to_csv(PROCESSED / "financed_emissions_sector_year.csv", index=False)
    bank_sector.to_csv(PROCESSED / "financed_emissions_bank_sector.csv", index=False)
    sens_out.to_csv(PROCESSED / "financed_emissions_sensitivities.csv", index=False)
    flags.to_csv(INTERIM / "sensitivity_flags.csv", index=False)
    ch.to_csv(INTERIM / "estimation_checks.csv", index=False)
    print(ch.to_string())
    print(f"S6 included: {d['s6'] is not None}; balanced panel: {bal}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
