"""Checks on the Phase 1b outputs (skipped if the outputs have not been built)."""

from pathlib import Path

import pandas as pd
import pytest

from bank_emissions.phase1b_config import RESIDUAL_LABEL

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "data" / "processed" / "exposures_by_sector.csv"
SAMPLE = ROOT / "data" / "processed" / "sample.csv"
TOTALS = ROOT / "data" / "processed" / "loans_totals.csv"

pytestmark = pytest.mark.skipif(not (EXP.exists() and SAMPLE.exists()), reason="Phase 1b outputs not built")


@pytest.fixture(scope="module")
def exp():
    return pd.read_csv(EXP)


def test_main_spec_has_one_level_and_basis_per_bank_year(exp):
    m = exp[exp.main_spec]
    assert (m.groupby(["bank", "year"])[["level", "basis"]].nunique() == 1).all().all()


def test_access_2025_residual_closes_to_printed_total(exp):
    m = exp[(exp.bank == "ACCESSCORP") & (exp.year == 2025) & exp.main_spec]
    tot = pd.read_csv(TOTALS)
    t = tot[(tot.bank == "ACCESSCORP") & (tot.year == 2025) & (tot.level == "group")].total_printed.iloc[0]
    assert abs(m.amount_printed.sum() - t) < 0.5
    res = m[m.printed_category == RESIDUAL_LABEL]
    assert len(res) == 1 and res.source_role.iloc[0].startswith("computed residual")


def test_stanbic_2023_main_spec_is_the_comparative(exp):
    g = exp[(exp.bank == "STANBIC") & (exp.year == 2023)]
    main = g[g.main_spec]
    assert set(main.source_role) == {"comparative from the following year's report (main specification)"}
    assert set(main.basis) == {"gross"} and set(main.level) == {"group"}
    assert not g[g.source_role == "extracted"].main_spec.any()
    assert abs(main.amount_printed.sum() - 2_091_137) < 0.5


def test_deviations_recorded_in_sample():
    s = pd.read_csv(SAMPLE).set_index(["bank", "year"])
    for key in [("STANBIC", 2023), ("ACCESSCORP", 2025), ("FIDELITYBK", 2020)]:
        assert "deviation" in s.loc[key, "status"] and isinstance(s.loc[key, "deviation"], str)
    assert s.loc[("FIDELITYBK", 2020), "main_level"] == "bank"
    assert s.loc[("FIDELITYBK", 2023), "main_level"] == "group"


def test_carrying_basis_accepted_for_gtco_and_uba():
    s = pd.read_csv(SAMPLE)
    for bank in ("GTCO", "UBA"):
        assert set(s[s.bank == bank].main_basis) == {"carrying"}
