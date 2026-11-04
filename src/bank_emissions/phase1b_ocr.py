"""Phase 1b: OCR of the Jaiz Bank FY2024 sector table (plan section 2, "Jaiz Bank 2024: OCR rule").

The FY2024 NGX filing has no text layer. The page is rendered with pypdfium2
(scale 4, about 288 dpi) and read with Tesseract (TSV output, word boxes). OCR
returns the printed thousands separators as spaces or drops them ('24 152 288',
'1999 029', '1351125'), so digit groups are re-joined from the word boxes: a
group of exactly three digits that follows a digit group on the same line with
a gap narrower than a column gap belongs to the same number. The rebuilt words
then go through the same row parser as the text-layer tables.

Rule applied (plan section 2): the year is kept only if the OCR sector rows sum
to the printed total within the section 8.2 tolerance and the total agrees with
the loans note in the same filing. Every OCR value is then rechecked against
the FY2025 filing's 2024 comparative column (text layer) and the 2023 column
against the FY2023 filing; results go to data/interim/jaiz2024_ocr_check.csv.

    python -m bank_emissions.phase1b_ocr
"""

from __future__ import annotations

import csv
import io
import re
import shutil
import subprocess
from pathlib import Path

import pandas as pd

from . import tables
from .phase1b_extract import INTERIM, ROOT, cached_lines, source_files

PDF = ROOT / "data" / "raw" / "annual_reports" / "JAIZBANK_2024_ngx.pdf"
PAGE = 122  # PDF page (1-based) located by OCR of pages 95-135 ("(iii) By sector")
SCALE = 4.0
TESSERACT_DEFAULT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
METHOD = "OCR: pypdfium2 render x4 + Tesseract 5 (psm 6, TSV word boxes); digit groups re-joined from box gaps"


def tesseract_exe() -> str:
    exe = shutil.which("tesseract")
    if exe:
        return exe
    if TESSERACT_DEFAULT.exists():
        return str(TESSERACT_DEFAULT)
    raise FileNotFoundError("tesseract not on PATH and not at the default install location")


def tesseract_version() -> str:
    out = subprocess.run([tesseract_exe(), "--version"], capture_output=True)
    return out.stdout.decode("utf-8", "replace").splitlines()[0].strip()


def ocr_words(pdf: Path, page: int, scale: float = SCALE) -> list[tables.Word]:
    """Tesseract word boxes for one page, in PDF points."""
    import pypdfium2

    doc = pypdfium2.PdfDocument(str(pdf))
    img = doc[page - 1].render(scale=scale).to_pil()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    out = subprocess.run([tesseract_exe(), "stdin", "stdout", "--psm", "6", "tsv"],
                         input=buf.getvalue(), capture_output=True, check=True)
    rows = csv.DictReader(io.StringIO(out.stdout.decode("utf-8", "replace")), delimiter="\t",
                          quoting=csv.QUOTE_NONE)
    words = []
    for r in rows:
        t = (r.get("text") or "").strip()
        if not t or r["level"] != "5":
            continue
        x0, top, w = float(r["left"]) / scale, float(r["top"]) / scale, float(r["width"]) / scale
        words.append(tables.Word(t, x0, x0 + w, top))
    return words


def join_digit_groups(words: list[tables.Word], max_gap: float = 6.0) -> list[tables.Word]:
    """Re-join numbers split at the thousands separators by OCR. A word of
    exactly three digits (commas removed) is appended to the preceding digit
    word on the same line when the gap is below ``max_gap`` points; column gaps
    in this table are over 40 points. Commas read by OCR are dropped first."""
    words = sorted(words, key=lambda w: (round(w.top / 4), w.x0))
    out: list[tables.Word] = []
    for w in words:
        t = w.text.replace(",", "").replace(".", "") if re.fullmatch(r"[\d,.]+", w.text) else w.text
        if (out and re.fullmatch(r"\d{3}", t) and re.fullmatch(r"\d+", out[-1].text)
                and abs(out[-1].top - w.top) < 4 and 0 <= w.x0 - out[-1].x1 < max_gap):
            p = out[-1]
            out[-1] = tables.Word(p.text + t, p.x0, w.x1, p.top)
        else:
            out.append(tables.Word(t, w.x0, w.x1, w.top))
    # print with thousands separators so the row parser reads them as numbers
    return [tables.Word(f"{int(w.text):,}" if re.fullmatch(r"\d+", w.text) else w.text, w.x0, w.x1, w.top)
            for w in out]


def ocr_table() -> tables.ParsedTable:
    lines = tables.words_to_lines(join_digit_groups(ocr_words(PDF, PAGE)))
    return tables.parse_rows(lines, r"By sector", 2, total_re=r"^total", tol=25.0)


def _text_layer_table(bank_year: tuple[str, int], page: int) -> dict[str, list[float]]:
    lines = cached_lines(source_files()[bank_year], page)
    t = tables.parse_rows(lines, r"By ?sector", 2, total_re=r"^total")
    return {_key(r.label): r.values for r in t.rows} | {"__total__": t.total}


def _key(label: str) -> str:
    return re.sub(r"[^a-z]", "", label.lower())


def find_total_in_filing(total: float, pages) -> list[dict]:
    """OCR other pages of the FY2024 filing and look for the table total
    (digits only, so separators read as spaces do not matter)."""
    import pypdfium2

    doc = pypdfium2.PdfDocument(str(PDF))
    target = str(int(total))
    hits = []
    for p in pages:
        if p == PAGE:
            continue
        buf = io.BytesIO()
        doc[p - 1].render(scale=3).to_pil().save(buf, format="PNG")
        out = subprocess.run([tesseract_exe(), "stdin", "stdout", "--psm", "6"], input=buf.getvalue(),
                             capture_output=True).stdout.decode("utf-8", "replace")
        for ln in out.splitlines():
            if target in re.sub(r"[\s,.]", "", ln):
                hits.append(dict(page=p, line=ln.strip()[:200]))
    return hits


LOANS_NOTE_PAGES = (109,)  # collateral analysis of customer financing; located by OCR of pp. 60-143


def run_core(loans_note_pages=LOANS_NOTE_PAGES) -> dict:
    t = ocr_table()
    rows = [(r.label, r.values[0], r.values[1]) for r in t.rows]
    total24, total23 = t.total
    sum24 = sum(v for _, v, _ in rows)
    tol = 0.5 * len(rows)

    fy25 = _text_layer_table(("JAIZBANK", 2025), 114)  # 2024 comparative is the second column
    fy23 = _text_layer_table(("JAIZBANK", 2023), 120)  # 2023 is the first column
    checks = []
    for label, v24, v23 in rows:
        k = _key(label)
        c24 = fy25.get(k, [None, None])[1]
        c23 = fy23.get(k, [None, None])[0]
        checks.append(dict(printed_category=label, ocr_2024=v24, fy2025_comparative_2024=c24,
                           match_2024=(c24 is not None and abs(c24 - v24) < 0.5),
                           ocr_2023=v23, fy2023_report_2023=c23,
                           match_2023=(c23 is not None and abs(c23 - v23) < 0.5)))
    checks.append(dict(printed_category="Total", ocr_2024=total24, fy2025_comparative_2024=fy25["__total__"][1],
                       match_2024=abs(fy25["__total__"][1] - total24) < 0.5, ocr_2023=total23,
                       fy2023_report_2023=fy23["__total__"][0], match_2023=abs(fy23["__total__"][0] - total23) < 0.5))
    pd.DataFrame(checks).to_csv(INTERIM / "jaiz2024_ocr_check.csv", index=False)
    loans_note = find_total_in_filing(total24, loans_note_pages)
    return dict(rows=rows, total=total24, sum=sum24, tol=tol, sum_ok=abs(sum24 - total24) <= tol,
                checks=checks, loans_note_hits=loans_note, tesseract=tesseract_version())


def main() -> int:
    r = run_core(range(60, 144))
    print(r["tesseract"])
    print(f"rows {len(r['rows'])}, sum {r['sum']:,.0f}, printed total {r['total']:,.0f}, sum check {r['sum_ok']}")
    for c in r["checks"]:
        print(f"  {c['printed_category'][:40]:40s} {c['ocr_2024']:>14,.0f} {c['match_2024']!s:5s} "
              f"{c['ocr_2023']:>14,.0f} {c['match_2023']}")
    print("total found elsewhere in filing:", r["loans_note_hits"][:5])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
