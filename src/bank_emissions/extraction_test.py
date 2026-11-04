"""Phase 0 extraction test: sector loan tables for two bank-years.

For each case the script
1. reads the sector table page located by phase0_check (PDF page index, 1-based),
2. tries camelot (stream flavour, no Ghostscript or Java needed) and a
   text-line parser on the same page,
3. writes the parsed table to data/interim/extraction_test_<symbol>_<year>.csv,
4. checks that the sector rows sum to the table's total row, and
5. searches the rest of the report for the same total to confirm that it matches
   a loans-and-advances total reported elsewhere (statement of financial position
   or the loans note).

Results are written to data/interim/extraction_test_results.json and picked up by
phase0_report.py.

    python -m bank_emissions.extraction_test
"""

from __future__ import annotations

import json
import re
import sys
import warnings
from pathlib import Path

import pandas as pd

from . import pdfscan

ROOT = Path(__file__).resolve().parents[2]
INTERIM = ROOT / "data" / "interim"
RAW = ROOT / "data" / "raw" / "annual_reports"

# Cases chosen after reviewing phase0_check output (clear, text-based tables).
# page = PDF page index (1-based); value_columns names the numeric columns in order.
CASES = [
    # Note 5.1.2. Company columns are printed as dashes and are not parsed; the
    # fourth column header is printed "Group" although it sits under "Company".
    dict(symbol="ACCESSCORP", year=2023, file="ACCESSCORP_2023_ir.pdf", page=233,
         value_columns=["group_2023", "group_2022"],
         units="millions of naira", basis="gross loans and advances to customers, group"),
    # Note 3(b). First block on the page is 31 December 2023; the 2022 block follows.
    dict(symbol="ZENITHBANK", year=2023, file="ZENITHBANK_2023_ngx.pdf", page=84,
         value_columns=["group_gross", "group_impairment", "group_carrying",
                        "bank_gross", "bank_impairment", "bank_carrying"],
         units="millions of naira", basis="gross loans, impairment allowance and carrying amount, group and bank, 31 Dec 2023"),
]

NUM = r"\(?-?\d{1,3}(?:,\d{3})+\)?|\(?-?\d+\)?"
ROW = re.compile(rf"^\s*(?P<label>[A-Za-z][^\d]*?)?\s*(?P<nums>(?:(?:{NUM})\s+){{1,7}}(?:{NUM}))\s*$")


def _to_num(s: str) -> float:
    s = s.strip()
    neg = s.startswith("(") and s.endswith(")")
    v = float(s.strip("()").replace(",", "") or 0)
    return -v if neg else v


def parse_text_table(text: str, ncols: int) -> tuple[pd.DataFrame, list[float] | None, list[str]]:
    """Parse 'label n1 n2 ...' lines with exactly ncols numbers. An unlabeled
    line with ncols numbers after the sector rows is taken as the total."""
    rows, total, notes = [], None, []
    for line in text.splitlines():
        # empty columns printed as dashes (e.g. Company columns) are dropped
        line = re.sub(r"(\s+[-–])+\s*$", "", line)
        m = ROW.match(line)
        if not m:
            continue
        nums = re.findall(NUM, m.group("nums"))
        if len(nums) != ncols:
            continue
        label = (m.group("label") or "").strip()
        vals = [_to_num(n) for n in nums]
        if not label or re.fullmatch(r"(?i)total.*", label):
            if rows:
                total = vals
                break
            continue
        if re.fullmatch(r"(?i)(december|in thousands of naira|group|bank)", label):
            continue
        rows.append([label] + vals)
    if total is None:
        notes.append("no total row found by text parser")
    return pd.DataFrame(rows, columns=["sector"] + [f"c{i}" for i in range(ncols)]), total, notes


def try_camelot(pdf: Path, page: int) -> dict:
    try:
        import camelot  # noqa: WPS433
    except Exception as exc:
        return {"ok": False, "error": f"import failed: {exc}"}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tables = camelot.read_pdf(str(pdf), pages=str(page), flavor="stream")
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"[:300]}
    shapes = [t.df.shape for t in tables]
    return {"ok": bool(tables), "n_tables": len(tables), "shapes": shapes,
            "largest_table_head": tables[max(range(len(tables)), key=lambda i: tables[i].df.size)].df.head(8).values.tolist() if tables else []}


def run_case(case: dict) -> dict:
    pdf = RAW / case["file"]
    texts = pdfscan.page_texts(pdf)
    page_text = texts[case["page"] - 1]
    cols = case["value_columns"]
    df, total, notes = parse_text_table(page_text, len(cols))
    df.columns = ["sector"] + cols
    out_csv = INTERIM / f"extraction_test_{case['symbol']}_{case['year']}.csv"
    df.insert(0, "page", case["page"])
    df.insert(0, "year", case["year"])
    df.insert(0, "symbol", case["symbol"])
    df["units"] = case["units"]
    df.to_csv(out_csv, index=False)

    res = {k: case[k] for k in ("symbol", "year", "page", "units", "basis")}
    res.update(csv=out_csv.relative_to(ROOT).as_posix(), n_sector_rows=len(df), notes=notes,
               text_chars_on_page=len(page_text))
    checks = []
    for i, c in enumerate(cols):
        s = float(df[c].sum())
        t = total[i] if total else None
        # Look for the printed total elsewhere in the report.
        elsewhere = []
        if t is not None:
            printed = f"{int(abs(t)):,}"
            for p, txt in enumerate(texts, start=1):
                if p == case["page"] or printed not in txt:
                    continue
                lines = txt.splitlines()
                for j, ln in enumerate(lines):
                    if printed in ln:
                        ctx = " / ".join(x.strip() for x in lines[max(0, j - 3): j + 1])
                        elsewhere.append({"page": p, "context": ctx[:300]})
                        break
        checks.append({"column": c, "sum_of_sectors": s, "table_total": t,
                       "sum_equals_table_total": (t is not None and abs(s - t) < 0.5),
                       "difference": (s - t) if t is not None else None,
                       "total_found_on_other_pages": elsewhere[:10]})
    res["checks"] = checks
    res["camelot_stream"] = try_camelot(pdf, case["page"])
    return res


def main(argv: list[str] | None = None) -> int:
    results = [run_case(c) for c in CASES]
    INTERIM.mkdir(parents=True, exist_ok=True)
    (INTERIM / "extraction_test_results.json").write_text(json.dumps(results, indent=1, default=str), encoding="utf-8")
    for r in results:
        print(r["symbol"], r["year"], "rows", r["n_sector_rows"], r["notes"])
        for c in r["checks"]:
            print("  ", c["column"], c["sum_of_sectors"], c["table_total"], c["sum_equals_table_total"])
            for e in c["total_found_on_other_pages"]:
                print("      p", e["page"], "|", e["context"][:220])
        print("   camelot:", {k: v for k, v in r["camelot_stream"].items() if k != "largest_table_head"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
