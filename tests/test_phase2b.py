"""Tests for Phase 2b: sector intensities and the intensity inputs of S4-S6,
plus the rule that Phase 1b and Phase 2a outputs stay unchanged."""

import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from bank_emissions.phase2a_crosswalk import AGRI, ECONOMY_WIDE, POWER, REFINING
from bank_emissions.phase2b_intensity import compute, load_inputs, recompute

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
INTERIM = ROOT / "data" / "interim"
OUT = PROC / "sector_intensity.csv"


def _need(*paths):
    missing = [p for p in paths if not p.exists()]
    if missing:
        pytest.skip(f"outputs not built: {missing}")


@pytest.fixture(scope="module")
def si():
    _need(OUT)
    return pd.read_csv(OUT)


@pytest.fixture(scope="module")
def inputs():
    _need(PROC / "btr1_emissions_by_category.csv", PROC / "nbs_gdp_by_activity.csv", PROC / "btr1_nbs_sector_map.csv")
    return load_inputs()


def _get(si, spec, group, year, col="intensity_t_per_naira"):
    return si[(si.spec == spec) & (si.intensity_group == group) & (si.year == year)][col].iloc[0]


def test_output_matches_a_fresh_computation(si, inputs):
    res = compute(*inputs)
    fresh = pd.concat([res[s] for s in ("main", "S4_PIK", "S5_LULUCF")], ignore_index=True)
    m = si.merge(fresh, on=["spec", "intensity_group", "year"], suffixes=("", "_new"))
    assert len(m) == len(si) == 162
    import numpy as np
    assert np.isclose(m.intensity_t_per_naira, m.intensity_t_per_naira_new, rtol=1e-12, atol=0.0).all()


def test_power_2022_by_hand(si, inputs):
    btr, nbs, _ = inputs
    e = btr[(btr.category_code == "1.A.1.a") & (btr.year == 2022)].kt_co2e.iloc[0] * 1000
    g = nbs[(nbs.activity_no == 22) & (nbs.year == 2022)].gdp_current_basic_naira.iloc[0]
    assert abs(_get(si, "main", POWER, 2022) / (e / g) - 1) < 1e-12


def test_economy_wide_2022_uses_printed_national_total(si, inputs):
    _, nbs, _ = inputs
    gdp = nbs[nbs.year == 2022].gdp_current_basic_naira.sum()
    assert abs(_get(si, "main", ECONOMY_WIDE, 2022) / (328_496.23e3 / gdp) - 1) < 1e-12


def test_year_rules(si):
    m = si[si.spec == "main"]
    for g in m.intensity_group.unique():
        e22 = _get(si, "main", g, 2022, "emissions_kt_co2e")
        for y in (2023, 2024):
            assert _get(si, "main", g, y, "emissions_kt_co2e") == e22  # Option A
            assert _get(si, "main", g, y, "gdp_year") == y
        assert _get(si, "main", g, 2025, "intensity_t_per_naira") == _get(si, "main", g, 2024, "intensity_t_per_naira")
    p = m[m.year == 2025]
    assert p.provisional.all() and not p.in_period_totals.any()
    assert m[m.year < 2025].in_period_totals.all()


def test_refining_2020_is_zero_as_printed(si):
    assert _get(si, "main", REFINING, 2020, "emissions_kt_co2e") == 0


def test_s4_changes_only_2023_onwards(si):
    for g in si.intensity_group.unique():
        for y in (2020, 2021, 2022):
            assert _get(si, "S4_PIK", g, y) == _get(si, "main", g, y)
    pr = pd.read_csv(INTERIM / "pik_growth_ratios.csv")
    r = pr[(pr.pik_sector == "Agriculture") & (pr.year == 2023)].ratio_to_2022.iloc[0]
    # agriculture group = 3 (agriculture) + 1.A.4.c and 1.B.1.b (energy): mixed ratios
    assert _get(si, "S4_PIK", AGRI, 2023, "emissions_kt_co2e") != _get(si, "main", AGRI, 2023, "emissions_kt_co2e")
    assert 0.9 < r < 1.1


def test_s5_adds_lulucf_to_agriculture_only(si, inputs):
    btr, _, _ = inputs
    lulucf = btr[(btr.category_code == "4") & (btr.year == 2021)].kt_co2e.iloc[0]
    d = _get(si, "S5_LULUCF", AGRI, 2021, "emissions_kt_co2e") - _get(si, "main", AGRI, 2021, "emissions_kt_co2e")
    assert abs(d - lulucf) < 1e-6
    assert _get(si, "S5_LULUCF", POWER, 2021) == _get(si, "main", POWER, 2021)


def test_recompute_function_agrees(si, inputs):
    rc = recompute(*inputs).merge(si[si.spec == "main"], on=["intensity_group", "year"])
    assert len(rc) == 54
    import numpy as np
    assert np.isclose(rc.recomputed_t_per_naira, rc.intensity_t_per_naira, rtol=1e-12, atol=0.0).all()


def test_checks_pass():
    _need(INTERIM / "intensity_checks.csv")
    c = pd.read_csv(INTERIM / "intensity_checks.csv")
    assert set(c.result) <= {"pass", "info"} and (c.result == "pass").sum() >= 60


def test_climate_watch_values_not_committed(si):
    assert "S6_ClimateWatch" not in set(si.spec)
    c = pd.read_csv(INTERIM / "intensity_checks.csv")
    s6 = c[c.spec == "S6_ClimateWatch"]
    assert s6.detail.str.startswith("values not committed").all()
    ignore = (ROOT / ".gitignore").read_text()
    assert "data/raw/*" in ignore


@pytest.mark.parametrize("manifest", ["phase1b_outputs_manifest.json", "phase2a_outputs_manifest.json"])
def test_earlier_outputs_unchanged(manifest):
    man = INTERIM / manifest
    _need(man)
    for f, h in json.loads(man.read_text())["sha256"].items():
        assert hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h, f
