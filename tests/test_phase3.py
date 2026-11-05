"""Tests for Phase 3 estimation, and that earlier outputs are unchanged."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from bank_emissions import phase3_estimate as p3

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
INTERIM = ROOT / "data" / "interim"


def _need(*paths):
    missing = [p for p in paths if not p.exists()]
    if missing:
        pytest.skip(f"outputs not built: {missing}")


@pytest.fixture(scope="module")
def d():
    _need(PROC / "exposures_by_sector.csv", PROC / "sector_intensity.csv", PROC / "sector_crosswalk.csv")
    return p3.load()


@pytest.fixture(scope="module")
def lines(d):
    return p3.apply_intensity(p3.expand(p3.main_rows(d["exp"]), d["cw"], d["splits"]),
                              p3.intensity_table(d["si"], "main"))


@pytest.fixture(scope="module")
def outputs():
    names = ["financed_emissions_main.csv", "financed_emissions_bank_year.csv", "financed_emissions_totals.csv",
             "financed_emissions_sensitivities.csv", "financed_emissions_sector_year.csv",
             "financed_emissions_bank_sector.csv"]
    _need(*[PROC / n for n in names])
    return {n.split(".")[0].replace("financed_emissions_", ""): pd.read_csv(PROC / n) for n in names}


def test_written_main_matches_fresh_run(lines, outputs):
    by = outputs["bank_year"].set_index(["bank", "year"]).tco2e
    fresh = p3.by_bank_year(lines)
    assert np.isclose(fresh.reindex(by.index), by, rtol=1e-12, atol=0).all()
    assert len(by) == 70


def test_recompute_separate_path(d, outputs):
    rc = p3.recompute_bank_year(d)
    by = outputs["bank_year"].set_index(["bank", "year"]).tco2e
    assert np.isclose(rc.reindex(by.index), by, rtol=1e-12, atol=0).all()


def test_exposure_equals_phase1b_totals(outputs):
    s = pd.read_csv(PROC / "sample.csv").set_index(["bank", "year"]).main_total_naira
    by = outputs["bank_year"].set_index(["bank", "year"]).exposure_naira
    assert np.isclose(by, s.reindex(by.index), rtol=1e-12).all()


def test_one_line_by_hand(d, outputs):
    m = outputs["main"]
    r = m[(m.bank == "ZENITHBANK") & (m.year == 2022) & (m.printed_category == "Power")].iloc[0]
    si = d["si"]
    i = si[(si.spec == "main") & (si.intensity_group == p3.POWER) & (si.year == 2022)].intensity_t_per_naira.iloc[0]
    assert np.isclose(r.tco2e, r.exposure_naira * i, rtol=1e-12)


def test_split_lines_preserve_exposure(outputs):
    m = outputs["main"]
    g = m.groupby(["bank", "year", "printed_category"]).agg(e=("exposure_naira", "sum"), row=("exposure_row_naira", "first"))
    assert np.isclose(g.e, g.row, rtol=1e-12).all()


def test_shares_sum_to_one(outputs):
    bs = outputs["bank_sector"].groupby(["bank", "year"]).share_of_bank_year_tco2e.sum()
    sy = outputs["sector_year"].groupby(["total_type", "year"]).share_of_year_tco2e.sum()
    assert ((bs - 1).abs() < 1e-12).all() and ((sy - 1).abs() < 1e-12).all()


def test_totals_and_provisional(outputs):
    t = outputs["totals"]
    assert set(t.total_type) == {"all available banks", "balanced panel"}
    period = t[t.year == "2020-2024"].set_index("total_type").tco2e
    yearly = t[t.year.isin([str(y) for y in range(2020, 2025)])].groupby("total_type").tco2e.sum()
    assert np.isclose(period, yearly.reindex(period.index), rtol=1e-12).all()
    assert t[t.year == "2025"].provisional.all()
    bal = t[(t.total_type == "balanced panel") & (t.year == "2020")].n_banks.iloc[0]
    assert bal == 11  # Unity Bank has no 2024-2025; ETI excluded
    by = outputs["bank_year"]
    assert not by[by.bank == "UNITYBNK"].in_balanced_panel.any()


def test_sensitivity_file(outputs):
    s = outputs["sensitivities"]
    by = s[s.row_type == "bank-year"].copy()
    by["year"] = by.year.astype(int)  # the file also holds '2020-2024' total rows
    assert len(by) == 70
    for col in p3.SENSITIVITIES:
        assert col in s.columns
    v = by[p3.SENSITIVITIES]
    assert np.isclose(by["min"], v.min(axis=1)).all() and np.isclose(by["max"], v.max(axis=1)).all()
    assert (by.min_sensitivity == v.idxmin(axis=1)).all() and (by.max_sensitivity == v.idxmax(axis=1)).all()
    # S3f applies only to Access 2025; S4 only from 2023
    assert by[by.S3f.notna()][["bank", "year"]].values.tolist() == [["ACCESSCORP", 2025]]
    assert by[by.year < 2023].S4.isna().all()
    # S1 not applicable where no bank-level table (e.g. Stanbic)
    assert by[by.bank == "STANBIC"].S1.isna().all()


def test_retarget_rules(lines):
    s3j = p3.retarget(lines, "S3j")
    hit = lines.tags.map(lambda t: "S3j" in t)
    assert hit.any() and (s3j.loc[hit, "target"] == p3.REFINING).all()
    s3k = p3.retarget(lines, "S3k")
    k = lines.tags.map(lambda t: "S3k" in t)
    assert set(s3k.loc[k, "target"]) <= {p3.MCM, p3.TRANSPORT}


def test_refining_flags_present():
    _need(INTERIM / "sensitivity_flags.csv")
    f = pd.read_csv(INTERIM / "sensitivity_flags.csv")
    assert (f[f.sensitivity == "S3j"].driver == "oil refining").all() and len(f[f.sensitivity == "S3j"]) > 0


def test_checks_all_pass():
    _need(INTERIM / "estimation_checks.csv")
    c = pd.read_csv(INTERIM / "estimation_checks.csv")
    assert (c.result == "pass").all(), c.to_string()


@pytest.mark.parametrize("manifest", ["phase1b_outputs_manifest.json", "phase2a_outputs_manifest.json",
                                      "phase2b_outputs_manifest.json"])
def test_earlier_outputs_unchanged(manifest):
    man = INTERIM / manifest
    _need(man)
    for f, h in json.loads(man.read_text())["sha256"].items():
        assert hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h, f
