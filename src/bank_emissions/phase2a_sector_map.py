"""Phase 2a, step 2: common sectors -> BTR1 categories and NBS activities (plan section 4).

Writes data/processed/btr1_nbs_sector_map.csv with two kinds of row:

- row_type 'common sector': each common sector of plan section 4 (and the two
  rule targets, economy-wide average and services) with the BTR1/NID
  categories and NBS activities that define it, the intensity group it falls
  in, and the reason;
- row_type 'inventory category not assigned': BTR1 categories that no common
  sector takes, with the reason, so that every inventory tonne is accounted for.

Checks (data/interim/sector_map_checks.csv): every BTR1 leaf category used
appears exactly once (assigned or not assigned), and every NBS activity 1-46
is assigned to exactly one intensity group. No intensity is computed.

    python -m bank_emissions.phase2a_sector_map
"""

from __future__ import annotations

import pandas as pd

from .phase1b_extract import INTERIM, PROCESSED
from .phase2a_crosswalk import (AGRI, CONSTR, ECONOMY_WIDE, MANUF, MINING, OIL_UP, POWER, REFINING, SERVICES,
                                TRANSPORT, WATER)

# Intensity groups. Plan section 4: where a split is not printed for every year,
# the sectors are merged rather than split by assumption. NID Table 3.18 (PDF
# p. 70) splits 1.A.2 into iron and steel, chemicals, non-metallic minerals and
# 'other - non specified' only: no construction and no mining sub-category. So
# manufacturing, construction and non-oil mining form one intensity group.
MCM = "Manufacturing, construction and non-oil mining (merged)"

MAP = [
    dict(common_sector=AGRI, intensity_group=AGRI,
         btr1_codes="3 (3.A-3.J);1.A.4.c;1.B.1.b", nid_tables="Table 3.41 (p. 90); Table 3.59 (p. 102)",
         nbs_activities="1;2;3;4",
         sensitivity="S5 adds 4 (LULUCF)", status="ok",
         reason="plan section 4 table: 3.A-3.H (3.I and 3.J are not estimated); NBS crop production, livestock, "
                "forestry, fishing. Signed off 2026-11-05: farm fuel use (1.A.4.c) and charcoal production "
                "(1.B.1.b, fuel transformation) are added to agriculture and forestry"),
    dict(common_sector=OIL_UP, intensity_group=OIL_UP,
         btr1_codes="1.B.2;1.A.1.c", nid_tables="Table 3.9 (p. 64)", nbs_activities="5",
         sensitivity="", status="ok",
         reason="Signed off 2026-11-05: 1.A.1.c accepted. Plan: 1.B.2 plus energy-industry combustion in fuel "
                "extraction if separable. NID Table 3.9 prints "
                "1.A.1.c 'Manufacture of solid fuels and other energy industries' every year; its activity data "
                "(Table 3.12) are natural gas only, consistent with field use in oil and gas extraction, but the "
                "NID description also names charcoal production"),
    dict(common_sector=REFINING, intensity_group=REFINING,
         btr1_codes="1.A.1.b", nid_tables="Table 3.9 (p. 64)", nbs_activities="9",
         sensitivity="", status="ok",
         reason="petroleum refining combustion, separable every year in NID Table 3.9 (zero in 2020); NBS oil "
                "refining. Fugitive emissions from refining stay in 1.B.2 (plan)"),
    dict(common_sector=POWER, intensity_group=POWER,
         btr1_codes="1.A.1.a", nid_tables="Table 3.9 (p. 64)", nbs_activities="22",
         sensitivity="", status="ok",
         reason="public electricity and heat production, separable every year in NID Table 3.9; NBS electricity, "
                "gas, steam and air conditioning supply"),
    dict(common_sector=MANUF, intensity_group=MCM,
         btr1_codes="1.A.2;2.A;2.B;2.C", nid_tables="Table 3.18 (p. 70)", nbs_activities="10-21",
         sensitivity="", status="ok",
         reason="plan section 4 table (1.A.2 and 2.A-2.C; NBS manufacturing excluding oil refining). Merged with "
                "construction and non-oil mining because 1.A.2 has no construction or mining sub-category in the NID"),
    dict(common_sector=CONSTR, intensity_group=MCM,
         btr1_codes="(in 1.A.2)", nid_tables="Table 3.18 (p. 70)", nbs_activities="24",
         sensitivity="", status="ok",
         reason="plan: construction sub-category of 1.A.2 if separable in the NID. Not separable (Table 3.18), so "
                "merged into the manufacturing group as the plan requires"),
    dict(common_sector=MINING, intensity_group=MCM,
         btr1_codes="(in 1.A.2);1.B.1.a", nid_tables="Table 3.18 (p. 70); Table 3.59 (p. 102)",
         nbs_activities="6;7;8",
         sensitivity="S3l moves Stanbic 'Mining' here", status="ok",
         reason="plan: share of 1.A.2 as separable in the NID. Not separable (Table 3.18), so merged into the "
                "manufacturing group as the plan requires; NBS coal mining, metal ores, quarrying. Signed off "
                "2026-11-05: coal mining and handling (1.B.1.a) is added to the non-oil mining (merged) group"),
    dict(common_sector=TRANSPORT, intensity_group=TRANSPORT,
         btr1_codes="1.A.3", nid_tables="", nbs_activities="27-32",
         sensitivity="", status="ok",
         reason="plan section 4 table; NBS transportation and storage section (road, rail and pipelines, water, "
                "air, transport services, post and courier). 1.A.3 includes private road vehicles (limitation)"),
    dict(common_sector=WATER, intensity_group=WATER,
         btr1_codes="5 (5.A-5.E)", nid_tables="", nbs_activities="23",
         sensitivity="", status="ok",
         reason="plan section 4 table: 5.A-5.D (5.B and 5.E not estimated). 5.D includes domestic wastewater "
                "(limitation)"),
    dict(common_sector=SERVICES, intensity_group=SERVICES,
         btr1_codes="1.A.4.a", nid_tables="Table 3.41 (p. 90)", nbs_activities="25;26;33-46",
         sensitivity="S3a (commerce), S3d (government), S3e (finance) change the rule, not this map",
         status="ok",
         reason="plan: 1.A.4 commercial and institutional, allocated across service activities by GDP share, so "
                "every service activity has the same intensity (limitation); separable every year in NID Table 3.41. "
                "NBS trade, accommodation, information and communication, arts, finance and insurance, real estate, "
                "professional, administrative, public administration, education, health, other services"),
    dict(common_sector=ECONOMY_WIDE, intensity_group=ECONOMY_WIDE,
         btr1_codes="Total CO2 equivalent emissions without LULUCF", nid_tables="", nbs_activities="1-46",
         sensitivity="S3b zero; S3f residual -> oil and gas downstream", status="ok",
         reason="plan section 4: BTR1 national total excluding LULUCF divided by total GDP at current basic prices"),
]

NOT_ASSIGNED = [
    dict(btr1_codes="1.A.4.b", status="ok",
         reason="residential combustion: not attributed (plan section 4, individuals rule)"),
    dict(btr1_codes="4", status="ok", reason="LULUCF: excluded in the main specification, added to agriculture "
                                              "in sensitivity S5 (plan section 7)"),
    dict(btr1_codes="1.A.5;1.C;2.D;2.E;2.F;2.G;2.H;6", status="ok",
         reason="not estimated in the inventory (notation keys NE, NO, NA, FX); no emissions to assign"),
]

# leaf categories of the inventory used by the map (Table 2.10 or NID)
LEAVES = ["1.A.1.a", "1.A.1.b", "1.A.1.c", "1.A.2", "1.A.3", "1.A.4.a", "1.A.4.b", "1.A.4.c", "1.A.5",
          "1.B.1.a", "1.B.1.b", "1.B.2", "1.C", "2.A", "2.B", "2.C", "2.D", "2.E", "2.F", "2.G", "2.H",
          "3", "4", "5", "6"]


def _codes(s: str) -> list[str]:
    """'3 (3.A-3.J);1.A.4.c' -> ['3', '1.A.4.c']; '(in 1.A.2);1.B.1.a' -> ['1.B.1.a']."""
    out = []
    for item in s.split(";"):
        item = item.strip()
        if not item or item.startswith("("):
            continue
        out.append(item.split(" (")[0].strip())
    return out


def _nbs(s: str) -> list[int]:
    out = []
    for part in s.split(";"):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = [dict(row_type="common sector", **m) for m in MAP]
    rows += [dict(row_type="inventory category not assigned", common_sector="", intensity_group="",
                  nid_tables="", nbs_activities="", sensitivity="", **m) for m in NOT_ASSIGNED]
    df = pd.DataFrame(rows)[["row_type", "common_sector", "intensity_group", "btr1_codes", "nid_tables",
                             "nbs_activities", "sensitivity", "status", "reason"]]
    nbs = pd.read_csv(PROCESSED / "nbs_gdp_by_activity.csv")
    names = nbs.drop_duplicates("activity_no").set_index("activity_no").activity
    df["nbs_activity_names"] = [", ".join(names[n] for n in _nbs(s)) if s and s != "1-46" else
                                ("all 46 activities" if s == "1-46" else "") for s in df.nbs_activities]
    # checks
    checks = []
    production = df[(df.row_type == "common sector") & (df.common_sector != ECONOMY_WIDE)]
    used = [c for s in production.btr1_codes for c in _codes(s)]
    unassigned = [c for s in df[df.row_type != "common sector"].btr1_codes for c in _codes(s)]
    for leaf in LEAVES:
        n = used.count(leaf) + unassigned.count(leaf)
        checks.append(dict(check="btr1_leaf_accounted_once", item=leaf, result="pass" if n == 1 else "fail",
                           detail=f"assigned {used.count(leaf)}, listed as not assigned {unassigned.count(leaf)}"))
    groups = production.drop_duplicates(["intensity_group", "nbs_activities"])
    nbs_used = [n for s in groups.nbs_activities for n in _nbs(s)]
    for n in range(1, 47):
        checks.append(dict(check="nbs_activity_in_one_group", item=n,
                           result="pass" if nbs_used.count(n) == 1 else "fail",
                           detail=f"{names[n]}: in {nbs_used.count(n)} intensity group(s)"))
    return df, pd.DataFrame(checks)


def main() -> int:
    df, ch = build()
    df.to_csv(PROCESSED / "btr1_nbs_sector_map.csv", index=False)
    ch.to_csv(INTERIM / "sector_map_checks.csv", index=False)
    print(f"{len(df)} rows; checks: {ch.result.value_counts().to_dict()}")
    bad = ch[ch.result != "pass"]
    if len(bad):
        print(bad.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
