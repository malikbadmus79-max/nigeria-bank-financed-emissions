"""Tests for Phase 4: comparison, decomposition, constant naira, national share,
disclosure table, figures and write-up; earlier outputs unchanged."""

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


@pytest.fixture(scope="module")
def comp():
    _need(PROC / "published_comparison.csv")
    return pd.read_csv(PROC / "published_comparison.csv")


def test_published_figures_as_printed(comp):
    for r in comp.itertuples():
        assert np.isclose(r.published_tco2e, float(r.value_as_printed.replace(",", "")))
    f = comp[(comp.bank == "FIDELITYBK") & ~comp["item"].str.startswith("(consistency)")].set_index("year")
    assert f.loc[2024, "value_as_printed"] == "4,606,362.05" and f.loc[2025, "pdf_page"] == 99
    assert f.loc[2023, "value_as_printed"] == "682,299.78"
    u = comp[comp.bank == "UBA"]
    assert set(u.coverage_share.dropna()) == {0.9, 0.52}
    # consistency: the FY2025 report's 2023 column equals the FY2023 sustainability report
    c = comp[comp["item"].str.startswith("(consistency)")].published_tco2e.iloc[0]
    assert c == f.loc[2023, "published_tco2e"]


def test_ratios_use_phase3_estimates(comp):
    s = pd.read_csv(PROC / "financed_emissions_sensitivities.csv")
    by = s[s.row_type == "bank-year"].copy()
    by["year"] = by.year.astype(int)
    est = by.set_index(["bank", "year"])["main"]
    for r in comp.itertuples():
        assert np.isclose(r.estimate_main_tco2e, est[(r.bank, r.year)])
        assert np.isclose(r.ratio_main_to_published, r.estimate_main_tco2e / r.published_tco2e)
    u = comp[comp.coverage_share.notna()]
    assert np.allclose(u.estimate_main_x_coverage_tco2e, u.estimate_main_tco2e * u.coverage_share)


def test_decomposition_closes_and_matches_totals():
    _need(PROC / "change_decomposition_2022_2024.csv")
    d = pd.read_csv(PROC / "change_decomposition_2022_2024.csv")
    assert (d.residual.abs() < 1e-3).all()
    assert np.allclose(d.exposure_effect, d.exposure_volume_effect + d.exposure_mix_effect)
    assert np.allclose(d.total_change, d.tco2e_to - d.tco2e_from)
    t = pd.read_csv(PROC / "financed_emissions_totals.csv")
    bal = t[t.total_type == "balanced panel"].set_index("year").tco2e
    tot = d[d.bank == "(balanced panel total)"].iloc[0]
    assert np.isclose(tot.tco2e_from, bal["2022"]) and np.isclose(tot.tco2e_to, bal["2024"])
    assert np.isclose(d[d.bank != "(balanced panel total)"].total_change.sum(), tot.total_change)


def test_constant_naira():
    _need(PROC / "constant_2022_naira.csv", PROC / "gdp_deflator_basic_prices.csv")
    df = pd.read_csv(PROC / "gdp_deflator_basic_prices.csv").set_index("year")
    assert np.isclose(df.loc[2022, "deflator_2022_1"], 1.0)
    assert np.isclose(df.loc[2019, "deflator_2019_100"], 100.0)
    cn = pd.read_csv(PROC / "constant_2022_naira.csv")
    r22 = cn[cn.year == 2022]
    assert np.allclose(r22.exposure_constant_2022_naira, r22.exposure_nominal_naira)
    assert np.allclose(r22.tco2e_constant_2022_naira_2022_intensity, r22.tco2e_main)
    assert np.allclose(cn.exposure_constant_2022_naira, cn.exposure_nominal_naira / cn.deflator_2022_1)
    assert 2025 not in set(cn.year)


def test_national_share():
    _need(PROC / "national_share.csv")
    n = pd.read_csv(PROC / "national_share.csv")
    assert sorted(n.year.unique()) == [2020, 2021, 2022]
    assert np.allclose(n.share_of_national, n.tco2e / n.national_without_lulucf_tco2e)
    assert (n[n.year == 2022].national_without_lulucf_tco2e == 328_496_230.0).all()


def test_disclosure_table():
    _need(PROC / "disclosure_table.csv")
    d = pd.read_csv(PROC / "disclosure_table.csv")
    assert len(d) == 13 * 6 and d.groupby("bank").size().eq(6).all()
    found = d[d.status != "not found in the documents opened"]
    assert found.document.notna().all() and found.pdf_page.notna().all() and found.as_printed.notna().all()
    fe = d[d["item"] == "financed_emissions"].set_index("bank").status
    assert fe["UBA"] == "figure disclosed" and fe["FIDELITYBK"] == "figure disclosed"
    assert (d[d.status == "not found in the documents opened"].documents_opened.notna()).all()


def test_disclosure_evidence_rereads():
    pytest.importorskip("pypdfium2")
    from bank_emissions import phase4_disclosure as p4d
    if not (ROOT / p4d.EVIDENCE[0][3]).exists():
        pytest.skip("source PDFs not present")
    fresh = p4d.build()
    saved = pd.read_csv(PROC / "disclosure_table.csv")
    assert list(fresh.as_printed.fillna("")) == list(saved.as_printed.fillna(""))


def test_b62_assessment():
    _need(PROC / "ifrs_s2_b62_assessment.csv")
    a = pd.read_csv(PROC / "ifrs_s2_b62_assessment.csv")
    assert len(a) == 13 * 5
    assert a[a.bank == "FCMB"].finding.str.contains("no financed-emissions figure").all()


def test_figures_exist():
    for f in ["fig1_loan_vs_emission_share.png", "fig2_financed_emissions_bank_year.png", "fig3_estimate_ranges.png",
              "fig4_estimate_vs_published.png", "fig5_disclosure_grid.png"]:
        p = ROOT / "figures" / f
        _need(p)
        assert p.stat().st_size > 10_000


def test_results_document():
    p = ROOT / "docs" / "results.md"
    _need(p)
    t = p.read_text(encoding="utf-8")
    for s in ["## RQ1", "## RQ2", "## RQ3", "## RQ4", "## Limitations", "## What the study cannot claim",
              "It does not reflect measured physical emissions", "including the naira value of foreign-currency loans"]:
        assert s in t, s


def test_plan_records_phase4_additions():
    plan = (ROOT / "docs" / "analysis_plan.md").read_text(encoding="utf-8")
    assert "Sensitivity flag (reporting rule)" in plan and "Constant 2022 naira (descriptive)" in plan
    assert "Change over time (descriptive)" in plan


@pytest.mark.parametrize("manifest", ["phase1b_outputs_manifest.json", "phase2a_outputs_manifest.json",
                                      "phase2b_outputs_manifest.json", "phase3_outputs_manifest.json"])
def test_earlier_outputs_unchanged(manifest):
    man = INTERIM / manifest
    _need(man)
    for f, h in json.loads(man.read_text())["sha256"].items():
        assert hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h, f
