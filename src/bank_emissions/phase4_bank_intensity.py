"""Bank-level financed-emissions intensity, 2022 (main specification).

For each bank in 2022: loans (main-specification exposure), financed emissions,
t CO2e per million naira of loans, and the reporting sector with the largest
share of the bank's financed emissions. Reads financed_emissions_main.csv only.

Writes data/processed/bank_intensity_2022.csv.

    python -m bank_emissions.phase4_bank_intensity
"""

from __future__ import annotations

import pandas as pd

from .phase1b_extract import PROCESSED

YEAR = 2022


def build(year: int = YEAR) -> pd.DataFrame:
    m = pd.read_csv(PROCESSED / "financed_emissions_main.csv")
    m = m[m.year == year]
    by = m.groupby("bank").agg(level=("level", "first"), basis=("basis", "first"),
                               loans_naira=("exposure_naira", "sum"), tco2e=("tco2e", "sum"))
    sec = m.groupby(["bank", "reporting_sector"]).tco2e.sum().reset_index()
    top = sec.loc[sec.groupby("bank").tco2e.idxmax()].set_index("bank")
    by["tco2e_per_million_naira"] = by.tco2e / by.loans_naira * 1e6
    by["largest_sector"] = top.reporting_sector
    by["largest_sector_share_of_bank_tco2e"] = top.tco2e / by.tco2e
    by.insert(0, "year", year)
    return by.reset_index().sort_values("tco2e_per_million_naira", ascending=False).reset_index(drop=True)


def main() -> int:
    df = build()
    df.to_csv(PROCESSED / "bank_intensity_2022.csv", index=False)
    pd.set_option("display.width", 200)
    print(df.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
