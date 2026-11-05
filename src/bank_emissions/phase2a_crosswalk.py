"""Phase 2a, step 1: sector crosswalk (plan section 4).

Maps every printed category in data/processed/exposures_by_sector.csv (one row
per bank and label as printed, including the computed 'unallocated (printed
total residual)' row) to the plan's common sectors and rules, and writes
data/processed/sector_crosswalk.csv.

Labels are matched on a letters-only key (so 'Oil&gas', 'Oil & gas' and
'OIL AND GAS' are one key); bank-specific overrides come first because some
labels mean different things at different banks. Rows whose mapping is a
judgment the plan does not settle are marked 'review'. No intensity is used
here.

    python -m bank_emissions.phase2a_crosswalk
"""

from __future__ import annotations

import re

import pandas as pd

from .phase1b_extract import PROCESSED

# Common sectors (plan section 4)
AGRI = "Agriculture, forestry and fishing"
OIL_UP = "Oil and gas, upstream"
REFINING = "Oil refining"
POWER = "Power (electricity and gas supply)"
MINING = "Mining and quarrying (non-oil)"
MANUF = "Manufacturing"
CONSTR = "Construction"
TRANSPORT = "Transport and storage"
WATER = "Water, waste and sewerage"
SERVICES = "Services"
COMMON_SECTORS = [AGRI, OIL_UP, REFINING, POWER, MINING, MANUF, CONSTR, TRANSPORT, WATER, SERVICES]

# Rule-only targets (plan section 4, "categories that do not map to a production activity")
ECONOMY_WIDE = "(economy-wide average)"
ZERO = "(zero direct intensity)"
NOT_LOAN = "(not a loan exposure)"

# rule, sensitivity group
MAPPED = ("mapped", "")
COMMERCE = ("services", "S3a")
OTHER = ("economy-wide", "S3b")
INDIVIDUALS = ("zero", "S3c")
GOVERNMENT = ("services", "S3d")
FINANCE = ("services", "S3e")


def key(label: str) -> str:
    """Letters-only key; '&' is read as 'and' ('Oil & gas' = 'Oil and gas')."""
    return re.sub(r"[^a-z]", "", label.lower().replace("&", " and "))


def _r(sector, rule, status, reason, services_activity=""):
    return dict(common_sector=sector, rule=rule[0], sensitivity_group=rule[1], status=status, reason=reason,
                services_activity=services_activity)


# Mappings by letters-only key. Reasons cite the plan section 4 table or rule.
GENERIC = {
    # agriculture
    "agriculture": _r(AGRI, MAPPED, "ok", "crop, livestock, forestry and fishing borrowers; plan section 4 table"),
    "agricultureforestryandfishing": _r(AGRI, MAPPED, "ok", "ISIC section A label; plan section 4 table"),
    # oil and gas
    "oilandgasupstream": _r(OIL_UP, MAPPED, "ok", "upstream exploration and production; NBS crude petroleum and natural gas"),
    "oilandgas": _r(OIL_UP, MAPPED, "review",
                    "undivided oil and gas: the label covers upstream, downstream and services; mapped to upstream, the "
                    "largest part of the activity in the national accounts, but the bank's split is not printed"),
    "oilandgasdownstream": _r(SERVICES, COMMERCE, "review",
                              "downstream lending in Nigerian banks finances petroleum-product import, distribution and "
                              "retail (trade); mapped to services under the commerce rule. Alternative: oil refining",
                              "trade"),
    "oilandgasservices": _r(OIL_UP, MAPPED, "review",
                            "oilfield services (drilling, support) are part of the extraction value chain; mapped to "
                            "upstream. Alternative: services"),
    "crudeoilrefining": _r(REFINING, MAPPED, "ok", "petroleum refining; NBS oil refining"),
    # power and utilities
    "power": _r(POWER, MAPPED, "ok", "electricity generation and distribution; NBS electricity, gas, steam and air conditioning"),
    "electricity": _r(POWER, MAPPED, "ok", "electricity supply; NBS electricity, gas, steam and air conditioning"),
    "powerandenergy": _r(POWER, MAPPED, "ok",
                         "power and energy in Nigerian bank sector notes is the power sector (generation, distribution, "
                         "gas-to-power); oil and gas is printed separately by every bank using this label"),
    "utilities": _r(POWER, MAPPED, "review",
                    "utilities not split between electricity and water; mapped to power (the larger utility in the "
                    "national accounts). Alternative: water, waste and sewerage"),
    "otherpublicutilities": _r(WATER, MAPPED, "review",
                               "printed next to a separate 'Power' row, so 'other' utilities are taken as water, "
                               "sewerage and waste. Alternative: power"),
    "watersupplysewagewastemanagementandremediationactivities": _r(WATER, MAPPED, "ok", "ISIC section E label"),
    "watersupplysewagewastemgtandremedial": _r(WATER, MAPPED, "ok", "ISIC section E label (abbreviated)"),
    # mining
    "mining": _r(MINING, MAPPED, "ok", "solid minerals; the bank prints oil and gas separately"),
    "miningandquarrying": _r(MINING, MAPPED, "ok", "solid minerals; the bank prints oil and gas separately"),
    # manufacturing
    "manufacturing": _r(MANUF, MAPPED, "ok", "plan section 4 table"),
    "othermanufacturingindustries": _r(MANUF, MAPPED, "ok", "manufacturing sub-category"),
    "basicmetalproducts": _r(MANUF, MAPPED, "ok", "manufacturing sub-category (basic metals)"),
    "cement": _r(MANUF, MAPPED, "ok", "manufacturing sub-category (cement; NBS cement)"),
    "flourmillsandbakeries": _r(MANUF, MAPPED, "ok", "manufacturing sub-category (food)"),
    "foodmanufacturing": _r(MANUF, MAPPED, "ok", "manufacturing sub-category (food, beverage and tobacco)"),
    "steelrollingmills": _r(MANUF, MAPPED, "ok", "manufacturing sub-category (basic metals)"),
    "conglomerate": _r(MANUF, MAPPED, "review",
                       "listed under manufacturing sub-categories in the Access table; conglomerates also trade and "
                       "hold services businesses"),
    # construction and real estate
    "construction": _r(CONSTR, MAPPED, "ok", "plan section 4 table"),
    "constructionrealestate": _r(CONSTR, MAPPED, "review",
                                 "combined construction and real estate; real estate is a service activity. Mapped "
                                 "to construction; the split is not printed. Alternative: services"),
    "constructionandrealestate": _r(CONSTR, MAPPED, "review",
                                    "combined construction and real estate; real estate is a service activity. "
                                    "Mapped to construction; the split is not printed. Alternative: services"),
    "realestateandconstruction": _r(CONSTR, MAPPED, "review",
                                    "combined real estate and construction; mapped to construction; the split is "
                                    "not printed. Alternative: services"),
    "realestateconstruction": _r(CONSTR, MAPPED, "review",
                                 "combined real estate and construction; mapped to construction; the split is not "
                                 "printed. Alternative: services"),
    "realestate": _r(SERVICES, MAPPED, "ok", "real estate activities are a service activity in the NBS accounts", "real estate"),
    "realestateactivities": _r(SERVICES, MAPPED, "ok", "service activity in the NBS accounts", "real estate"),
    # transport
    "transportation": _r(TRANSPORT, MAPPED, "ok", "plan section 4 table"),
    "transportationandstorage": _r(TRANSPORT, MAPPED, "ok", "ISIC section H label"),
    "transportstorageanddistribution": _r(TRANSPORT, MAPPED, "ok",
                                          "transport, storage and distribution (logistics); plan section 4 table"),
    "infotelecomsandtransport": _r(TRANSPORT, MAPPED, "review",
                                "combined information, telecoms and transport; the split is not printed. Mapped to "
                                "transport. Alternative: services"),
    # commerce (rule: services intensity; S3a economy-wide)
    "generalcommerce": _r(SERVICES, COMMERCE, "ok", "trade; plan section 4 rule for general commerce", "trade"),
    "commerce": _r(SERVICES, COMMERCE, "ok", "trade; plan section 4 rule for general commerce", "trade"),
    "wholesaleandretailtrade": _r(SERVICES, COMMERCE, "ok", "trade; plan section 4 rule for general commerce", "trade"),
    "retailservices": _r(SERVICES, COMMERCE, "review",
                         "First HoldCo prints 'Retail services' in both its retail and corporate portfolios; read "
                         "as retail trade and services businesses. Alternative: individuals (zero)", "trade"),
    # other services (mapped; services intensity)
    "education": _r(SERVICES, MAPPED, "ok", "service activity", "education"),
    "communication": _r(SERVICES, MAPPED, "ok", "information and communication", "information and communication"),
    "informationandcommunication": _r(SERVICES, MAPPED, "ok", "ISIC section J", "information and communication"),
    "infotainment": _r(SERVICES, MAPPED, "ok", "information, communication and entertainment", "information and communication"),
    "professionalscientificandtechnicalactivities": _r(SERVICES, MAPPED, "ok", "ISIC section M", "professional services"),
    "professionalservices": _r(SERVICES, MAPPED, "ok", "service activity", "professional services"),
    "administrativeandsupportservices": _r(SERVICES, MAPPED, "ok", "ISIC section N", "administrative and support"),
    "administrativeandsupportserviceactivities": _r(SERVICES, MAPPED, "ok", "ISIC section N", "administrative and support"),
    "businessservices": _r(SERVICES, MAPPED, "ok", "service activity", "professional services"),
    "healthcare": _r(SERVICES, MAPPED, "ok", "human health", "health"),
    "humanhealthandsocialworkactivities": _r(SERVICES, MAPPED, "ok", "ISIC section Q", "health"),
    "hospitality": _r(SERVICES, MAPPED, "ok", "accommodation and food service", "accommodation and food"),
    "hotelsrestaurantsandtourism": _r(SERVICES, MAPPED, "ok", "accommodation and food service", "accommodation and food"),
    "recreation": _r(SERVICES, MAPPED, "ok", "arts, entertainment and recreation", "arts and recreation"),
    "artsentertainmentandrecreation": _r(SERVICES, MAPPED, "ok", "ISIC section R", "arts and recreation"),
    "communitysocialandpersonalservices": _r(SERVICES, MAPPED, "ok", "other service activities", "other services"),
    # government (rule: services intensity; S3d zero)
    "government": _r(SERVICES, GOVERNMENT, "ok", "plan section 4 rule for government", "public administration"),
    "governments": _r(SERVICES, GOVERNMENT, "ok", "plan section 4 rule for government", "public administration"),
    "publicsector": _r(SERVICES, GOVERNMENT, "ok", "plan section 4 rule for government", "public administration"),
    "governmentincludingcentralbank": _r(SERVICES, GOVERNMENT, "ok",
                                         "plan section 4 rule for government (the loans column holds loans to "
                                         "government; central bank balances are another column)",
                                         "public administration"),
    # finance (rule: services intensity; S3e zero)
    "financeandinsurance": _r(SERVICES, FINANCE, "ok", "plan section 4 rule for finance and insurance", "finance and insurance"),
    "financialintermediariesandinsurance": _r(SERVICES, FINANCE, "ok", "plan section 4 rule for finance and insurance",
                                           "finance and insurance"),
    "capitalmarket": _r(SERVICES, FINANCE, "ok", "financial institutions; plan section 4 rule for finance",
                        "finance and insurance"),
    "capitalmarketandfinancialinstitution": _r(SERVICES, FINANCE, "ok", "plan section 4 rule for finance",
                                            "finance and insurance"),
    # individuals (rule: zero; S3c economy-wide)
    "individual": _r(ZERO, INDIVIDUALS, "ok", "plan section 4 rule for individuals"),
    "consumer": _r(ZERO, INDIVIDUALS, "ok", "plan section 4 rule for consumer lending"),
    "consumercredit": _r(ZERO, INDIVIDUALS, "ok", "plan section 4 rule for consumer lending"),
    "privatehouseholds": _r(ZERO, INDIVIDUALS, "ok", "plan section 4 rule for individuals"),
    "mortgage": _r(ZERO, INDIVIDUALS, "review",
                   "printed as a separate sector with no borrower type; read as residential mortgages to "
                   "individuals (zero rule). Alternative: services (real estate)"),
    # other (rule: economy-wide; S3b zero)
    "others": _r(ECONOMY_WIDE, OTHER, "ok", "plan section 4 rule for 'Other'"),
    "other": _r(ECONOMY_WIDE, OTHER, "ok", "plan section 4 rule for 'Other'"),
    "generalothers": _r(ECONOMY_WIDE, OTHER, "ok", "plan section 4 rule for 'Other'"),
    "noninterestbanking": _r(ECONOMY_WIDE, OTHER, "ok", "product label named in the plan section 4 rule for 'Other'"),
    "general": _r(ECONOMY_WIDE, OTHER, "review",
                  "'General' is not defined in the reports; treated as 'Other'. It is large at some banks (Access, "
                  "UBA) and may hold consumer or retail lending (alternative: individuals, zero)"),
    "unallocatedprintedtotalresidual": dict(
        common_sector=ECONOMY_WIDE, rule="economy-wide", sensitivity_group="S3b;S3f", status="ok",
        reason="computed residual of the omitted 'Oil And Gas - downstream' row (Access FY2025); author decision "
               "2026-11-04: plan 'Other' rule; S3f assigns it to the common sector of Access 'Oil And Gas - downstream', "
               "which the 2026-11-05 sign-off keeps as services (trade, commerce rule)",
        services_activity=""),
    # not loans to customers
    "centralbankbalancerestricted": _r(NOT_LOAN, ("not a loan", ""), "ok",
                                       "restricted central bank balances; printed with a dash in the loans column "
                                       "(amount zero in every year)"),
}

OVERRIDES = {
    ("STANBIC", "mining"): _r(OIL_UP, MAPPED, "review",
                              "Stanbic prints no oil and gas row; 'Mining' (ISIC section B) then includes crude oil and "
                              "gas extraction, which dominates Nigerian mining. Mapped to oil and gas upstream. "
                              "Alternative: mining and quarrying (non-oil)"),
    ("STANBIC", "insurance"): _r(SERVICES, FINANCE, "ok",
                                 "the label is 'Financial intermediaries & insurance' printed over two lines; the "
                                 "first line is cut off by the extraction (full label in the FY2024 report)",
                                 "finance and insurance"),
    ("UNITYBNK", "utilities"): _r(WATER, MAPPED, "review",
                                  "Unity prints 'Power and Energy' separately, so 'Utilities' is taken as water, "
                                  "sewerage and waste. Alternative: power"),
}


# ---------------------------------------------------------------------------
# Author sign-off, 2026-11-05 (recorded in docs/analysis_plan.md section 4).
# Applied on top of the proposed mappings above; every row that was 'review'
# becomes 'ok' with the decision as its reason.

SIGNOFF_DATE = "2026-11-05"
SPLIT = "(split by shares; see sector_crosswalk_splits.csv)"
OIL_KEYS = {"upstream": "oilandgasupstream", "downstream": "oilandgasdownstream", "services": "oilandgasservices"}
OIL_SPLIT_BANKS = ["ACCESSCORP", "FCMB"]  # the banks that print the upstream/downstream/services split
COMBINED = {
    # label key -> (component, common sector, services activity, NBS activity numbers)
    "constructionandrealestate": [("construction", CONSTR, "", [24]), ("real estate", SERVICES, "real estate", [40])],
    "constructionrealestate": [("construction", CONSTR, "", [24]), ("real estate", SERVICES, "real estate", [40])],
    "realestateandconstruction": [("construction", CONSTR, "", [24]), ("real estate", SERVICES, "real estate", [40])],
    "realestateconstruction": [("construction", CONSTR, "", [24]), ("real estate", SERVICES, "real estate", [40])],
    "infotelecomsandtransport": [("transport", TRANSPORT, "", list(range(27, 33))),
                                 ("information and telecommunications", SERVICES, "information and communication",
                                  list(range(33, 37)))],
}
OIL_COMPONENTS = [  # component, common sector, rule, sensitivity group, services activity
    ("upstream", OIL_UP, "mapped", "", ""),
    ("downstream", SERVICES, "services", "S3a;S3j", "trade"),
    ("services", SERVICES, "mapped", "S3i", "oilfield services"),
]


def _signed(base: dict, reason: str, sensitivity: str = "", **change) -> dict:
    m = dict(base, **change)
    m["status"] = "ok"
    m["reason"] = f"Signed off {SIGNOFF_DATE}: {reason}. Proposal: {base['reason']}"
    if sensitivity:
        m["sensitivity_group"] = ";".join(x for x in (m.get("sensitivity_group", ""), sensitivity) if x)
    return m


def signoff(bank: str, k: str, m: dict) -> dict:
    if m["status"] != "review":
        return m
    if k == "oilandgas":
        return _signed(m, "undivided oil and gas is split into upstream, downstream and services by the year's "
                          "average shares of the banks that print the split (Access, FCMB); S3g all upstream, "
                          "S3h all downstream", "S3g;S3h", common_sector=SPLIT, rule="split")
    if k == "oilandgasservices":
        return _signed(m, "oil and gas services mapped to services; S3i maps them to oil and gas upstream", "S3i",
                       common_sector=SERVICES, rule="mapped", services_activity="oilfield services")
    if k == "oilandgasdownstream":
        return _signed(m, "downstream kept as services (trade, commerce rule); S3j maps it to oil refining", "S3j")
    if k in COMBINED:
        alt = "construction" if k != "infotelecomsandtransport" else "transport"
        return _signed(m, f"combined category split by the NBS GDP shares of its two activities in the year "
                          f"(2025: 2024 shares, NBS 2025 not located); S3k maps it wholly to {alt}", "S3k",
                       common_sector=SPLIT, rule="split")
    if k == "general":
        return _signed(m, "kept as proposed: economy-wide average; sensitivity zero (S3b, the 'Other' rule)")
    if (bank, k) == ("STANBIC", "mining"):
        return _signed(m, "kept as proposed: oil and gas upstream; S3l maps it to non-oil mining", "S3l")
    if k == "utilities":
        return _signed(m, "kept as proposed (" + ("water, waste and sewerage" if bank == "UNITYBNK" else "power") + ")")
    if k == "otherpublicutilities":
        return _signed(m, "kept as proposed (water, waste and sewerage)")
    if k in ("retailservices", "conglomerate", "mortgage"):
        return _signed(m, "kept as proposed")
    raise KeyError(f"review row without a sign-off decision: {bank} {k}")


def oil_gas_shares(e: pd.DataFrame) -> pd.DataFrame:
    """Per year: each split bank's upstream/downstream/services shares (main
    specification) and their simple average. A bank-year is used only if it
    prints all three rows (Access FY2025 omits the downstream row, so 2025
    uses FCMB alone)."""
    m = e[e.main_spec & e.bank.isin(OIL_SPLIT_BANKS)].copy()
    m["k"] = m.printed_category.map(key)
    m = m[m.k.isin(OIL_KEYS.values())]
    rows = []
    for (bank, year), g in m.groupby(["bank", "year"]):
        amt = {c: g[g.k == k].amount_naira.sum() for c, k in OIL_KEYS.items()}
        printed = {c: (g.k == k).any() for c, k in OIL_KEYS.items()}
        tot = sum(amt.values())
        rows.append(dict(bank=bank, year=int(year), used=all(printed.values()),
                         pages=";".join(str(int(p)) for p in sorted(g.pdf_page.unique())),
                         source_file=g.source_file.iloc[0], basis=g.basis.iloc[0], level=g.level.iloc[0],
                         **{f"share_{c}": amt[c] / tot for c in OIL_KEYS},
                         note="" if all(printed.values()) else
                         "not used: " + ", ".join(c for c, p in printed.items() if not p) + " row not printed"))
    per_bank = pd.DataFrame(rows)
    avg = (per_bank[per_bank.used].groupby("year")[[f"share_{c}" for c in OIL_KEYS]].mean().reset_index())
    avg["banks_used"] = [";".join(per_bank[(per_bank.year == y) & per_bank.used].bank) for y in avg.year]
    return per_bank, avg


def combined_shares(years: list[int]) -> pd.DataFrame:
    """NBS GDP shares of the two activities of each combined category; 2025
    uses 2024 (NBS 2025 GDP by activity not located)."""
    nbs = pd.read_csv(PROCESSED / "nbs_gdp_by_activity.csv")
    rows = []
    for k, comps in COMBINED.items():
        for y in years:
            ny = min(y, int(nbs.year.max()))
            vals = {c: nbs[(nbs.year == ny) & nbs.activity_no.isin(acts)].gdp_current_basic_naira_million.sum()
                    for c, _, _, acts in comps}
            tot = sum(vals.values())
            for c, sec, act, acts in comps:
                rows.append(dict(label_key=k, year=y, component=c, common_sector=sec, services_activity=act,
                                 share=vals[c] / tot, nbs_year=ny, nbs_activities=";".join(map(str, acts))))
    return pd.DataFrame(rows)


def build_splits(cw: pd.DataFrame, e: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    per_bank, avg = oil_gas_shares(e)
    years = sorted(int(y) for y in e.year.unique())
    comb = combined_shares(years)
    rows = []
    for r in cw[cw.rule == "split"].itertuples():
        for y in (int(x) for x in r.years.split(";")):
            if r.label_key == "oilandgas":
                a = avg[avg.year == y].iloc[0]
                src = per_bank[(per_bank.year == y) & per_bank.used]
                source = "; ".join(f"{b.bank} {b.source_file} p. {b.pages}" for b in src.itertuples())
                for c, sec, rule, sens, act in OIL_COMPONENTS:
                    rows.append(dict(bank=r.bank, printed_category=r.printed_category, year=y, component=c,
                                     common_sector=sec, rule=rule, sensitivity_group=sens, services_activity=act,
                                     share=a[f"share_{c}"],
                                     share_basis=f"simple average of {a.banks_used.replace(';', ' and ')} "
                                                 f"shares (main specification)",
                                     share_source=source))
            else:
                for c in comb[(comb.label_key == r.label_key) & (comb.year == y)].itertuples():
                    rows.append(dict(bank=r.bank, printed_category=r.printed_category, year=y, component=c.component,
                                     common_sector=c.common_sector, rule="mapped", sensitivity_group="",
                                     services_activity=c.services_activity, share=c.share,
                                     share_basis=f"NBS GDP at current basic prices, {c.nbs_year}"
                                                 + (" (2025: 2024 shares)" if c.nbs_year != y else ""),
                                     share_source=f"data/processed/nbs_gdp_by_activity.csv, activities "
                                                  f"{c.nbs_activities} (NBS rebasing annex, PDF p. 7)"))
    return pd.DataFrame(rows), per_bank


def build() -> pd.DataFrame:
    e = pd.read_csv(PROCESSED / "exposures_by_sector.csv")
    main = e[e.main_spec]
    total_main = main.amount_naira.sum()
    rows = []
    for (bank, label), g in e.groupby(["bank", "printed_category"]):
        k = key(label)
        m = OVERRIDES.get((bank, k)) or GENERIC.get(k)
        if m is None:
            m = _r("", ("", ""), "review", "no mapping rule for this label")
        proposed = dict(m)
        m = signoff(bank, k, m)
        gm = main[(main.bank == bank) & (main.printed_category == label)]
        rows.append(dict(bank=bank, printed_category=label, label_key=k,
                         years=";".join(str(y) for y in sorted(g.year.unique())),
                         **m, proposed_sector=proposed["common_sector"], proposed_status=proposed["status"],
                         main_spec_naira=gm.amount_naira.sum(),
                         main_spec_share=gm.amount_naira.sum() / total_main))
    cw = pd.DataFrame(rows)
    return cw[["bank", "printed_category", "label_key", "years", "common_sector", "rule", "sensitivity_group",
               "services_activity", "status", "reason", "proposed_sector", "proposed_status",
               "main_spec_naira", "main_spec_share"]]


def main() -> int:
    e = pd.read_csv(PROCESSED / "exposures_by_sector.csv")
    cw = build()
    splits, per_bank = build_splits(cw, e)
    cw.to_csv(PROCESSED / "sector_crosswalk.csv", index=False)
    splits.to_csv(PROCESSED / "sector_crosswalk_splits.csv", index=False)
    per_bank.to_csv(PROCESSED.parent / "interim" / "oil_gas_split_shares.csv", index=False)
    print(f"{len(cw)} rows; status: {cw.status.value_counts().to_dict()}; split rows: {(cw.rule == 'split').sum()}; "
          f"split lines: {len(splits)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
