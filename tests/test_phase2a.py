"""Tests for Phase 2a: crosswalk, sector map, BTR1/NID and NBS extractions, and
the rule that Phase 1b outputs stay unchanged."""

import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from bank_emissions.phase2a_crosswalk import (COMMON_SECTORS, CONSTR, ECONOMY_WIDE, NOT_LOAN, OIL_UP, SERVICES,
                                              SPLIT, TRANSPORT, ZERO, build, build_splits, key, oil_gas_shares)

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
    assert set(cw.common_sector) <= set(COMMON_SECTORS) | {ECONOMY_WIDE, ZERO, NOT_LOAN, SPLIT}
    rule_target = {"zero": {ZERO}, "economy-wide": {ECONOMY_WIDE}, "services": {SERVICES},
                   "mapped": set(COMMON_SECTORS), "not a loan": {NOT_LOAN}, "split": {SPLIT}}
    for r in cw.itertuples():
        assert r.common_sector in rule_target[r.rule], (r.bank, r.printed_category)
        assert r.status == "ok"  # all review rows signed off 2026-11-05
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


# --- sign-off 2026-11-05 ---------------------------------------------------------

@pytest.fixture(scope="module")
def signed():
    _need(PROC / "exposures_by_sector.csv", PROC / "nbs_gdp_by_activity.csv")
    e = pd.read_csv(PROC / "exposures_by_sector.csv")
    cw = build()
    splits, per_bank = build_splits(cw, e)
    return e, cw, splits, per_bank


def test_no_review_rows_and_decisions_recorded(signed):
    _, cw, _, _ = signed
    assert (cw.status == "ok").all()
    reviewed = cw[cw.proposed_status == "review"]
    assert len(reviewed) == 37 and reviewed.reason.str.startswith("Signed off 2026-11-05").all()


def test_split_shares_sum_to_one_for_every_label_year(signed):
    _, cw, splits, _ = signed
    sums = splits.groupby(["bank", "printed_category", "year"]).share.sum()
    assert ((sums - 1).abs() < 1e-9).all()
    split_rows = cw[cw.rule == "split"]
    expected = sum(len(y.split(";")) for y in split_rows.years)
    assert len(sums) == expected
    assert splits.share_source.str.len().gt(0).all()


def test_oil_gas_shares_from_access_and_fcmb_only(signed):
    e, _, splits, per_bank = signed
    assert set(per_bank.bank) == {"ACCESSCORP", "FCMB"}
    a25 = per_bank[(per_bank.bank == "ACCESSCORP") & (per_bank.year == 2025)].iloc[0]
    assert not a25.used and "downstream" in a25.note  # Access FY2025 omits the downstream row
    _, avg = oil_gas_shares(e)
    assert avg[avg.year == 2025].banks_used.iloc[0] == "FCMB"
    z = splits[(splits.bank == "ZENITHBANK") & (splits.year == 2022)].set_index("component")
    used = per_bank[(per_bank.year == 2022) & per_bank.used]
    assert abs(z.share["upstream"] - used.share_upstream.mean()) < 1e-12
    assert z.common_sector["upstream"] == OIL_UP and z.common_sector["services"] == SERVICES
    assert "S3j" in z.sensitivity_group["downstream"] and "S3i" in z.sensitivity_group["services"]


def test_combined_shares_follow_nbs_gdp(signed):
    _, _, splits, _ = signed
    nbs = pd.read_csv(PROC / "nbs_gdp_by_activity.csv")
    g = nbs[nbs.year == 2023].set_index("activity_no").gdp_current_basic_naira_million
    z = splits[(splits.bank == "ZENITHBANK") & (splits.year == 2023)].set_index("component")
    assert abs(z.share["construction"] - g[24] / (g[24] + g[40])) < 1e-12
    assert z.common_sector["construction"] == CONSTR
    t = splits[(splits.bank == "GTCO") & (splits.year == 2025)].set_index("component")
    g24 = nbs[nbs.year == 2024].set_index("activity_no").gdp_current_basic_naira_million
    assert abs(t.share["transport"] - g24.loc[27:32].sum() / g24.loc[27:36].sum()) < 1e-12  # 2025 uses 2024
    assert t.common_sector["transport"] == TRANSPORT


def test_signoff_sensitivity_tags(signed):
    _, cw, _, _ = signed
    c = cw.set_index(["bank", "printed_category"])
    assert set(c.loc[("ZENITHBANK", "Oil and gas"), "sensitivity_group"].split(";")) >= {"S3g", "S3h"}
    assert c.loc[("ACCESSCORP", "Oil And Gas - services"), "common_sector"] == SERVICES
    assert "S3i" in c.loc[("ACCESSCORP", "Oil And Gas - services"), "sensitivity_group"]
    assert "S3j" in c.loc[("FCMB", "Oil and Gas - Downstream"), "sensitivity_group"]
    assert "S3k" in c.loc[("GTCO", "Info.Telecoms & Transport"), "sensitivity_group"]
    assert c.loc[("STANBIC", "Mining"), "common_sector"] == OIL_UP
    assert "S3l" in c.loc[("STANBIC", "Mining"), "sensitivity_group"]
    assert "services" in c.loc[("ACCESSCORP", "unallocated (printed total residual)"), "reason"]


def test_sector_map_signoff():
    _need(PROC / "btr1_nbs_sector_map.csv")
    from bank_emissions.phase2a_sector_map import _codes, build as build_map
    m, ch = build_map()
    assert (m.status == "ok").all() and (ch.result == "pass").all()
    sec = m[m.row_type == "common sector"].set_index("common_sector")
    assert {"1.A.4.c", "1.B.1.b"} <= set(_codes(sec.loc["Agriculture, forestry and fishing", "btr1_codes"]))
    assert "1.B.1.a" in _codes(sec.loc["Mining and quarrying (non-oil)", "btr1_codes"])
    assert "1.A.1.c" in _codes(sec.loc[OIL_UP, "btr1_codes"])
    unassigned = [c for s in m[m.row_type != "common sector"].btr1_codes for c in _codes(s)]
    assert not {"1.A.4.c", "1.B.1.a", "1.B.1.b"} & set(unassigned)


def test_plan_records_signoff_additions():
    plan = (ROOT / "docs" / "analysis_plan.md").read_text(encoding="utf-8")
    assert "Recorded addition, 2026-11-05" in plan
    for s in ["S3g", "S3h", "S3i", "S3j", "S3k", "S3l"]:
        assert f"| {s} |" in plan


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
