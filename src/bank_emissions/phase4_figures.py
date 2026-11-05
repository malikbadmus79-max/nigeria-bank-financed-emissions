"""Phase 4 (part 3): checking figures (simple matplotlib; final designs later).

    python -m bank_emissions.phase4_figures
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from .phase1b_extract import PROCESSED, ROOT  # noqa: E402
from .phase3_estimate import PERIOD_YEARS, SENSITIVITIES  # noqa: E402

FIG = ROOT / "figures"


def period_sensitivities() -> pd.DataFrame:
    """Per bank, 2020-2024 sums of main and each sensitivity (non-applicable
    bank-years keep the main value, as in the Phase 3 totals)."""
    s = pd.read_csv(PROCESSED / "financed_emissions_sensitivities.csv")
    by = s[s.row_type == "bank-year"].copy()
    by["year"] = by.year.astype(int)
    by = by[by.year.isin(PERIOD_YEARS)]
    for c in SENSITIVITIES:
        by[c] = by[c].fillna(by["main"])
    return by.groupby("bank")[["main"] + SENSITIVITIES].sum()


def fig_sector_shares():
    sy = pd.read_csv(PROCESSED / "financed_emissions_sector_year.csv")
    g = sy[(sy.total_type == "balanced panel") & sy.year.isin(PERIOD_YEARS)].groupby("reporting_sector")[
        ["exposure_naira", "tco2e"]].sum()
    g = g[g.exposure_naira > 0]
    g["loan_share"] = g.exposure_naira / g.exposure_naira.sum() * 100
    g["emission_share"] = g.tco2e / g.tco2e.sum() * 100
    g = g.sort_values("emission_share")
    y = np.arange(len(g))
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(y - 0.2, g.loan_share, 0.4, label="share of loans")
    ax.barh(y + 0.2, g.emission_share, 0.4, label="share of financed emissions")
    ax.set_yticks(y, g.index)
    ax.set_xlabel("% (balanced panel, 2020-2024 pooled, main specification)")
    ax.set_title("Loan share vs financed-emissions share by sector")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "fig1_loan_vs_emission_share.png", dpi=120)
    plt.close(fig)


def fig_bank_year():
    b = pd.read_csv(PROCESSED / "financed_emissions_bank_year.csv")
    p = b.pivot_table(index="year", columns="bank", values="tco2e") / 1e6
    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = np.zeros(len(p))
    for bank in p.columns:
        v = p[bank].fillna(0).values
        bars = ax.bar(p.index.astype(str), v, bottom=bottom, label=bank)
        for rect, yr in zip(bars, p.index):
            if yr == 2025:
                rect.set_hatch("//")
        bottom += v
    ax.set_ylabel("Mt CO2e (main specification)")
    ax.set_title("Financed emissions by bank and year (2025 provisional, hatched)")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(FIG / "fig2_financed_emissions_bank_year.png", dpi=120)
    plt.close(fig)


def fig_ranges():
    ps = period_sensitivities() / 1e6
    others = [c for c in SENSITIVITIES if c != "S3j"]
    ps = ps.sort_values("main")
    y = np.arange(len(ps))
    fig, ax = plt.subplots(figsize=(9, 6))
    lo, hi = ps[others].min(axis=1), ps[others].max(axis=1)
    ax.hlines(y, lo, hi, color="grey", lw=4, label="range of sensitivities excluding S3j")
    ax.plot(ps["main"], y, "ko", label="main")
    ax.plot(ps["S3j"], y, "rx", label="S3j (downstream to oil refining)")
    ax.set_yticks(y, ps.index)
    ax.set_xscale("log")
    ax.set_xlabel("Mt CO2e, 2020-2024 total (log scale)")
    ax.set_title("Main estimate and sensitivity range by bank")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig3_estimate_ranges.png", dpi=120)
    plt.close(fig)


def fig_published():
    c = pd.read_csv(PROCESSED / "published_comparison.csv")
    c = c[~c["item"].str.startswith("(consistency)") & ~c["item"].str.contains("Scope 3 \\(SASB")]
    labels = [f"{r.bank} {r.year}\n{'S1&2 ' if r.bank == 'UBA' else ''}{'p.37' if r.pdf_page == 37 else ''}"
              for r in c.itertuples()]
    x = np.arange(len(c))
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - 0.3, c.published_tco2e / 1e6, 0.2, label="published")
    ax.bar(x - 0.1, c.estimate_main_tco2e / 1e6, 0.2, label="estimate, main (group)")
    ax.bar(x + 0.1, c.estimate_bank_level_tco2e / 1e6, 0.2, label="estimate, bank level (S1)")
    ax.bar(x + 0.3, c.estimate_main_x_coverage_tco2e.fillna(0) / 1e6, 0.2, label="estimate x printed coverage (UBA)")
    ax.set_xticks(x, labels, fontsize=8)
    ax.set_yscale("log")
    ax.set_ylabel("Mt CO2e (log scale)")
    ax.set_title("Estimate vs published financed emissions (2025 estimate provisional)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig4_estimate_vs_published.png", dpi=120)
    plt.close(fig)


def fig_disclosure():
    d = pd.read_csv(PROCESSED / "disclosure_table.csv")
    order = list(dict.fromkeys(d.bank))
    items = list(dict.fromkeys(d["item"]))
    code = {"figure disclosed": 3, "metric disclosed in another unit": 2,
            "figure in a chart only (values not in the text layer)": 2, "statement only, no figure": 1,
            "not found in the documents opened": 0}
    grid = d.pivot(index="bank", columns="item", values="status").loc[order, items].map(code.get)
    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(grid.values, cmap="Greens", vmin=0, vmax=3)
    ax.set_xticks(range(len(items)), items, rotation=30, ha="right")
    ax.set_yticks(range(len(order)), order)
    cb = fig.colorbar(im, ticks=[0, 1, 2, 3])
    cb.ax.set_yticklabels(["not found", "statement only", "chart / other unit", "figure"])
    ax.set_title("Disclosure grid (latest annual report and sustainability report opened)")
    fig.tight_layout()
    fig.savefig(FIG / "fig5_disclosure_grid.png", dpi=120)
    plt.close(fig)


def main() -> int:
    FIG.mkdir(exist_ok=True)
    fig_sector_shares()
    fig_bank_year()
    fig_ranges()
    fig_published()
    fig_disclosure()
    print(sorted(p.name for p in FIG.glob("*.png")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
