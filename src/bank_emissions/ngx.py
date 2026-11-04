"""Access to Nigerian Exchange (NGX) public data.

Two endpoints, both used by ngxgroup.com itself:

* company directory: ``doclib.ngxgroup.com/REST/api/issuers/companydirectory``
* issuer filings (SharePoint list ``XFinancial_News``) on ``doclib.ngxgroup.com``
"""

from __future__ import annotations

import re

import requests

from .fetch import UA

DIRECTORY_URL = "https://doclib.ngxgroup.com/REST/api/issuers/companydirectory?$orderby=CompanyName"
FILINGS_URL = "https://doclib.ngxgroup.com/_api/Web/Lists/GetByTitle('XFinancial_News')/items/"


def company_directory(timeout: int = 120) -> tuple[list[dict], bytes]:
    r = requests.get(DIRECTORY_URL, headers=UA, timeout=timeout)
    r.raise_for_status()
    return r.json(), r.content


def filings(symbol: str, submission_type: str | None = "Financial Statements",
            top: int = 2000, timeout: int = 180) -> list[dict]:
    flt = f"CompanySymbol eq '{symbol}'"
    if submission_type:
        flt += f" and Type_of_Submission eq '{submission_type}'"
    params = {
        "$select": "URL,Modified,CompanySymbol,Type_of_Submission",
        "$filter": flt,
        "$orderby": "Modified desc",
        "$top": str(top),
    }
    headers = dict(UA, Accept="application/json;odata=verbose")
    r = requests.get(FILINGS_URL, params=params, headers=headers, timeout=timeout)
    r.raise_for_status()
    out = []
    for it in r.json()["d"]["results"]:
        out.append({
            "symbol": it["CompanySymbol"],
            "posted": it["Modified"][:10],
            "type": it["Type_of_Submission"],
            "description": it["URL"]["Description"],
            "url": it["URL"]["Url"],
        })
    return out


_EXCLUDE = re.compile(r"UNAUDITED|HALF|INTERIM|\bQ[1-4]\b|QUARTER\s*[1-4]|QUARTER_[1-4]|NINE MONTHS|9M", re.I)
_AUDITED = re.compile(r"AUSITED|AUDITED|QUARTER[ _]5", re.I)


def audited_fy_filings(rows: list[dict]) -> dict[int, dict]:
    """Map financial year -> the most recently posted audited full-year filing."""
    best: dict[int, dict] = {}
    for row in rows:
        desc = row["description"]
        if not _AUDITED.search(desc) or _EXCLUDE.search(desc):
            continue
        years = [int(y) for y in re.findall(r"20\d\d", desc)]
        if not years:
            continue
        fy = years[-1]
        if fy not in best or row["posted"] > best[fy]["posted"]:
            best[fy] = row
    return best
