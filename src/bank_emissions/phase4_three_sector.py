"""Share of financed emissions in transport + power + upstream oil and gas
under the main specification, each of the 17 fixed sensitivities (S1-S6) and
the post-results check S7; balanced panel, pooled 2020-2024.

A line counts towards a sector by its target intensity group in that
specification (so S3j moves downstream lending to oil refining, S3g moves
undivided oil and gas to upstream, and so on).

Writes data/processed/three_sector_share_by_sensitivity.csv.

    python -m bank_emissions.phase4_three_sector
"""

from __future__ import annotations

import pandas as pd

from . import phase3_estimate as p3
from .phase1b_extract import PROCESSED

TOP = {"transport_share": p3.TRANSPORT, "power_share": p3.POWER, "upstream_share": p3.OIL_UP}


def _shares(lines: pd.DataFrame, value: str = "tco2e") -> dict:
    tot = lines[value].sum()
    out = {k: lines.loc[lines.target == g, value].sum() / tot for k, g in TOP.items()}
    out["three_sector_share"] = sum(out.values())
    out["total_tco2e"] = tot
    return out


def build() -> pd.DataFrame:
    d = p3.load()
    main = p3.apply_intensity(p3.expand(p3.main_rows(d["exp"]), d["cw"], d["splits"]),
                              p3.intensity_table(d["si"], "main"))
    _, used = p3.run_sensitivities(d, main)
    by = pd.read_csv(PROCESSED / "financed_emissions_bank_year.csv")
    panel = set(by[by.in_balanced_panel].bank)

    def sub(ln):
        return ln[ln.bank.isin(panel) & ln.year.isin(p3.PERIOD_YEARS)]

    rows = [dict(specification="main", description="main specification", status="fixed plan", **_shares(sub(main)))]
    for s in p3.SENSITIVITIES:
        if s not in used:
            continue
        note = "fixed plan"
        if s == "S3j":
            note = "fixed plan; driven by the oil-refining intensity (reported separately)"
        rows.append(dict(specification=s, description=p3.SENS_DESC[s], status=note, **_shares(sub(used[s]))))
    # S7 (post-results): transport intensity excluding passenger cars
    it = pd.read_csv(PROCESSED / "postresults_s7_intensity.csv").set_index("year").intensity_s7_t_per_million / 1e6
    s7 = sub(main).copy()
    tr = s7.target == p3.TRANSPORT
    s7.loc[tr, "tco2e"] = s7.loc[tr, "exposure_naira"] * s7.loc[tr, "year"].map(it)
    rows.append(dict(specification="S7", description="transport intensity excluding passenger cars (1.A.3.b.i)",
                     status="post-results check, not part of the fixed plan", **_shares(s7)))
    df = pd.DataFrame(rows)
    df.insert(1, "basis", "balanced panel, 2020-2024 pooled")
    return df


def main() -> int:
    df = build()
    df.to_csv(PROCESSED / "three_sector_share_by_sensitivity.csv", index=False)
    print(df.assign(three_sector_share=(df.three_sector_share * 100).round(1))[
        ["specification", "three_sector_share", "status"]].to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
