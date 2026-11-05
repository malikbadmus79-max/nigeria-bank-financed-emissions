"""POST-RESULTS CHECK (added 2026-11-05 after the results; not part of the
fixed analysis plan): sensitivity S7, transport intensity excluding passenger
cars (CRT 1.A.3.b.i).

The main transport intensity uses all of 1.A.3 (including road transport,
1.A.3.b, of which passenger cars are part). The BTR1 National Inventory
Document splits road transport by vehicle type in two places:

- Annex II, Table AII.1 (uncertainty assessment, PDF pp. 202-203): emissions by
  vehicle type and gas for the base year 2000 and for 2022 (columns 'base year'
  and 'year-t'), sub-categories 1.A.3.b.i cars, ii light-duty trucks, iii
  heavy-duty trucks and buses, iv motorcycles;
- Table 3.32 (PDF pp. 82-84): fuel use (kt, gasoline and diesel) by vehicle type
  for every year 2000-2022; Table 3.33 applies the same emission factors per
  fuel to every vehicle type.

Car emissions:
- 2022: as printed in Table AII.1 (CO2 + CH4 + N2O, kt CO2e). Under Option A the
  2022 value also applies to 2023-2024 (and to the provisional 2025).
- 2020 and 2021: not printed by vehicle type. The car share of road CO2e is
  rebuilt from Table 3.32 fuel use: CO2 per kt of gasoline and of diesel is
  estimated by least squares from the printed 2000 and 2022 CO2 of the four
  vehicle types (8 equations, 2 unknowns; no external constant is typed in);
  each vehicle type's CO2e in year t is its printed 2022 CO2e scaled by its
  fuel-based CO2 in t relative to 2022; the car share is applied to the
  printed road total of Table 3.27 (PDF p. 80). Validation: the method's 2022
  vehicle shares are compared with the printed 2022 shares.

S7: transport emissions = BTR1 1.A.3 - car emissions; same GDP; every other
element as in the main specification. Car emissions are left unattributed
(like residential combustion).

Outputs (new files only; earlier outputs unchanged):
- data/processed/postresults_s7_road_split.csv
- data/processed/postresults_s7_results.csv
- data/interim/postresults_s7_checks.csv

    python -m bank_emissions.postresults_s7
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from .phase1b_extract import INTERIM, PROCESSED, ROOT
from .phase2a_crosswalk import TRANSPORT
from .phase3_estimate import PERIOD_YEARS, ZERO_GROUP

NID = ROOT / "data" / "raw" / "intensity" / "Nigeria_BTR1_NID_2024.pdf"
VEHICLES = ["1.A.3.b.i", "1.A.3.b.ii", "1.A.3.b.iii", "1.A.3.b.iv"]
VNAME = {"1.A.3.b.i": "Cars", "1.A.3.b.ii": "Light-duty trucks", "1.A.3.b.iii": "Heavy-duty trucks and buses",
         "1.A.3.b.iv": "Motorcycles"}
# Table 3.32 series in printed order: (vehicle, fuel)
AD_SERIES = [("1.A.3.b.i", "gasoline"), ("1.A.3.b.i", "diesel"), ("1.A.3.b.ii", "gasoline"), ("1.A.3.b.ii", "diesel"),
             ("1.A.3.b.iii", "gasoline"), ("1.A.3.b.iii", "diesel"), ("1.A.3.b.iv", "gasoline")]
AD_YEARS = [list(range(2000, 2008)), list(range(2008, 2016)), list(range(2016, 2023))]


def _text(pages: list[int]) -> str:
    import pypdfium2

    doc = pypdfium2.PdfDocument(str(NID))
    return " ".join(re.sub(r"\s+", " ", doc[p - 1].get_textpage().get_text_range()) for p in pages)


def _n(s: str) -> float:
    return float(s.replace(",", ""))


def annex_vehicle_emissions() -> pd.DataFrame:
    """Table AII.1: kt of each gas for 2000 and 2022, by vehicle type."""
    t = _text([202, 203])
    rows = []
    for v in VEHICLES:
        for gas in ("CO2", "CH4", "N2O"):
            m = re.search(re.escape(v) + r" - [A-Za-z -]+? - Liquid Fuels " + gas + r" ([\d,]+\.\d+) ([\d,]+\.\d+)", t)
            if not m:
                raise LookupError(f"Table AII.1 row not found: {v} {gas}")
            rows.append(dict(vehicle=v, gas=gas, kt_2000=_n(m.group(1)), kt_2022=_n(m.group(2))))
    return pd.DataFrame(rows)


def activity_data() -> pd.DataFrame:
    """Table 3.32: BTR1-NID1 fuel use (kt) by vehicle type and fuel, 2000-2022."""
    t = _text([82, 83, 84])
    t = t[t.index("Table 3.32. Activity Data used for Road transportation"):t.index("Table 3.33")]
    rows = re.findall(r"BTR1 - NID1 ((?:[\d,]+ ?)+?)(?= -|\s*Year|\s*[A-Z][a-z]|$)", t)
    vals = [[_n(x) for x in r.split()] for r in rows]
    if len(vals) != 3 * len(AD_SERIES):
        raise ValueError(f"expected {3 * len(AD_SERIES)} BTR1 rows in Table 3.32, found {len(vals)}")
    out = []
    for k, (veh, fuel) in enumerate(AD_SERIES):
        for blk in range(3):
            v = vals[3 * k + blk]
            ys = AD_YEARS[blk]
            if len(v) != len(ys):
                raise ValueError(f"{veh} {fuel} block {blk}: {len(v)} values for {len(ys)} years")
            out += [dict(vehicle=veh, fuel=fuel, year=y, kt=x) for y, x in zip(ys, v)]
    return pd.DataFrame(out)


def road_totals() -> dict[int, float]:
    """Table 3.27 (PDF p. 80): road transportation kt CO2e; the second block is 2012-2022."""
    t = _text([80])
    m = re.search(r"Table 3\.27\. Emissions \(kt CO2 e\) for Road Transportation \(2000-2022\) ((?:[\d,]+ ){11})-", t)
    if not m:
        raise LookupError("Table 3.27 values not found")
    vals = [_n(x) for x in m.group(1).split()]
    return dict(zip(range(2012, 2023), vals))


def fuel_factors(ad: pd.DataFrame, annex: pd.DataFrame) -> tuple[dict, float]:
    """CO2 (kt) per kt of gasoline and of diesel, least squares over the
    printed CO2 of the four vehicle types in 2000 and 2022."""
    A, b = [], []
    co2 = annex[annex.gas == "CO2"].set_index("vehicle")
    for v in VEHICLES:
        for y, col in ((2000, "kt_2000"), (2022, "kt_2022")):
            g = ad[(ad.vehicle == v) & (ad.year == y)].set_index("fuel").kt
            A.append([g.get("gasoline", 0.0), g.get("diesel", 0.0)])
            b.append(co2.loc[v, col])
    A, b = np.array(A), np.array(b)
    x, *_ = np.linalg.lstsq(A, b, rcond=None)
    fit = A @ x
    worst = float(np.max(np.abs(fit / b - 1)))
    return {"gasoline": x[0], "diesel": x[1]}, worst


def road_split() -> tuple[pd.DataFrame, pd.DataFrame]:
    annex = annex_vehicle_emissions()
    ad = activity_data()
    roads = road_totals()
    c, worst_fit = fuel_factors(ad, annex)
    co2e22 = annex.groupby("vehicle").kt_2022.sum()
    ad["co2_fuel"] = ad.kt * ad.fuel.map(c)
    fco2 = ad.groupby(["vehicle", "year"]).co2_fuel.sum()
    rows, checks = [], []
    for y in (2020, 2021, 2022):
        est = {v: co2e22[v] * fco2[(v, y)] / fco2[(v, 2022)] for v in VEHICLES}
        tot = sum(est.values())
        for v in VEHICLES:
            share = est[v] / tot
            printed = co2e22[v] if y == 2022 else np.nan
            rows.append(dict(year=y, vehicle=v, vehicle_name=VNAME[v], share_of_road_from_activity_data=share,
                             road_total_table_3_27_kt=roads[y],
                             kt_co2e_used=printed if y == 2022 else share * roads[y],
                             basis=("printed, NID Annex II Table AII.1 (PDF p. 203), CO2 + CH4 + N2O" if y == 2022 else
                                    "car share from NID Table 3.32 fuel use (PDF pp. 82-84) x Table 3.27 road total (PDF p. 80)")))
    df = pd.DataFrame(rows)
    p22 = co2e22 / co2e22.sum()
    s22 = df[df.year == 2022].set_index("vehicle").share_of_road_from_activity_data
    worst_share = float((s22 - p22).abs().max())
    checks.append(dict(check="fuel_factor_fit", result="pass" if worst_fit < 0.01 else "fail",
                       detail=f"CO2 per kt fuel fitted to the 8 printed vehicle-type CO2 values (2000, 2022): gasoline "
                              f"{c['gasoline']:.4f}, diesel {c['diesel']:.4f}; largest relative misfit {worst_fit:.2%}"))
    checks.append(dict(check="method_reproduces_printed_2022_shares", result="pass" if worst_share < 0.005 else "fail",
                       detail=f"largest gap between rebuilt and printed 2022 vehicle shares {worst_share * 100:.2f} "
                              f"percentage points (car share printed {p22['1.A.3.b.i']:.2%})"))
    checks.append(dict(check="printed_vehicle_sum_equals_table_3_27_2022",
                       result="pass" if abs(co2e22.sum() - roads[2022]) <= 2.0 else "fail",
                       detail=f"Table AII.1 2022 sum {co2e22.sum():,.1f} kt vs Table 3.27 {roads[2022]:,.0f} kt"))
    return df, pd.DataFrame(checks)


def s7_results(split: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    btr = pd.read_csv(PROCESSED / "btr1_emissions_by_category.csv")
    t210 = btr[btr.level == "Table 2.10"].set_index(["category_code", "year"]).kt_co2e
    si = pd.read_csv(PROCESSED / "sector_intensity.csv")
    main_si = si[si.spec == "main"].set_index(["intensity_group", "year"])
    cars = split[split.vehicle == "1.A.3.b.i"].set_index("year").kt_co2e_used
    s7 = {}
    rows_i = []
    for y in range(2020, 2026):
        ey = min(y, 2022)
        gy = min(y, 2024)
        e = t210[("1.A.3", ey)] - cars[ey]
        gdp = main_si.loc[(TRANSPORT, gy), "gdp_naira"]
        s7[y] = e * 1000.0 / gdp
        rows_i.append(dict(year=y, transport_kt_main=t210[("1.A.3", ey)], cars_kt=cars[ey], transport_kt_s7=e,
                           gdp_naira=gdp, intensity_main_t_per_million=main_si.loc[(TRANSPORT, y), "intensity_t_per_naira"] * 1e6,
                           intensity_s7_t_per_million=s7[y] * 1e6, provisional=y == 2025))
    m = pd.read_csv(PROCESSED / "financed_emissions_main.csv")
    m["tco2e_s7"] = np.where(m.intensity_group == TRANSPORT, m.exposure_naira * m.year.map(s7), m.tco2e)
    bank_year = pd.read_csv(PROCESSED / "financed_emissions_bank_year.csv")
    panel = set(bank_year[bank_year.in_balanced_panel].bank)
    rows = []
    for ttype, sub in (("all available banks", m), ("balanced panel", m[m.bank.isin(panel)])):
        for y in [*PERIOD_YEARS, "2020-2024", 2025]:
            g = sub[sub.year.isin(PERIOD_YEARS)] if y == "2020-2024" else sub[sub.year == y]
            tr = g.intensity_group == TRANSPORT
            rows.append(dict(total_type=ttype, year=str(y), provisional=y == 2025,
                             tco2e_main=g.tco2e.sum(), tco2e_s7=g.tco2e_s7.sum(),
                             transport_share_main=g[tr].tco2e.sum() / g.tco2e.sum(),
                             transport_share_s7=g[tr].tco2e_s7.sum() / g.tco2e_s7.sum()))
    return pd.DataFrame(rows), pd.DataFrame(rows_i), m


def s7_sector_shares(m: pd.DataFrame) -> pd.DataFrame:
    """Shares of financed emissions by reporting sector (as in Phase 3), main
    and S7, balanced panel, pooled 2020-2024."""
    bank_year = pd.read_csv(PROCESSED / "financed_emissions_bank_year.csv")
    panel = set(bank_year[bank_year.in_balanced_panel].bank)
    g = m[m.bank.isin(panel) & m.year.isin(PERIOD_YEARS)].groupby("reporting_sector")[
        ["exposure_naira", "tco2e", "tco2e_s7"]].sum()
    out = pd.DataFrame({"reporting_sector": g.index,
                        "loan_share": g.exposure_naira / g.exposure_naira.sum(),
                        "share_main": g.tco2e / g.tco2e.sum(),
                        "share_s7": g.tco2e_s7 / g.tco2e_s7.sum(),
                        "tco2e_main": g.tco2e, "tco2e_s7": g.tco2e_s7}).reset_index(drop=True)
    out.insert(0, "total_type", "balanced panel")
    out.insert(1, "years", "2020-2024 pooled")
    out.insert(2, "row_type", "sector")
    out = out.sort_values("share_s7", ascending=False).reset_index(drop=True)
    # combined row: transport + power + upstream oil and gas (shares of all sectors; not a further sector)
    top = out[out.reporting_sector.isin(TOP3)]
    comb = {c: top[c].sum() for c in ("loan_share", "share_main", "share_s7", "tco2e_main", "tco2e_s7")}
    comb.update(total_type="balanced panel", years="2020-2024 pooled", row_type="combined",
                reporting_sector="Transport + power + oil and gas upstream (combined)")
    return pd.concat([out, pd.DataFrame([comb])], ignore_index=True)[list(out.columns)]


TOP3 = ["Transport and storage", "Power (electricity and gas supply)", "Oil and gas, upstream"]


def s7_national_share(res: pd.DataFrame) -> pd.DataFrame:
    """S7 financed emissions as a share of BTR1 national emissions without
    LULUCF, 2020-2022 (as data/processed/national_share.csv for the main)."""
    si = pd.read_csv(PROCESSED / "sector_intensity.csv")
    nat = si[(si.spec == "main") & (si.intensity_group == "(economy-wide average)")].set_index("year").emissions_t_co2e
    r = res[res.year.isin(["2020", "2021", "2022"])].copy()
    r["year"] = r.year.astype(int)
    r["national_without_lulucf_tco2e"] = r.year.map(nat)
    r["share_main"] = r.tco2e_main / r.national_without_lulucf_tco2e
    r["share_s7"] = r.tco2e_s7 / r.national_without_lulucf_tco2e
    return r[["total_type", "year", "tco2e_main", "tco2e_s7", "national_without_lulucf_tco2e", "share_main", "share_s7"]]


def main() -> int:
    split, ch = road_split()
    res, inten, lines = s7_results(split)
    shares = s7_sector_shares(lines)
    shares.to_csv(PROCESSED / "postresults_s7_sector_shares.csv", index=False)
    nshare = s7_national_share(res)
    nshare.to_csv(PROCESSED / "postresults_s7_national_share.csv", index=False)
    print(shares.to_string())
    print(nshare.to_string())
    split.to_csv(PROCESSED / "postresults_s7_road_split.csv", index=False)
    res.to_csv(PROCESSED / "postresults_s7_results.csv", index=False)
    inten.to_csv(PROCESSED / "postresults_s7_intensity.csv", index=False)
    ch.to_csv(INTERIM / "postresults_s7_checks.csv", index=False)
    pd.set_option("display.width", 220)
    print(ch.to_string())
    print(split.to_string())
    print(inten.to_string())
    print(res.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
