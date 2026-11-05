"""Phase 2a, step 4: NBS GDP by economic activity at current basic prices, 2019-2024 (plan section 5).

Source: NBS, "Rebasing of Gross Domestic Product (GDP): Key Highlights",
data/raw/intensity/nbs_microdata_147_1256.pdf, annex table "Gross Domestic
Product At Current Basic Prices (=N=Million)", PDF p. 7. Base year 2019.

Activities are read as printed (46 numbered lines, with the section heading
they sit under). Two activities are both numbered '34.' (Publishing; Motion
Pictures, Sound recording and Music production): the second is the 35th line
and is recorded with activity_no 35 and the printed number kept in
number_as_printed. Check: the 46 activities sum to the printed 'GDP Current
Basic Price' for each year, within 0.01 million naira per term (values are
printed to two decimals).

    python -m bank_emissions.phase2a_nbs
"""

from __future__ import annotations

import re

import pandas as pd

from .phase1b_extract import INTERIM, PROCESSED, ROOT

PDF = ROOT / "data" / "raw" / "intensity" / "nbs_microdata_147_1256.pdf"
PAGE = 7
YEARS = [2019, 2020, 2021, 2022, 2023, 2024]
_V = r"\d{1,3}(?:,\d{3})*\.\d{2}"
LINE = re.compile(rf"^(?P<no>\d+)\.\s*(?P<label>.*?)\s+(?P<vals>(?:{_V}\s+){{5}}{_V})\s*$")
TOTAL = re.compile(rf"^GDP Current Basic Price\s+(?P<vals>(?:{_V}\s+){{5}}{_V})\s*$")
SECTIONS = {"AGRICULTURE", "MINING AND QUARRYING", "MANUFACTURING", "TRANSPORTATION AND STORAGE",
            "INFORMATION AND COMMUNICATION", "FINANCIAL AND INSURANCE"}


def page_text() -> str:
    import pypdfium2

    return pypdfium2.PdfDocument(str(PDF))[PAGE - 1].get_textpage().get_text_range()


def extract() -> tuple[pd.DataFrame, dict[int, float]]:
    rows, total, section, carry = [], {}, "", ""
    seq = 0
    header = None
    for raw in page_text().splitlines():
        ln = raw.strip()
        if not ln:
            continue
        if ln.startswith("Gross Domestic Product At Current Basic Prices"):
            header = [int(y) for y in re.findall(r"\b(20\d\d)\b", ln)]
            continue
        if ln in SECTIONS:
            section, carry = ln, ""
            continue
        m = TOTAL.match(ln)
        if m:
            total = {y: float(v.replace(",", "")) for y, v in zip(YEARS, m.group("vals").split())}
            continue
        cand = f"{carry} {ln}".strip() if carry else ln
        m = LINE.match(cand)
        if m:
            seq += 1
            label = re.sub(r"\s+", " ", m.group("label")).strip().rstrip(",")
            # a numbered line in capitals outside a section is a section of its own
            sec = section if not label.isupper() else label
            for y, v in zip(YEARS, m.group("vals").split()):
                rows.append(dict(activity_no=seq, number_as_printed=int(m.group("no")), activity=label,
                                 nbs_section=sec, year=y, value_as_printed=v,
                                 gdp_current_basic_naira_million=float(v.replace(",", "")),
                                 gdp_current_basic_naira=float(v.replace(",", "")) * 1e6,
                                 pdf_page=PAGE))
            carry = ""
            if label.isupper():
                section = ""  # capitalised activities (22-26, 37, 40-46) end the preceding section
        elif re.match(r"^\d+\.", ln):
            carry = ln  # wrapped label (activities 22 and 23)
    if header != YEARS:
        raise ValueError(f"year header {header} is not {YEARS}")
    df = pd.DataFrame(rows)
    df["source"] = "NBS, Rebasing of GDP: Key Highlights, annex (GDP at current basic prices)"
    df["source_file"] = PDF.relative_to(ROOT).as_posix()
    df["units_as_printed"] = "=N= Million"
    return df, total


def checks(df: pd.DataFrame, total: dict[int, float]) -> pd.DataFrame:
    out = []
    n = df.activity_no.nunique()
    out.append(dict(check="activity_count", year="", result="pass" if n == 46 else "fail",
                    detail=f"{n} activities read (46 printed lines)"))
    for y in YEARS:
        s = df[df.year == y].gdp_current_basic_naira_million.sum()
        t = total.get(y)
        out.append(dict(check="activities_sum_to_total", year=y,
                        result="pass" if t is not None and abs(s - t) <= 0.01 * n else "fail",
                        detail=f"sum {s:,.2f} vs printed GDP at current basic prices {t:,.2f} (diff {s - t:,.2f})"))
    return pd.DataFrame(out)


def main() -> int:
    df, total = extract()
    ch = checks(df, total)
    df.to_csv(PROCESSED / "nbs_gdp_by_activity.csv", index=False)
    ch.to_csv(INTERIM / "nbs_gdp_checks.csv", index=False)
    print(f"{len(df)} rows; checks: {ch.result.value_counts().to_dict()}")
    print(ch.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
