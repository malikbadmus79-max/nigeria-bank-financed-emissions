"""Text-layer scans of annual and sustainability reports.

All results here are heuristic page locators. They point to candidate pages
and record what the page text says; they do not extract or validate figures.
"""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass, field
from pathlib import Path

import pypdfium2 as pdfium

# Sector labels commonly used in Nigerian bank credit-concentration notes.
SECTOR_PATTERNS = {
    "agriculture": r"agricultur",
    "oil_gas": r"oil\s*(and|&)\s*gas|upstream|downstream|petroleum",
    "manufacturing": r"manufactur",
    "general_commerce": r"general\s+commerce|commerce|trade",
    "government": r"government|public\s+sector",
    "construction": r"construction",
    "real_estate": r"real\s+estate",
    "power": r"\bpower\b|electricity|energy",
    "transport": r"transport",
    "finance_insurance": r"financ\w*\s*(and|&)\s*insurance|financial\s+institution|capital\s+market",
    "ict": r"information\s*(and|&)\s*communication|telecom|communication",
    "education": r"education",
    "individuals": r"individual|retail|consumer|personal",
    "mining": r"mining|quarrying",
    "professional_services": r"professional|general\s+services|other\s+services",
}

_LOANS = re.compile(r"loans?\s+and\s+advances|loans?\s+to\s+customers|financing\s+(and|&)\s+advances|financing\s+analysis|financing|risk\s+assets|credit\s+exposure|loans", re.I)
_CONTEXT = re.compile(r"sector|industry|concentration", re.I)
_NUM = re.compile(r"\d{1,3}(,\d{3})+|\d{1,3}( \d{3}){2,}|\d+\.\d+")


@dataclass
class SectorScan:
    n_pages: int = 0
    text_pages: int = 0
    candidate_pages: list[int] = field(default_factory=list)
    best_page: int | None = None
    best_sector_hits: int = 0
    gross_or_net: str = ""
    level: str = ""
    categories: str = ""
    error: str = ""


def _sector_hits(text: str) -> int:
    return sum(1 for p in SECTOR_PATTERNS.values() if re.search(p, text, re.I))


def _row_labels(text: str) -> list[str]:
    labels = []
    for line in text.splitlines():
        m = re.match(r"^\s*([A-Za-z][A-Za-z&,'/()\-\s]{2,60}?)\s+[\(\-]?\d", line)
        if not m:
            continue
        lab = re.sub(r"\s+", " ", m.group(1)).strip(" -")
        if len(lab) < 3 or re.fullmatch(r"(?i)(note|page|group|bank|company|total|n'?million|in millions of naira)", lab):
            continue
        labels.append(lab)
    seen, out = set(), []
    for lab in labels:
        k = lab.lower()
        if k not in seen:
            seen.add(k)
            out.append(lab)
    return out


def _gross_net(text: str) -> str:
    t = text.lower()
    gross = "gross" in t
    allowance = bool(re.search(r"impairment|allowance|expected credit loss|\becl\b", t))
    net = bool(re.search(r"\bnet\b", t))
    if gross and allowance:
        return "gross (allowance shown on page)"
    if gross:
        return "gross"
    if net and allowance:
        return "net (allowance mentioned)"
    if net:
        return "net"
    return "not stated on page"


def _level(text: str) -> str:
    g = bool(re.search(r"\bgroup\b", text, re.I))
    b = bool(re.search(r"\bbank\b|\bcompany\b|\bparent\b", text, re.I))
    if g and b:
        return "group and bank/company columns or mentions"
    if g:
        return "group"
    if b:
        return "bank/company"
    return "not stated on page"


_PDFIUM_LOCK = threading.Lock()  # PDFium is not thread-safe


def page_texts(pdf_path: Path) -> list[str]:
    """Page texts via PDFium (fast); pdfplumber is kept for table extraction."""
    with _PDFIUM_LOCK:
        return _page_texts(pdf_path)


def _page_texts(pdf_path: Path) -> list[str]:
    texts = []
    pdf = pdfium.PdfDocument(str(pdf_path))
    try:
        for i in range(len(pdf)):
            try:
                page = pdf[i]
                tp = page.get_textpage()
                texts.append(tp.get_text_range() or "")
                tp.close()
                page.close()
            except Exception:  # damaged page objects occur in some reports
                texts.append("")
    finally:
        pdf.close()
    return [t.replace("\r\n", "\n").replace("\r", "\n") for t in texts]


def _year_bonus(t: str, year: int | None) -> int:
    """+3 if a table-title line names the report year, -3 if it names only the
    prior year (comparative table)."""
    if not year:
        return 0
    titles = [ln for ln in t.splitlines()
              if re.search(r"sector|industry|concentration|as\s+at|dec(ember)?|group|bank", ln, re.I)
              and not re.search(r"for\s+the\s+year\s+ended|annual\s+report", ln, re.I)]
    joined = "\n".join(titles)
    if re.search(rf"\b{year}\b", joined):
        return 3
    if re.search(rf"\b{year - 1}\b", joined):
        return -3
    return 0


def _score_page(t: str, year: int | None) -> int:
    hits = _sector_hits(t)
    bonus = 2 if re.search(r"concentration", t, re.I) else 0
    bonus += 2 if re.search(r"by\s+(economic\s+)?sector|sectoral|by\s+industry|per\s+(industry\s+)?sector|industry\s+sector", t, re.I) else 0
    bonus += 3 if re.search(r"gross\s+loans|loans\s+and\s+advances\s+to\s+customers|financing\s+analysis", t, re.I) else 0
    bonus -= 3 if re.search(r"off[\s\-]balance", t, re.I) and not re.search(r"on[\s\-]balance", t, re.I) else 0
    bonus -= 4 if len(_NUM.findall(t)) < 30 else 0
    return hits + bonus + _year_bonus(t, year)


def describe_page(t: str) -> tuple[str, str, str]:
    return _gross_net(t), _level(t), "; ".join(_row_labels(t)[:40])


def scan_sector_table(texts: list[str], min_hits: int = 6, year: int | None = None) -> SectorScan:
    """Locate the loans-by-sector note. ``year`` (the report year) is used to
    prefer current-year tables over prior-year comparatives."""
    res = SectorScan(n_pages=len(texts))
    res.text_pages = sum(1 for t in texts if len(t.strip()) > 50)
    scored = []
    for i, t in enumerate(texts, start=1):
        by_sector = re.search(r"by\s+(economic\s+)?sector", t, re.I)
        if not ((_LOANS.search(t) and _CONTEXT.search(t)) or (by_sector and _sector_hits(t) >= 8)):
            continue
        if _sector_hits(t) >= min_hits and len(_NUM.findall(t)) >= 10:
            scored.append((_score_page(t, year), -i, i))
    res.candidate_pages = sorted(i for _, _, i in scored)
    if scored:
        _, _, best = max(scored)
        res.best_page = best
        t = texts[best - 1]
        res.best_sector_hits = _sector_hits(t)
        res.gross_or_net, res.level, res.categories = describe_page(t)
    return res


# --- sustainability disclosures -------------------------------------------

_TCO2 = re.compile(r"tCO2|tCO₂|tonnes?\s+(of\s+)?CO2|tons?\s+(of\s+)?CO2|CO2e|CO₂e|kgCO2|MtCO2|ktCO2", re.I)
_MONEY = re.compile(r"(₦|N|NGN|US\$|USD|\$)\s?\d[\d,\.]*\s*(bn|billion|million|m|trillion|tn)?", re.I)

DISCLOSURE_PATTERNS = {
    "scope1": re.compile(r"scope\s*1\b", re.I),
    "scope2": re.compile(r"scope\s*2\b", re.I),
    "scope3": re.compile(r"scope\s*3\b", re.I),
    "financed_emissions": re.compile(r"financed\s+emissions?|portfolio\s+emissions|category\s*15", re.I),
    "pcaf": re.compile(r"\bPCAF\b|Partnership\s+for\s+Carbon\s+Accounting", re.I),
    "green_loans": re.compile(r"green\s+(loans?|finance|financing|lending|bonds?|assets)|sustainable\s+(finance|financing|loans?)|climate\s+finance", re.I),
}


def scan_disclosures(texts: list[str]) -> dict[str, dict]:
    """For each disclosure item: pages mentioning it, and pages where it co-occurs
    with an emissions unit (or a currency amount, for green loans)."""
    out = {}
    for key, pat in DISCLOSURE_PATTERNS.items():
        mention, quant = [], []
        for i, t in enumerate(texts, start=1):
            if not pat.search(t):
                continue
            mention.append(i)
            if key == "green_loans":
                if _MONEY.search(t):
                    quant.append(i)
            elif key == "pcaf":
                quant.append(i)
            elif _TCO2.search(t) and _NUM.search(t):
                quant.append(i)
        out[key] = {"mention_pages": mention, "quantified_pages": quant}
    return out


# --- foreign operations --------------------------------------------------

COUNTRIES = [
    "Ghana", "Sierra Leone", "Gambia", "Guinea", "Liberia", "Senegal", "Cote d'Ivoire", "Côte d'Ivoire",
    "Burkina Faso", "Benin", "Togo", "Niger", "Mali", "Cameroon", "Chad", "Gabon", "Congo", "Kenya",
    "Uganda", "Tanzania", "Rwanda", "Zambia", "Mozambique", "Malawi", "Zimbabwe", "Botswana",
    "South Africa", "Angola", "Ethiopia", "Burundi", "Sao Tome", "Cape Verde", "Equatorial Guinea",
    "Central African Republic", "Mauritius", "Morocco", "Egypt", "Namibia", "South Sudan",
    "United Kingdom", "France", "United Arab Emirates", "UAE", "Hong Kong", "China", "India",
    "Lebanon", "United States", "Germany", "Netherlands",
]


def foreign_countries(texts: list[str]) -> tuple[list[str], list[int]]:
    """Countries named on pages that describe subsidiaries."""
    found, pages = set(), []
    for i, t in enumerate(texts, start=1):
        if not re.search(r"subsidiar", t, re.I):
            continue
        if not re.search(r"(Limited|Ltd|S\.A\.|SA\b|Plc|Bank)", t):
            continue
        hit = False
        for c in COUNTRIES:
            if re.search(r"\b" + re.escape(c) + r"\b", t):
                # "Niger" must not be counted from "Nigeria".
                if c == "Niger" and not re.search(r"\bNiger\b(?!ia)", t):
                    continue
                found.add("Cote d'Ivoire" if c == "Côte d'Ivoire" else c)
                hit = True
        if hit:
            pages.append(i)
    return sorted(found), pages
