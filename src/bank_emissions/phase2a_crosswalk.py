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
               "2026-11-04: plan 'Other' rule; S3f assigns it to the common sector of Access 'Oil And Gas - downstream'",
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
        gm = main[(main.bank == bank) & (main.printed_category == label)]
        rows.append(dict(bank=bank, printed_category=label, label_key=k,
                         years=";".join(str(y) for y in sorted(g.year.unique())),
                         **m, main_spec_naira=gm.amount_naira.sum(),
                         main_spec_share=gm.amount_naira.sum() / total_main))
    cw = pd.DataFrame(rows)
    return cw[["bank", "printed_category", "label_key", "years", "common_sector", "rule", "sensitivity_group",
               "services_activity", "status", "reason", "main_spec_naira", "main_spec_share"]]


def main() -> int:
    cw = build()
    cw.to_csv(PROCESSED / "sector_crosswalk.csv", index=False)
    print(f"{len(cw)} rows; status: {cw.status.value_counts().to_dict()}; unmapped: {(cw.common_sector == '').sum()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
