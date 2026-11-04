"""Phase 1b: extract loans to customers by sector (plan sections 2-3).

Reads the annual reports logged in data/interim/phase0_sources.csv, applies the
table specifications in phase1b_config.py and writes

- data/processed/loans_by_sector.csv   one row per bank-year-level-basis-category
- data/processed/loans_totals.csv      the printed total of each table
- data/interim/phase1b_extract_log.csv one row per bank-year-spec attempt

No intensities or emissions are computed here.

    python -m bank_emissions.phase1b_extract
"""

from __future__ import annotations

import csv
import hashlib
import pickle
import re
import sys
import traceback
from pathlib import Path

import pandas as pd

from . import pdfscan, tables
from .phase1b_config import PRINTED_INCONSISTENCIES, SAMPLE_EXCLUSIONS, SPECS

ROOT = Path(__file__).resolve().parents[2]
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
TEXT_CACHE = ROOT / "data" / "raw" / ".textcache"  # data/raw is gitignored

UNIT_PATTERNS = [
    (re.compile(r"(?i)in\s+thousands|thousands\s+of|N\s*['’]?\s*000|₦\s*['’]?\s*000|'000"), 1e3),
    (re.compile(r"(?i)in\s+millions|millions\s+of|N\s*['’]?\s*million|₦\s*['’]?\s*million|=N=\W{0,2}million|N'?m\b"), 1e6),
    (re.compile(r"(?i)in\s+billions|billions\s+of"), 1e9),
]

OUT_COLUMNS = ["bank", "year", "level", "basis", "units_as_printed", "printed_category", "amount_printed",
               "amount_naira", "source_file", "pdf_page", "extraction_method", "main_spec", "note", "printed_cells"]


def source_files() -> dict[tuple[str, int], Path]:
    """Annual-report file per bank-year, as logged in Phase 0 (source_used)."""
    out: dict[tuple[str, int], Path] = {}
    with open(INTERIM / "phase0_sources.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["doc_type"] != "annual_report" or not r["local_path"]:
                continue
            p = ROOT / r["local_path"]
            if not p.exists():
                continue
            key = (r["symbol"], int(r["year"]))
            if key in out and not p.name.endswith(f"_{r['source_used']}.pdf"):
                continue
            out[key] = p
    return out


def cached_texts(pdf: Path) -> list[str]:
    TEXT_CACHE.mkdir(parents=True, exist_ok=True)
    k = TEXT_CACHE / f"{pdf.name}.{pdf.stat().st_size}.pkl"
    if k.exists():
        return pickle.loads(k.read_bytes())
    t = pdfscan.page_texts(pdf)
    k.write_bytes(pickle.dumps(t))
    return t


def cached_lines(pdf: Path, page: int, **kw) -> list[tables.Line]:
    """tables.page_lines with an on-disk cache (keyed on file, size, page and options)."""
    TEXT_CACHE.mkdir(parents=True, exist_ok=True)
    opts = re.sub(r"[^A-Za-z0-9=_.]", "-", "_".join(f"{k}={v}" for k, v in sorted(kw.items()) if v))
    code = hashlib.sha1(Path(tables.__file__).read_bytes()).hexdigest()[:8]  # invalidate when the parser changes
    k = TEXT_CACHE / f"{pdf.name}.{pdf.stat().st_size}.p{page}.{opts}.{code}.lines.pkl"
    if k.exists():
        return pickle.loads(k.read_bytes())
    lines = tables.page_lines(pdf, page, **kw)
    k.write_bytes(pickle.dumps(lines))
    return lines


def reconcile(result: dict) -> dict[tuple, str]:
    """Plan section 8.2: sector rows must sum to the printed total within half a
    printed unit per row. Returns {(level, basis): failure} (empty if all pass)."""
    bad = {}
    for key, total in result["totals"].items():
        vals = [v[key] for v in result["categories"].values() if key in v]
        diff = sum(vals) - (total or 0.0)
        if abs(diff) > 0.5 * max(len(vals), 1):
            bad[key] = f"{key[0]}/{key[1]}: rows sum {sum(vals):,.0f} vs total {total:,.0f} (diff {diff:,.0f}, {len(vals)} rows)"
    return bad


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def detect_units(lines: list[tables.Line], start_idx: int) -> tuple[str, float | None]:
    """Units phrase nearest above the table start (then anywhere on the page)."""
    order = list(range(start_idx, -1, -1)) + list(range(start_idx + 1, len(lines)))
    for i in order:
        for rx, mult in UNIT_PATTERNS:
            m = rx.search(lines[i].text)
            if m:
                return lines[i].text.strip()[:80], mult
    return "", None


def _start_index(lines, start_re):
    rx = re.compile(start_re, re.I)
    for i, ln in enumerate(lines):
        if rx.search(ln.text):
            return i
    return 0


_ANY_YEAR_HEADING = re.compile(r"(?i)(31\s*dec(ember)?|december\s*31,?)\s*20\d\d")
_DATE_LINE = re.compile(r"(?i)(at\s+)?(31\s*december|december\s*31,?)\s*((?:19|20)\d\d)")


def _has(rx: str, lines: list[tables.Line]) -> bool:
    return any(re.search(rx, ln.text.strip()) for ln in lines)


def check_headings(spec: dict, year: int, lines: list[tables.Line], prev_lines: list[tables.Line]) -> list[str]:
    """Level and year checks. A heading printed at the foot of the previous page
    (table continued overleaf) is carried over, but only when the current page
    carries no level (respectively year) heading of its own; a page with the
    other level's heading is rejected outright."""
    fmt = lambda s: s.replace("{year}", str(year))  # noqa: E731
    notes = []
    tail = prev_lines[-25:]
    if spec.get("level_check_re"):
        own, other = fmt(spec["level_check_re"]), spec.get("level_exclude_re")
        if other and _has(other, lines):
            raise LookupError("page carries the other level's heading")
        if not _has(own, lines):
            if tail and _has(own, tail) and not (other and _has(other, tail)):
                notes.append("level heading carried over from previous page")
            else:
                raise LookupError("level heading not on page")
    if spec.get("year_heading_first"):
        # The table's own date heading (a line holding only a date) decides; a
        # running header 'for the year ended ...' does not. Pages with the
        # comparative-year table are rejected.
        dates = [m.group(3) for ln in lines
                 if (m := _DATE_LINE.fullmatch(norm(ln.text.strip())))]
        if dates:
            if dates[0] != str(year):
                raise LookupError(f"table date heading is {dates[0]}, not {year}")
            return notes
    if spec.get("year_check_re"):
        yrx = fmt(spec["year_check_re"])
        text = norm("\n".join(ln.text for ln in lines))
        if not re.search(yrx, text, re.I):
            prev_text = norm("\n".join(ln.text for ln in tail))
            if not _ANY_YEAR_HEADING.search(text) and re.search(yrx, prev_text, re.I):
                notes.append("year heading carried over from previous page")
            else:
                raise LookupError("year heading not on page")
    return notes


def parse_spec_on_page(spec: dict, year: int, lines: list[tables.Line],
                       prev_lines: list[tables.Line] | None = None) -> dict:
    """Run the layout parser for one spec on one page. Returns a dict with
    'categories' {label: {(level, basis): value}}, 'totals' {(level, basis): value},
    'n_cells', 'notes'. Raises on failure."""
    fmt = lambda s: s.replace("{year}", str(year)) if s else s  # noqa: E731
    notes = check_headings(spec, year, lines, prev_lines or [])
    layout = spec["layout"]
    cats: dict[str, dict] = {}
    cells: dict[str, dict] = {}  # label -> key -> printed cells added into the value
    totals: dict = {}
    n_cells: dict = {}
    if layout == "rows":
        t = tables.parse_rows(lines, fmt(spec["start_re"]), spec["ncols"],
                              total_re=fmt(spec.get("total_re", r"^(grand\s*)?total")),
                              skip_re=spec.get("skip_re"), join_first=spec.get("join_first", False),
                              tol=spec.get("col_tol", 12.0), align=spec.get("align", {}).get(year, "right"))
        for key, idx in spec["columns"].items():
            n_cells[key] = 0
            for r in t.rows:
                v = r.values[idx]
                if v is None:
                    continue
                cats.setdefault(r.label, {})[key] = cats.get(r.label, {}).get(key, 0.0) + v
                cells.setdefault(r.label, {}).setdefault(key, []).append(v)
                n_cells[key] += 1
            totals[key] = t.total[idx]
        notes += t.notes
        start = _start_index(lines, fmt(spec["start_re"]))
    elif layout == "columns":
        t = tables.parse_sector_columns(lines, fmt(spec["start_re"]), spec["sectors"], spec["row_res"],
                                        fmt(spec["end_re"]), spec["anchor_re"])
        (key,) = spec["columns"].keys()
        sums = tables.column_sums(t)
        n_cells[key] = sum(1 for r in t.rows for v in r.values[:-1] if v)
        for j, sec in enumerate(spec["sectors"]):
            cats[sec] = {key: sums[j]}
            cells[sec] = {key: [r.values[j] for r in t.rows if r.values[j] is not None]}
        totals[key] = sums[-1]
        notes.append("loans rows summed: " + "; ".join(r.label for r in t.rows))
        notes.append("printed total = sum of the Total column over those rows")
        start = _start_index(lines, fmt(spec["start_re"]))
    elif layout == "blocks":
        (key,) = spec["columns"].keys()
        n_cells[key] = 0
        totals[key] = 0.0
        prev_end = 0
        for b in spec["blocks"]:
            sub = lines[prev_end:] if b.get("after_previous") else lines
            t = tables.parse_rows(sub, fmt(b["start_re"]), b["ncols"], total_re=fmt(spec["total_re"]),
                                  skip_re=spec.get("skip_re"))
            for r in t.rows:
                v = r.values[b["value_col"]] or 0.0
                cats.setdefault(r.label, {})[key] = cats.get(r.label, {}).get(key, 0.0) + v
                cells.setdefault(r.label, {}).setdefault(key, []).append(v)
                n_cells[key] += 1
            totals[key] += t.total[b["value_col"]] or 0.0
            # position of this block's total line, so the next block starts after it
            tops = [ln.top for ln in sub]
            end_top = max(r.top for r in t.rows)
            prev_end = (len(lines) - len(sub)) + next(i for i, tp in enumerate(tops) if tp > end_top) + 1
            notes.append(f"{b['name']}: {len(t.rows)} rows, total {t.total[b['value_col']]:,.0f}")
        start = _start_index(lines, fmt(spec["blocks"][0]["start_re"]))
    else:
        raise ValueError(layout)
    units_txt, mult = detect_units(lines, start)
    if mult is None:
        raise LookupError("units not found on page")
    return dict(categories=cats, cells=cells, totals=totals, n_cells=n_cells, notes=notes, units=units_txt, mult=mult)


def run(banks: list[str] | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    files = source_files()
    rows, tot_rows, log = [], [], []
    for bank, specs in SPECS.items():
        if banks and bank not in banks:
            continue
        for spec in specs:
            for year in spec["years"]:
                if (bank, year) in SAMPLE_EXCLUSIONS:
                    continue
                pdf = files.get((bank, year))
                entry = dict(bank=bank, year=year, levels=";".join(f"{l}/{b}" for l, b in spec["columns"]),
                             source_file="", pdf_page="", status="", detail="")
                if pdf is None:
                    entry.update(status="fail", detail="no file")
                    log.append(entry)
                    continue
                entry["source_file"] = pdf.relative_to(ROOT).as_posix()
                texts = cached_texts(pdf)
                cands = [i + 1 for i, t in enumerate(texts) if re.search(spec["page_re"], norm(t), re.I)]
                errors = []
                result = None
                for p in cands:
                    kw = dict(space_thousands=year in spec.get("space_thousands_years", []),
                              crop_frac=spec.get("crop_frac", {}).get(year))
                    try:
                        lines = cached_lines(pdf, p, **kw)
                        prev = cached_lines(pdf, p - 1, **kw) if p > 1 else []
                        res = parse_spec_on_page(spec, year, lines, prev)
                        bad = reconcile(res)
                        known = {k: v for k, v in bad.items() if (bank, year) + k in PRINTED_INCONSISTENCIES}
                        if len(known) < len(bad):
                            raise ValueError("rows do not sum to total: " + "; ".join(bad.values()))
                        res["flags"] = {k: f"{v} -- printed inconsistency: {PRINTED_INCONSISTENCIES[(bank, year) + k]}"
                                        for k, v in known.items()}
                        res["page"] = p
                        result = res
                        break
                    except Exception as exc:  # try next candidate page
                        errors.append(f"p{p}: {type(exc).__name__}: {exc}"[:200])
                if result is None:
                    entry.update(status="fail", detail=" | ".join(errors) or "no candidate page")
                    log.append(entry)
                    continue
                flags = result.get("flags", {})
                entry.update(status="ok_flagged" if flags else "ok", pdf_page=result["page"],
                             detail=" | ".join(list(flags.values()) + result["notes"])[:700])
                log.append(entry)
                method = spec.get("method") or f"pdfplumber word positions; layout={spec['layout']}"
                for (level, basis), total in result["totals"].items():
                    for label, vals in result["categories"].items():
                        if (level, basis) not in vals:
                            continue
                        v = vals[(level, basis)]
                        rows.append(dict(bank=bank, year=year, level=level, basis=basis,
                                         units_as_printed=result["units"], printed_category=label,
                                         amount_printed=v, amount_naira=v * result["mult"],
                                         source_file=entry["source_file"], pdf_page=result["page"],
                                         extraction_method=method, main_spec="", note=spec.get("note", ""),
                                         printed_cells=" + ".join(f"{c:,.0f}" for c in
                                                                  result["cells"].get(label, {}).get((level, basis), []))))
                    tot_rows.append(dict(bank=bank, year=year, level=level, basis=basis,
                                         units_as_printed=result["units"],
                                         total_printed=total, total_naira=(total or 0) * result["mult"],
                                         n_printed_values=result["n_cells"][(level, basis)],
                                         total_type=("sum of printed row totals" if spec["layout"] == "columns"
                                                     else "sum of printed block totals" if spec["layout"] == "blocks"
                                                     else "printed total row"),
                                         source_file=entry["source_file"], pdf_page=result["page"],
                                         flag=flags.get((level, basis), "")))
    df = pd.DataFrame(rows, columns=OUT_COLUMNS)
    tot = pd.DataFrame(tot_rows)
    return df, tot, pd.DataFrame(log)


def mark_main_spec(df: pd.DataFrame) -> pd.DataFrame:
    """Main specification (plan section 3): group level where printed, else the
    reporting entity (bank); gross where printed, else carrying, else not stated."""
    order = {"gross": 0, "carrying": 1, "not_stated": 2}
    df = df.copy()
    df["main_spec"] = False
    for (bank, year), g in df.groupby(["bank", "year"]):
        level = "group" if (g["level"] == "group").any() else "bank"
        gl = g[g["level"] == level]
        basis = min(gl["basis"].unique(), key=lambda b: order[b])
        df.loc[gl[gl["basis"] == basis].index, "main_spec"] = True
    return df


def main(argv: list[str] | None = None) -> int:
    banks = argv or None
    df, tot, log = run(banks)
    df = mark_main_spec(df)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "loans_by_sector.csv", index=False)
    tot.to_csv(PROCESSED / "loans_totals.csv", index=False)
    log.to_csv(INTERIM / "phase1b_extract_log.csv", index=False)
    print(log[["bank", "year", "levels", "status", "pdf_page", "detail"]].to_string(max_colwidth=90))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception:
        traceback.print_exc()
        sys.exit(1)
