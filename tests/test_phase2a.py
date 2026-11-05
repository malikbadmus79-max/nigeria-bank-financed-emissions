"""Tests for Phase 2a: crosswalk, sector map, BTR1/NID and NBS extractions, and
the rule that Phase 1b outputs stay unchanged."""

import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from bank_emissions.phase2a_crosswalk import (COMMON_SECTORS, ECONOMY_WIDE, NOT_LOAN, SERVICES, ZERO, build,
                                              key)

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
INTERIM = ROOT / "data" / "interim"


def _need(*paths):
    missing = [p for p in paths if not p.exists()]
    if missing:
        pytest.skip(f"outputs not built: {missing}")


# --- crosswalk ---------------------------------------------------------------

def test_key_normalises_spacing_and_ampersand():
    assert key("Oil&gas") == key("Oil & gas") == key("OIL AND GAS") == "oilandgas"
    assert key("ADMINISTRATIVEANDSUPPORTSERVICE ACTIVITIES") == key("Administrative and support service activities")


def test_crosswalk_covers_every_printed_label():
    _need(PROC / "exposures_by_sector.csv")
    cw = build()
    e = pd.read_csv(PROC / "exposures_by_sector.csv")
    pairs = set(zip(e.bank, e.printed_category))
    assert pairs == set(zip(cw.bank, cw.printed_category))
    assert (cw.common_sector.fillna("") != "").all()
    assert abs(cw.main_spec_share.sum() - 1) < 1e-9


def test_crosswalk_targets_and_rules_are_consistent():
    _need(PROC / "exposures_by_sector.csv")
    cw = build()
    assert set(cw.common_sector) <= set(COMMON_SECTORS) | {ECONOMY_WIDE, ZERO, NOT_LOAN}
    rule_target = {"zero": {ZERO}, "economy-wide": {ECONOMY_WIDE}, "services": {SERVICES},
                   "mapped": set(COMMON_SECTORS), "not a loan": {NOT_LOAN}}
    for r in cw.itertuples():
        assert r.common_sector in rule_target[r.rule], (r.bank, r.printed_category)
        assert r.status in {"ok", "review"}
        assert isinstance(r.reason, str) and r.reason


def test_crosswalk_plan_rules():
    _need(PROC / "exposures_by_sector.csv")
    cw = build().set_index(["bank", "printed_category"])
    assert cw.loc[("STERLINGNG", "Non-interest banking"), "rule"] == "economy-wide"
    assert cw.loc[("ACCESSCORP", "General commerce"), "sensitivity_group"] == "S3a"
    assert cw.loc[("ZENITHBANK", "Government"), "sensitivity_group"] == "S3d"
    assert cw.loc[("GTCO", "Individual"), "rule"] == "zero"
    res = cw.loc[("ACCESSCORP", "unallocated (printed total residual)")]
    assert res.rule == "economy-wide" and "S3f" in res.sensitivity_group


def test_not_a_loan_rows_carry_no_exposure():
    _need(PROC / "exposures_by_sector.csv")
    cw = build()
    assert (cw[cw.rule == "not a loan"].main_spec_naira == 0).all()


# --- sector map, BTR1, NBS ------------------------------------------------------

@pytest.mark.parametrize("name", ["btr1_checks.csv", "nbs_gdp_checks.csv", "sector_map_checks.csv"])
def test_phase2a_checks_all_pass(name):
    _need(INTERIM / name)
    ch = pd.read_csv(INTERIM / name)
    assert len(ch) and (ch.result == "pass").all(), ch[ch.result != "pass"].to_string()


def test_btr1_years_and_key_values():
    _need(PROC / "btr1_emissions_by_category.csv")
    d = pd.read_csv(PROC / "btr1_emissions_by_category.csv")
    assert sorted(d.year.unique()) == [2019, 2020, 2021, 2022]
    t = d[d.category == "Total CO2 equivalent emissions without LULUCF"].set_index("year").kt_co2e
    assert abs(t[2022] - 328496.23) < 0.005  # printed on BTR1 PDF p. 62
    nid = d[d.level == "NID sub-category"].set_index(["category_code", "year"]).kt_co2e
    assert nid[("1.B.1.b", 2022)] > nid[("1.B.1.a", 2022)]  # fuel transformation dominates solid fuels


def test_nbs_activities_and_total():
    _need(PROC / "nbs_gdp_by_activity.csv")
    d = pd.read_csv(PROC / "nbs_gdp_by_activity.csv")
    assert d.activity_no.nunique() == 46 and sorted(d.year.unique()) == list(range(2019, 2025))
    assert abs(d[d.year == 2024].gdp_current_basic_naira_million.sum() - 364_619_399.00) < 0.5


def test_sector_map_nbs_groups_partition_gdp():
    _need(PROC / "btr1_nbs_sector_map.csv")
    from bank_emissions.phase2a_sector_map import build as build_map
    m, ch = build_map()
    assert (ch.result == "pass").all()
    assert (m[m.row_type == "common sector"].common_sector.isin(COMMON_SECTORS + [ECONOMY_WIDE])).all()


# --- Phase 1b outputs unchanged ----------------------------------------------------

def test_phase1b_outputs_unchanged():
    man = INTERIM / "phase1b_outputs_manifest.json"
    _need(man)
    for f, h in json.loads(man.read_text())["sha256"].items():
        assert hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h, f
