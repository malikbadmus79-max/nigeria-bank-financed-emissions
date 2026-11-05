"""Phase 2a, step 3: BTR1 emissions by IPCC category, 2019-2022 (plan section 5).

Source: Nigeria's First Biennial Transparency Report (BTR1), Table 2.10
"Summary of greenhouse gas emissions and removals ... emission trends",
data/raw/intensity/Nigeria_BTR1.pdf. Units as printed: kt CO2 equivalent.

The table is printed in three year-blocks; the third block (PDF pp. 60-62)
holds six year columns (2017-2022) followed by a percentage-change column.
On PDF p. 60 the top of that block (year header, total net emissions, all
energy rows 1 to 1.C and the row "2. Industrial processes and product use") is
an embedded image, not text; it is read by OCR (Tesseract, page rendered at
4x) and every OCR value is checked by the parent/child sums below and was
compared with the rendered image. The rest of the block is text. The years of
those columns are not read from a header on every page (the PDF p. 56 header
is misprinted "2014 2016 2016", plan section 5); they are assigned by position
and checked: the 2018 column must equal the printed reference-year total
without LULUCF (310,030.28 on PDF p. 57) and the 2022 column the printed 2022
totals (328,496.23 without LULUCF and 554,095.14 with LULUCF, PDF p. 62).

Checks written to data/interim/btr1_checks.csv:
- each parent category equals the sum of its printed sub-categories;
- the top-level categories sum to the printed national totals, with and
  without LULUCF.
Tolerance: 0.01 kt per summed term (values are printed to two decimals).

    python -m bank_emissions.phase2a_btr1
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .phase1b_extract import INTERIM, PROCESSED, ROOT

PDF = ROOT / "data" / "raw" / "intensity" / "Nigeria_BTR1.pdf"
BLOCK3_PAGES = [60, 61, 62]  # PDF pages (1-based) of the 2017-2022 block
IMAGE_PAGE = 60  # the block's top part on this page is an image (PDF points, top to bottom)
IMAGE_BOX = (60.0, 65.0, 800.0, 280.0)
BLOCK3_YEARS = [2017, 2018, 2019, 2020, 2021, 2022]
KEEP_YEARS = [2019, 2020, 2021, 2022]

PRINTED_CHECKS = {  # (PDF page, label as printed, year): value as printed, used only as a check target
    (57, "Total CO2 equivalent emissions without LULUCF", 2018): 310030.28,
    (62, "Total CO2 equivalent emissions without LULUCF", 2022): 328496.23,
    (62, "Total CO2 equivalent emissions with LULUCF", 2022): 554095.14,
}

_VAL = r"(?:-?\d{1,3}(?:,\d{3})*\.\d+|-?\d+\.\d+|[A-Z]{2}(?:,[A-Z]{2})*)"
_PCT = r"(?:-?\d+(?:\.\d+)?|–|-)"
_CODE = r"(?:\d\.(?:[A-Z]\.)?(?:\d\.)?(?:[a-z]\.)?)"
ROW = re.compile(rf"^(?P<code>{_CODE})\s*(?P<label>.*?)\s+(?P<vals>(?:{_VAL}\s+){{5}}{_VAL})\s+(?P<pct>{_PCT})\s*$")
TOTAL = re.compile(rf"^(?P<label>Total CO2 equivalent emissions[^\d]*?)\s+(?P<vals>(?:{_VAL}\s+){{5}}{_VAL})\s+(?P<pct>{_PCT})\s*$")


def page_texts(pdf: Path, pages: list[int]) -> dict[int, str]:
    import pypdfium2

    doc = pypdfium2.PdfDocument(str(pdf))
    return {p: doc[p - 1].get_textpage().get_text_range() for p in pages}


def _num(tok: str) -> float | None:
    if re.fullmatch(r"[A-Z]{2}(?:,[A-Z]{2})*", tok):
        return None  # notation key (NE, NO, NA, IE, FX ...): no value
    return float(tok.replace(",", ""))


def _lines(text: str) -> list[str]:
    """Join wrapped lines: a line without the six values is carried into the next."""
    out, carry = [], ""
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        cand = (carry + " " + ln).strip() if carry else ln
        if ROW.match(cand) or TOTAL.match(cand):
            out.append(cand)
            carry = ""
        elif re.match(_CODE + r"\s", ln) or ln.startswith("Total CO2"):
            carry = ln
        elif carry:
            carry = cand
    return out


# Rows of the image part, in printed order (the same sequence as in the other
# year-blocks of Table 2.10, e.g. PDF pp. 54-55 and 57-58).
IMAGE_ROWS = [("", "Total (net emissions)"), ("1", "Energy"), ("1.A", "Fuel combustion"),
              ("1.A.1", "Energy industries"), ("1.A.2", "Manufacturing industries and construction"),
              ("1.A.3", "Transport"), ("1.A.4", "Other sectors"), ("1.A.5", "Other"),
              ("1.B", "Fugitive emissions from fuels"), ("1.B.1", "Solid fuels"),
              ("1.B.2", "Oil and natural gas and other emissions from energy production"),
              ("1.C", "CO2 Transport and storage"), ("2", "Industrial processes and product use")]
# the six year columns of the image, in PDF points (left, right); rows span the image
IMAGE_COLS_BOX = (276.8, 71.0, 595.3, 275.0)


def _runs(flags: list[bool], min_len: int = 1) -> list[tuple[int, int]]:
    out, start = [], None
    for i, f in enumerate(flags + [False]):
        if f and start is None:
            start = i
        elif not f and start is not None:
            if i - start >= min_len:
                out.append((start, i))
            start = None
    return out


def ocr_grid_cells(scale: float = 5.0) -> list[list[str]]:
    """OCR of the year-column grid of the image, cell by cell. Grid lines are
    found as pixel rows/columns that are mostly dark; each cell is read as a
    single line restricted to digits, separators and the letters of the
    notation keys. Returns the text of each cell, row by row."""
    import io
    import subprocess

    import pypdfium2

    from .phase1b_ocr import tesseract_exe

    doc = pypdfium2.PdfDocument(str(PDF))
    img = doc[IMAGE_PAGE - 1].render(scale=scale).to_pil().convert("L")
    x0, t, x1, b = IMAGE_COLS_BOX
    img = img.crop((int(x0 * scale), int(t * scale), int(x1 * scale), int(b * scale)))
    w, h = img.size
    px = img.load()
    dark_row = [sum(px[x, y] < 100 for x in range(w)) > 0.6 * w for y in range(h)]
    dark_col = [sum(px[x, y] < 100 for y in range(h)) > 0.6 * h for x in range(w)]
    hlines = [(a + b2) // 2 for a, b2 in _runs(dark_row)]
    vlines = [(a + b2) // 2 for a, b2 in _runs(dark_col)]
    # cell bands between consecutive grid lines (edges of the crop count as lines)
    ys = sorted(set([0] + hlines + [h - 1]))
    xs = sorted(set([0] + vlines + [w - 1]))
    rows_y = [(a, b2) for a, b2 in zip(ys, ys[1:]) if b2 - a > 6 * scale]
    cols_x = [(a, b2) for a, b2 in zip(xs, xs[1:]) if b2 - a > 20 * scale]
    out = []
    for ya, yb in rows_y:
        line = []
        for xa, xb in cols_x:
            cell = img.crop((xa + 4, ya + 4, xb - 4, yb - 4))
            buf = io.BytesIO()
            cell.save(buf, format="PNG")
            txt = subprocess.run([tesseract_exe(), "stdin", "stdout", "--psm", "7", "-c",
                                  "tessedit_char_whitelist=0123456789,.NEO"],
                                 input=buf.getvalue(), capture_output=True).stdout.decode("utf-8", "replace").strip()
            line.append(txt)
        out.append(line)
    return out


def image_part_rows() -> list[dict]:
    """Values of the image part: the first grid row must read 2017-2022; the
    unit row is skipped; the next rows are IMAGE_ROWS in order."""
    grid = ocr_grid_cells()
    header = next(r for r in grid if any(c.strip() for c in r))
    if [c.strip() for c in header] != [str(y) for y in BLOCK3_YEARS]:
        raise ValueError(f"OCR year header {header} is not {BLOCK3_YEARS}")
    data = [r for r in grid[grid.index(header) + 1:] if sum(bool(c.strip()) for c in r) == 6]
    if len(data) != len(IMAGE_ROWS):
        raise ValueError(f"expected {len(IMAGE_ROWS)} data rows from the image, got {len(data)}: {data}")
    rows = []
    for (code, label), cells in zip(IMAGE_ROWS, data):
        for y, tok in zip(BLOCK3_YEARS, cells):
            tok = tok.strip()
            if not re.fullmatch(_VAL, tok):
                raise ValueError(f"unreadable OCR cell {tok!r} for {code or label} {y}")
            rows.append(dict(category_code=code, category=label, year=y, value_as_printed=tok, kt_co2e=_num(tok),
                             pdf_page=IMAGE_PAGE, extraction_method="OCR of embedded image (Tesseract, cell by cell)"))
    return rows


def extract() -> pd.DataFrame:
    rows = image_part_rows()
    for p, text in page_texts(PDF, BLOCK3_PAGES).items():
        for ln in _lines(text):
            m = ROW.match(ln) or TOTAL.match(ln)
            if not m:
                continue
            code = m.groupdict().get("code") or ""
            label = re.sub(r"\s*\(\d\)\s*", " ", m.group("label")).strip()
            toks = m.group("vals").split()
            for y, tok in zip(BLOCK3_YEARS, toks):
                rows.append(dict(category_code=code.rstrip("."), category=label, year=y, value_as_printed=tok,
                                 kt_co2e=_num(tok), pdf_page=p, extraction_method="text layer (pypdfium2)"))
    df = pd.DataFrame(rows)
    df["source"] = "Nigeria BTR1 (26 Dec 2024), Table 2.10"
    df["source_file"] = PDF.relative_to(ROOT).as_posix()
    df["units"] = "kt CO2 equivalent"
    return df


# parent -> children, as printed in Table 2.10
TREE = {
    "1.A": ["1.A.1", "1.A.2", "1.A.3", "1.A.4", "1.A.5"],
    "1.B": ["1.B.1", "1.B.2", "1.B.3"],
    "1": ["1.A", "1.B", "1.C"],
    "2": ["2.A", "2.B", "2.C", "2.D", "2.E", "2.F", "2.G", "2.H"],
    "3": ["3.A", "3.B", "3.C", "3.D", "3.E", "3.F", "3.G", "3.H", "3.I", "3.J"],
    "4": ["4.A", "4.B", "4.C", "4.D", "4.E", "4.F", "4.G", "4.H"],
    "5": ["5.A", "5.B", "5.C", "5.D", "5.E"],
}
TOTAL_WITHOUT = ["1", "2", "3", "5", "6"]


def checks(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    v = {(r.category_code, r.year): (0.0 if pd.isna(r.kt_co2e) else r.kt_co2e)
         for r in df.itertuples() if r.category_code}
    tot = {(r.category, r.year): r.kt_co2e for r in df.itertuples() if not r.category_code}
    for y in BLOCK3_YEARS:
        for parent, kids in TREE.items():
            present = [k for k in kids if (k, y) in v]
            if (parent, y) not in v:
                out.append(dict(check="parent_sum", item=parent, year=y, result="fail", detail="parent row not found"))
                continue
            s = sum(v[(k, y)] for k in present)
            tol = 0.01 * max(len(present), 1)
            out.append(dict(check="parent_sum", item=parent, year=y,
                            result="pass" if abs(s - v[(parent, y)]) <= tol else "fail",
                            detail=f"children {present}: {s:,.2f} vs printed {v[(parent, y)]:,.2f}"))
        s = sum(v.get((k, y), 0.0) for k in TOTAL_WITHOUT)
        t = tot.get(("Total CO2 equivalent emissions without LULUCF", y))
        out.append(dict(check="national_total_without_lulucf", item="1+2+3+5+6", year=y,
                        result="pass" if t is not None and abs(s - t) <= 0.05 else "fail",
                        detail=f"{s:,.2f} vs printed {t}"))
        s2 = s + v.get(("4", y), 0.0)
        t2 = tot.get(("Total CO2 equivalent emissions with LULUCF", y))
        out.append(dict(check="national_total_with_lulucf", item="1+2+3+4+5+6", year=y,
                        result="pass" if t2 is not None and abs(s2 - t2) <= 0.06 else "fail",
                        detail=f"{s2:,.2f} vs printed {t2}"))
        tn = tot.get(("Total (net emissions)", y))
        out.append(dict(check="net_total_equals_total_with_lulucf", item="Total (net emissions)", year=y,
                        result="pass" if tn is not None and t2 is not None and abs(tn - t2) <= 0.005 else "fail",
                        detail=f"OCR net total {tn} vs printed total with LULUCF {t2}"))
    # column-year assignment
    texts = page_texts(PDF, sorted({p for p, _, _ in PRINTED_CHECKS}))
    for (p, label, y), val in PRINTED_CHECKS.items():
        printed_on_page = f"{val:,.2f}" in texts[p]
        got = tot.get((label, y))
        out.append(dict(check="year_assignment", item=label, year=y,
                        result="pass" if printed_on_page and got is not None and abs(got - val) < 0.005 else "fail",
                        detail=f"column value {got} vs {val:,.2f} printed on PDF p. {p}"))
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# NID sub-category tables (plan section 5: sub-category splits where the NID
# prints them for every year used)

NID = ROOT / "data" / "raw" / "intensity" / "Nigeria_BTR1_NID_2024.pdf"
# (PDF page, table, parent code, child codes as printed). Table 3.18 prints the
# code of 'Other - Non specified' as '1.A.1.g.viii'; it is read as 1.A.2.g.viii
# (the row is the fourth sub-category of 1.A.2 and the text on p. 72 names it
# CRT 1.A.2.g.viii).
NID_TABLES = [
    (64, "Table 3.9", "1.A.1", ["1.A.1.a", "1.A.1.b", "1.A.1.c"]),
    (70, "Table 3.18", "1.A.2", ["1.A.2.a", "1.A.2.c", "1.A.2.f", "1.A.1.g.viii"]),
    (90, "Table 3.41", "1.A.4", ["1.A.4.a", "1.A.4.b", "1.A.4.c"]),
    (102, "Table 3.59", "1.B.1", ["1.B.1.a", "1.B.1.b"]),
]
CODE_FIX = {"1.A.1.g.viii": "1.A.2.g.viii"}
# Table 3.59 prints the coal-mining figures inside the label column on the
# 'mining and' line and the fuel-transformation figures in the value columns
# between the two labels; the label word identifies the row (the text on PDF
# p. 102 gives fuel transformation as 1,407 kt in 2000 and 5,653 kt in 2022).
NID_LABEL_HINTS = {"Table 3.59": {"1.B.1.a": r"\bmining\b"}}
_NID_CODE = re.compile(r"\b(\d\.[A-Z]\.\d(?:\.[a-z])?(?:\.[ivx]+)?)\b")


def nid_rows() -> list[dict]:
    from .phase1b_extract import cached_lines

    rows = []
    for page, table, parent, kids in NID_TABLES:
        lines = cached_lines(NID, page)
        hdr = next(i for i, ln in enumerate(lines) if ln.text.startswith("Category") and len(ln.nums) >= 5
                   and int(ln.nums[0].value) >= 2000 and any(int(n.value) == 2019 for n in ln.nums))
        years = []
        for n in lines[hdr].nums:  # stop at '2022 on 2000 (% change)'
            if years and n.value <= years[-1]:
                break
            years.append(int(n.value))
        wanted = [parent] + kids
        found: dict[str, list[float]] = {}
        # rows identified by a word of their label first (NID_LABEL_HINTS), then by position
        for code, word in NID_LABEL_HINTS.get(table, {}).items():
            for ln in lines[hdr + 1: hdr + 30]:
                if len(ln.nums) >= len(years) and re.search(word, ln.label, re.I):
                    found[code] = [n.value for n in ln.nums[:len(years)]]
                    break
        for i in range(hdr + 1, min(hdr + 30, len(lines))):
            ln = lines[i]
            if len(ln.nums) < len(years) or any([n.value for n in ln.nums[:len(years)]] == v for v in found.values()):
                continue
            near = " ".join(x.text for x in lines[max(hdr + 1, i - 3): i + 3])
            own = _NID_CODE.findall(ln.text)
            cands = own or [c for c in _NID_CODE.findall(near) if c in wanted and c not in found]
            code = next((c for c in cands if c in wanted and c not in found), None)
            if code is None:
                continue
            found[code] = [n.value for n in ln.nums[:len(years)]]
        missing = [c for c in wanted if c not in found]
        if missing:
            raise LookupError(f"NID {table} p. {page}: rows not found {missing}")
        for code in wanted:
            for y, v in zip(years, found[code]):
                if y in KEEP_YEARS:
                    rows.append(dict(category_code=CODE_FIX.get(code, code), category="", year=y,
                                     value_as_printed=f"{v:,.0f}", kt_co2e=v, pdf_page=page,
                                     extraction_method="text layer (pdfplumber word positions)",
                                     source=f"Nigeria BTR1 NID (24 Dec 2024), {table}",
                                     source_file=NID.relative_to(ROOT).as_posix(), units="kt CO2 equivalent"))
    return rows


NID_LABELS = {"1.A.1": "Energy industries", "1.A.1.a": "Public electricity and heat production",
              "1.A.1.b": "Petroleum refining", "1.A.1.c": "Manufacture of solid fuels and other energy industries",
              "1.A.2": "Manufacturing industries and construction", "1.A.2.a": "Iron and steel",
              "1.A.2.c": "Chemicals", "1.A.2.f": "Non-metallic minerals", "1.A.2.g.viii": "Other - non specified",
              "1.A.4": "Other sectors", "1.A.4.a": "Commercial / institutional", "1.A.4.b": "Residential",
              "1.A.4.c": "Agriculture / forestry / fishing", "1.B.1": "Solid fuels",
              "1.B.1.a": "Coal mining and handling", "1.B.1.b": "Fuel transformation"}


def nid_checks(nid: pd.DataFrame, btr: pd.DataFrame) -> pd.DataFrame:
    """NID children sum to the NID parent (whole kt, so up to 0.5 per term) and
    the NID parent equals the BTR1 Table 2.10 value within rounding (0.5 kt)."""
    out = []
    for page, table, parent, kids in NID_TABLES:
        kids = [CODE_FIX.get(k, k) for k in kids]
        for y in KEEP_YEARS:
            g = nid[(nid.year == y) & (nid.source.str.endswith(table))].set_index("category_code").kt_co2e
            s = sum(g[k] for k in kids)
            out.append(dict(check="nid_children_sum", item=f"{table} {parent}", year=y,
                            result="pass" if abs(s - g[parent]) <= 0.5 * len(kids) else "fail",
                            detail=f"{kids}: {s:,.0f} vs NID parent {g[parent]:,.0f}"))
            b = btr[(btr.year == y) & (btr.category_code == parent)].kt_co2e
            out.append(dict(check="nid_parent_equals_btr1", item=f"{table} {parent}", year=y,
                            result="pass" if len(b) and abs(b.iloc[0] - g[parent]) <= 0.5 else "fail",
                            detail=f"NID {g[parent]:,.0f} vs Table 2.10 {b.iloc[0] if len(b) else None}"))
    # A swap of two children leaves every sum unchanged; guard the one table
    # whose rows are identified by label words (the NID text on p. 102 states
    # that fuel transformation is more than 98% of solid-fuel emissions).
    for y in KEEP_YEARS:
        g = nid[nid.year == y].set_index("category_code").kt_co2e
        share = g["1.B.1.b"] / g["1.B.1"]
        out.append(dict(check="nid_row_identity", item="Table 3.59 1.B.1.b share", year=y,
                        result="pass" if share > 0.95 else "fail",
                        detail=f"fuel transformation {share:.1%} of solid fuels (NID text: more than 98%)"))
    return pd.DataFrame(out)


def main() -> int:
    df = extract()
    nid = pd.DataFrame(nid_rows())
    nid["category"] = nid.category_code.map(NID_LABELS)
    df["level"] = "Table 2.10"
    nid["level"] = "NID sub-category"
    ch = pd.concat([checks(df), nid_checks(nid, df)], ignore_index=True)
    df = pd.concat([df, nid], ignore_index=True)
    keep = df[df.year.isin(KEEP_YEARS)]
    keep.to_csv(PROCESSED / "btr1_emissions_by_category.csv", index=False)
    ch.to_csv(INTERIM / "btr1_checks.csv", index=False)
    print(f"{len(keep)} rows ({keep.category_code.nunique()} codes); checks: {ch.result.value_counts().to_dict()}")
    bad = ch[ch.result != "pass"]
    if len(bad):
        print(bad.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
