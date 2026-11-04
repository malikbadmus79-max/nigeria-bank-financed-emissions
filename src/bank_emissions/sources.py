"""Source registry for Phase 0.

Every URL below was located during Phase 0 on the bank's own investor-relations
(IR) site or on the Nigerian Exchange (NGX) document library. Where an IR URL is
not listed, the IR site was blocked (HTTP 403), rendered its document list with
JavaScript only, or was unreachable from a script; the NGX filing of the audited
financial statements is used instead and the reason is recorded in IR_NOTES.
"""

YEARS = list(range(2020, 2026))

# NGX symbols used for each listed entity. Symbols changed when holding
# companies replaced the banks as the listed entity.
BANKS = {
    "ACCESSCORP": dict(name="Access Holdings Plc", ngx_symbols=["ACCESSCORP", "ACCESS"]),
    "ZENITHBANK": dict(name="Zenith Bank Plc", ngx_symbols=["ZENITHBANK"]),
    "GTCO": dict(name="Guaranty Trust Holding Company Plc", ngx_symbols=["GTCO", "GUARANTY"]),
    "UBA": dict(name="United Bank for Africa Plc", ngx_symbols=["UBA"]),
    "FIRSTHOLDCO": dict(name="First HoldCo Plc", ngx_symbols=["FIRSTHOLDCO", "FBNH"]),
    "FIDELITYBK": dict(name="Fidelity Bank Plc", ngx_symbols=["FIDELITYBK"]),
    "FCMB": dict(name="FCMB Group Plc", ngx_symbols=["FCMB"]),
    "STANBIC": dict(name="Stanbic IBTC Holdings Plc", ngx_symbols=["STANBIC"]),
    "STERLINGNG": dict(name="Sterling Financial Holdings Company Plc", ngx_symbols=["STERLINGNG", "STERLNBANK"]),
    "WEMABANK": dict(name="Wema Bank Plc", ngx_symbols=["WEMABANK"]),
    "UNITYBNK": dict(name="Unity Bank Plc", ngx_symbols=["UNITYBNK"]),
    "JAIZBANK": dict(name="Jaiz Bank Plc", ngx_symbols=["JAIZBANK"]),
    "ETI": dict(name="Ecobank Transnational Incorporated", ngx_symbols=["ETI"]),
}

# Listed-entity type as at the check date, from the NGX directory name and
# "nature of business" fields, and the symbol history visible in NGX filings.
ENTITY_TYPE = {
    "ACCESSCORP": "holding company (listed since 2022-03-28; Access Bank Plc, symbol ACCESS, was the listed entity before)",
    "ZENITHBANK": "bank (NGX nature of business: commercial banking)",
    "GTCO": "holding company (listed 2021-06-24; Guaranty Trust Bank Plc, symbol GUARANTY, filed FY2020)",
    "UBA": "bank (NGX nature of business: commercial banking)",
    "FIRSTHOLDCO": "holding company (formerly FBN Holdings Plc, symbol FBNH, until FY2023 filings)",
    "FIDELITYBK": "bank (NGX nature of business: commercial banking)",
    "FCMB": "holding company (FCMB Group Plc)",
    "STANBIC": "holding company (Stanbic IBTC Holdings Plc)",
    "STERLINGNG": "holding company (listed 2023-04-06; Sterling Bank Plc, symbol STERLNBANK, filed FY2020-FY2022)",
    "WEMABANK": "bank (NGX nature of business: commercial banking)",
    "UNITYBNK": "bank (NGX nature of business: commercial banking)",
    "JAIZBANK": "bank (non-interest; NGX Non-Interest Finance Board)",
    "ETI": "holding company incorporated and domiciled in Togo (ETI FY2025 statements, NGX filing, PDF p. 22); NGX nature of business: banking through subsidiaries and affiliates",
}

_GT ="https://gtco-plc.files.svdcdn.com/production/annual-reports/"
_FID = "https://www.fidelitybank.ng/documents/"
_ABP = "https://www.accessbankplc.com/access/media/Financial-Report/Annual%20Reports/"

# Annual reports found on IR sites: (symbol, year) -> URL
IR_ANNUAL_REPORTS = {
    ("ACCESSCORP", 2020): _ABP + "Annual-Report-2020.pdf",
    ("ACCESSCORP", 2021): _ABP + "2021-Annual-Report-Full.pdf",
    ("ACCESSCORP", 2022): "https://theaccesscorporation.com/wp-content/uploads/2023/07/ACCESS-HOLDINGS-PLCS-2022-ANNUAL-REPORT.pdf",
    ("ACCESSCORP", 2023): "https://theaccesscorporation.com/ACCESS-HOLDINGS-PLC-2023-ANNUAL-REPORT.pdf",
    ("ACCESSCORP", 2024): "https://theaccesscorporation.com/Access-holdco-2024-AR.pdf",
    ("ACCESSCORP", 2025): "https://theaccesscorporation.com/wp-content/uploads/2026/06/Access-Holding-plc-2025-Annual-Report.pdf",
    ("GTCO", 2020): _GT + "2020-annual-report/2020-Annual-Report.pdf?dm=1620654462",
    ("GTCO", 2021): _GT + "2021-annual-report/2021-ANNUAL-REPORT.pdf?dm=1648469950",
    ("GTCO", 2022): _GT + "2022-annual-report/2022-Annual-Report_2023-05-05-162627_yqbx.pdf?dm=1683303987",
    ("GTCO", 2023): _GT + "2023-annual-report/2023-Annual-Report.pdf?dm=1716814519",
    ("GTCO", 2024): _GT + "2024-annual-report/GTCO-FY-2024-Annual-Report_2025-04-15-073502_qpsd.pdf?dm=1744702504",
    ("GTCO", 2025): _GT + "2025-annual-report/GTCO-2025-Annual-Report_2026-04-30-093114_eecj.pdf?dm=1777541474",
    ("FIDELITYBK", 2020): _FID + "2020_Annual_report-Final_compressed.pdf",
    ("FIDELITYBK", 2021): _FID + "Fidelity-Bank-2021-Annual-report-final-compressed.pdf",
    ("FIDELITYBK", 2022): _FID + "Fidelity-Bank-Plc-2022-Annual-Report.pdf",
    ("FIDELITYBK", 2023): _FID + "Fidelity-Bank-2023-Annual-Report.pdf",
    ("FIDELITYBK", 2024): _FID + "2024-Fidelity-Bank-Annual-Report.pdf",
    ("FIDELITYBK", 2025): _FID + "Fidelity-Bank-Plc-2025-Annual-Report.pdf",
    ("STERLINGNG", 2022): "https://sterling.ng/files/2022%20Annual%20Report%20%20HD.pdf",
    ("STERLINGNG", 2023): "https://sterlingholdco.ng/files/Sterling%20Financial%20Holdings%20Company%20Annual%20Report%202023_.pdf",
    ("STERLINGNG", 2024): "https://sterlingholdco.ng/wp-content/uploads/2025/07/Sterling-Financial-Holdings-Company-Plc-Annual-Report-2024-.pdf",
    ("STERLINGNG", 2025): "https://sterlingholdco.ng/wp-content/uploads/2026/06/Sterling-HoldCo-AR-2025.pdf",
    ("FIRSTHOLDCO", 2021): "https://first-holdco.com/FBN_Holdings_Plc_FY_2021_Audited_Financial_Statements.pdf",
    ("FIRSTHOLDCO", 2025): "https://first-holdco.com/wp-content/uploads/2026/05/First-HoldCo-Plc-2025-Annual-Report-Accounts-_.pdf",
}

IR_NOTES = {
    "ACCESSCORP": "IR sites theaccesscorporation.com (2022-2025, holding company) and accessbankplc.com (2020-2021, Access Bank Plc was the listed entity) list PDFs in static HTML.",
    "ZENITHBANK": "zenithbank.com returned HTTP 403 to scripted requests; NGX filings used.",
    "GTCO": "gtcoplc.com annual-reports pages 1-3 list PDFs in static HTML.",
    "UBA": "ubagroup.com returns a 212-byte JavaScript shell; no document links visible to a script; NGX filings used.",
    "FIRSTHOLDCO": "first-holdco.com annual-report page lists only 2025 in static HTML; financial-statements page lists FY2021; other years from NGX.",
    "FIDELITYBK": "fidelitybank.ng annual-reports page lists all six years in static HTML.",
    "FCMB": "fcmbgroup.com investor pages returned no document links to a script (IR host fcmbgroup.gcs-web.com uses opaque static-file IDs); NGX filings used.",
    "STANBIC": "stanbicibtc.com IR pages returned no annual-report links; reporting.stanbicibtc.com links the 2025 report on a third-party host (thevault.exchange); NGX filings used.",
    "STERLINGNG": "sterlingholdco.ng lists 2023-2025; sterling.ng lists 2022 (Sterling Bank Plc); 2020-2021 from NGX (symbol STERLNBANK).",
    "WEMABANK": "wemabank.com returns a 3 KB JavaScript shell; NGX filings used.",
    "UNITYBNK": "unitybankng.com did not respond (connection failure); NGX filings used. No audited FY2024 or FY2025 statements on NGX as of the check date (merger with Providus Bank in progress).",
    "JAIZBANK": "jaizbankplc.com investor pages returned no PDF links to a script; NGX filings used.",
    "ETI": "ecobank.com annual-reports page renders links through JavaScript with opaque upload IDs; NGX filings used.",
}

# Latest standalone sustainability report found per bank (None = none found;
# the 2025 annual report is scanned for every bank in addition).
SUSTAINABILITY_REPORTS = {
    "ACCESSCORP": (2025, "https://theaccesscorporation.com/wp-content/uploads/2026/10/Access-Holdings-Standalone-Sustainability-Report-2025-compressed.pdf"),
    "ZENITHBANK": None,
    "GTCO": (2023, "https://gtco-plc.files.svdcdn.com/production/annual-reports/gtco-plc-2023-sustainability-report/GTCO-Plc-2023-Sustainability-Report.pdf?dm=1720698952"),
    "UBA": (2024, "https://doclib.ngxgroup.com/Financial_NewsDocs/45428_UNITED_BANK_FOR_AFRICA_PLC-UBA_ANNUAL_SUSTAINABILITY_REPORT_2024_CORPORATE_ACTIONS_NOVEMBER_2025.pdf"),
    "FIRSTHOLDCO": (2024, "https://www.firstbanknigeria.com/downloads/FirstHoldCo_2024_Sustainability_Report.pdf"),
    "FIDELITYBK": (2023, "https://www.fidelitybank.ng/documents/Fidelity_Bank_Sustainability_Climate_Report_2023.pdf"),
    "FCMB": None,
    "STANBIC": (2023, "https://reporting.stanbicibtc.com/wp-content/uploads/2024/05/SIBTC_Sustainability-ReportYE2023%20FINAL%20R.pdf"),
    "STERLINGNG": (2024, "https://sterling.ng/wp-content/uploads/2025/12/Sterling-HoldCo-Sustainabiity-Report-2024-.pdf"),
    "WEMABANK": (2024, "https://wemaprodstorage.blob.core.windows.net/report-upload/638991399040206013_2024_sustainability_report_Wema_Bank.pdf"),
    "UNITYBNK": (2021, "https://unitybankng.com/uploads/pdf/sustainability-report-2021.pdf"),
    "JAIZBANK": None,
    "ETI": None,
}

# Emission-intensity sources checked in Phase 0 (opened during the check).
INTENSITY_SOURCES = {
    "unfccc_btr1": "https://unfccc.int/sites/default/files/resource/Nigeria%20BTR1%20.pdf",
    "unfccc_btr1_nid": "https://unfccc.int/sites/default/files/resource/Nigeria%20BTR1%20NID%202024.pdf",
    "nbs_rebased_gdp": "https://microdata.nigerianstat.gov.ng/index.php/catalog/147/download/1256",
    "climate_watch_api": "https://www.climatewatchdata.org/api/v1/data/historical_emissions",
    "pcaf_database_sheet": "https://carbonaccountingfinancials.com/files/database/PCAF-2025Database-2Pager-R2.pdf",
}
