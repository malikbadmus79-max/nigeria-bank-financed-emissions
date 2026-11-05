"""Tests for the post-results S7 check (transport excluding passenger cars).
Added after the results; not part of the fixed plan."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
INTERIM = ROOT / "data" / "interim"


def _need(*paths):
    missing = [p for p in paths if not p.exists()]
    if missing:
        pytest.skip(f"outputs not built: {missing}")


def test_checks_pass():
    _need(INTERIM / "postresults_s7_checks.csv")
    c = pd.read_csv(INTERIM / "postresults_s7_checks.csv")
    assert len(c) == 3 and (c.result == "pass").all(), c.to_string()


def test_road_split():
    _need(PROC / "postresults_s7_road_split.csv")
    s = pd.read_csv(PROC / "postresults_s7_road_split.csv")
    assert set(s.year) == {2020, 2021, 2022} and s.groupby("year").size().eq(4).all()
    assert np.allclose(s.groupby("year").share_of_road_from_activity_data.sum(), 1.0)
    p22 = s[s.year == 2022]
    assert p22.basis.str.startswith("printed").all()
    # printed 2022 vehicle emissions sum to the Table 3.27 road total within rounding
    assert abs(p22.kt_co2e_used.sum() - p22.road_total_table_3_27_kt.iloc[0]) <= 2.0
    cars = s[s.vehicle == "1.A.3.b.i"]
    assert ((cars.share_of_road_from_activity_data > 0.5) & (cars.share_of_road_from_activity_data < 0.7)).all()


def test_intensity_and_results(tmp_path):
    _need(PROC / "postresults_s7_intensity.csv", PROC / "postresults_s7_results.csv")
    it = pd.read_csv(PROC / "postresults_s7_intensity.csv").set_index("year")
    assert np.allclose(it.transport_kt_s7, it.transport_kt_main - it.cars_kt)
    assert np.allclose(it.intensity_s7_t_per_million, it.transport_kt_s7 * 1000 / it.gdp_naira * 1e6)
    assert (it.intensity_s7_t_per_million < it.intensity_main_t_per_million).all()
    assert it.loc[2023, "cars_kt"] == it.loc[2022, "cars_kt"]  # Option A
    r = pd.read_csv(PROC / "postresults_s7_results.csv")
    r["year"] = r.year.astype(str)
    main_tot = pd.read_csv(PROC / "financed_emissions_totals.csv")
    main_tot["year"] = main_tot.year.astype(str)
    m = r.merge(main_tot, on=["total_type", "year"])
    assert np.allclose(m.tco2e_main, m.tco2e)  # main column equals the Phase 3 totals
    assert (r.tco2e_s7 < r.tco2e_main).all() and (r.transport_share_s7 < r.transport_share_main).all()


def test_s7_line_by_hand():
    _need(PROC / "postresults_s7_intensity.csv")
    it = pd.read_csv(PROC / "postresults_s7_intensity.csv").set_index("year")
    m = pd.read_csv(PROC / "financed_emissions_main.csv")
    tr = m[(m.intensity_group == "Transport and storage") & (m.year == 2022)]
    s7 = (tr.exposure_naira * it.loc[2022, "intensity_s7_t_per_million"] / 1e6).sum()
    main = tr.tco2e.sum()
    assert np.isclose(s7 / main, it.loc[2022, "intensity_s7_t_per_million"] / it.loc[2022, "intensity_main_t_per_million"])


def test_results_md_section_labelled():
    t = (ROOT / "docs" / "results.md").read_text(encoding="utf-8")
    assert "### Post-results check: S7" in t
    assert "Added after the results (2026-11-05); not part of the fixed analysis plan." in t
    sens = t.index("## Sensitivities")
    assert sens < t.index("### Post-results check: S7") < t.index("## RQ3")


@pytest.mark.parametrize("manifest", ["phase1b_outputs_manifest.json", "phase2a_outputs_manifest.json",
                                      "phase2b_outputs_manifest.json", "phase3_outputs_manifest.json"])
def test_earlier_outputs_unchanged(manifest):
    man = INTERIM / manifest
    _need(man)
    for f, h in json.loads(man.read_text())["sha256"].items():
        assert hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h, f


def test_s7_sector_shares():
    _need(PROC / "postresults_s7_sector_shares.csv")
    s = pd.read_csv(PROC / "postresults_s7_sector_shares.csv")
    s = s[s.row_type == "sector"].set_index("reporting_sector")
    assert np.isclose(s.share_s7.sum(), 1.0) and np.isclose(s.share_main.sum(), 1.0)
    assert round(s.loc["Power (electricity and gas supply)", "share_s7"] * 100, 1) == 26.0
    assert round(s.loc["Oil and gas, upstream", "share_s7"] * 100, 1) == 24.9
    assert round(s.loc["Transport and storage", "share_s7"] * 100, 1) == 22.1
    top3 = s.loc[["Transport and storage", "Power (electricity and gas supply)", "Oil and gas, upstream"], "share_s7"].sum()
    assert round(top3 * 100, 1) == 73.0
    # S7 changes only transport; other sectors' tonnes are unchanged
    other = s.drop(index="Transport and storage")
    assert np.allclose(other.tco2e_s7, other.tco2e_main)
    # main shares agree with the Phase 3 sector table
    sy = pd.read_csv(PROC / "financed_emissions_sector_year.csv")
    g = sy[(sy.total_type == "balanced panel") & sy.year.isin(range(2020, 2025))].groupby("reporting_sector").tco2e.sum()
    assert np.allclose((g / g.sum()).reindex(s.index), s.share_main)


def test_s7_national_share():
    _need(PROC / "postresults_s7_national_share.csv")
    n = pd.read_csv(PROC / "postresults_s7_national_share.csv")
    a = n[n.total_type == "all available banks"].set_index("year").share_s7
    assert [round(a[y] * 100, 1) for y in (2020, 2021, 2022)] == [8.9, 8.4, 9.2]
    main = pd.read_csv(PROC / "national_share.csv")
    m = n.merge(main, on=["total_type", "year"])
    assert np.allclose(m.share_main, m.share_of_national)


def test_combined_top3_row():
    _need(PROC / "postresults_s7_sector_shares.csv")
    s = pd.read_csv(PROC / "postresults_s7_sector_shares.csv")
    comb = s[s.row_type == "combined"]
    assert len(comb) == 1
    c = comb.iloc[0]
    sec = s[s.row_type == "sector"].set_index("reporting_sector")
    top = sec.loc[["Transport and storage", "Power (electricity and gas supply)", "Oil and gas, upstream"]]
    for col in ("loan_share", "share_main", "share_s7"):
        assert np.isclose(c[col], top[col].sum())
    assert round(c.loan_share * 100, 1) == 17.1
    assert round(c.share_main * 100, 1) == 79.2
    assert round(c.share_s7 * 100, 1) == 73.0
    t = (ROOT / "docs" / "results.md").read_text(encoding="utf-8")
    assert "17.1% of loans; 79.2% of financed emissions under the main specification and 73.0% under S7" in t
