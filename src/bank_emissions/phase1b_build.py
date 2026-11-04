"""Phase 1b, steps 1-5: loans-note decisions, Jaiz 2024 OCR, random re-read,
and the plan's Phase 1b outputs (plan sections 2, 3, 8 and 9).

Inputs: data/processed/loans_by_sector.csv and loans_totals.csv (written by
phase1b_extract, unchanged here), the decisions in phase1b_config, and the
Jaiz FY2024 OCR (phase1b_ocr).

Outputs:
- data/processed/exposures_by_sector.csv  one row per bank-year-level-basis-category
- data/processed/sample.csv               bank-years included, flagged or excluded, with reasons
- data/interim/extraction_validation.csv  internal, external, evidence and re-read checks

    python -m bank_emissions.phase1b_build
"""

from __future__ import annotations

import random
import re
from pathlib import Path

import pandas as pd

from . import phase1b_ocr, tables
from .phase1b_config import (ALTERNATIVE_SOURCES, BASIS_DECISIONS, EXTERNAL_FLAGS, LEVEL_DEVIATIONS,
                             PRINTED_INCONSISTENCIES, RESIDUAL_LABEL, RESIDUAL_ROWS, SAMPLE_EXCLUSIONS,
                             SOURCE_DEVIATIONS, UNIT_DECISIONS, WEMA_UNIT_EVIDENCE_PAGES, YEARS)
from .phase1b_extract import INTERIM, PROCESSED, ROOT, cached_lines, cached_texts
from .phase1b_validate import table_matches

SEED = 20261104  # fixed seed for the section 8.1 re-read sample (date of the draw)
SAMPLE_SHARE = 0.05

BANKS = ["ACCESSCORP", "ZENITHBANK", "GTCO", "UBA", "FIRSTHOLDCO", "FIDELITYBK", "FCMB", "STANBIC",
         "STERLINGNG", "WEMABANK", "UNITYBNK", "JAIZBANK", "ETI"]

# Which entity a 'bank'-level column describes (plan section 3: record whether a
# column is the Nigerian bank, the holding company or neither).
BANK_ENTITY = {
    "ACCESSCORP": "Access Bank Plc (listed entity FY2020-FY2021)",
    "ZENITHBANK": "Zenith Bank Plc (separate statements)",
    "GTCO": "Guaranty Trust Bank Plc (listed entity FY2020, 'Parent' columns)",
    "UBA": "United Bank for Africa Plc (separate statements)",
    "FIDELITYBK": "Fidelity Bank Plc",
    "STERLINGNG": "Sterling Bank Plc (listed entity FY2020-FY2022)",
    "WEMABANK": "Wema Bank Plc (separate statements)",
    "UNITYBNK": "Unity Bank Plc (reporting entity; no group table)",
    "JAIZBANK": "Jaiz Bank Plc (reporting entity; no group table)",
}

EXPOSURE_COLUMNS = ["bank", "year", "reporting_date", "level", "level_entity", "basis", "basis_as_printed",
                    "units_as_printed", "units_applied", "printed_category", "amount_printed", "amount_naira",
                    "printed_cells", "source_file", "pdf_page", "printed_page", "extraction_method", "source_role",
                    "main_spec", "flag", "note"]


def external_flag(bank: str, year: int, level: str, basis_as_printed: str) -> str:
    return EXTERNAL_FLAGS.get((bank, year, level, basis_as_printed)) or EXTERNAL_FLAGS.get((bank, year, level), "")


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", s).lower()


# ---------------------------------------------------------------------------
# Jaiz FY2024 (OCR) and the Stanbic FY2023 alternative source


def jaiz_2024_rows() -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    """Apply the plan section 2 OCR rule. Returns exposure rows, the totals row
    and validation records; rows are empty if the rule fails."""
    r = phase1b_ocr.run_core()
    pdf = phase1b_ocr.PDF.relative_to(ROOT).as_posix()
    val = [dict(check="ocr_sum", bank="JAIZBANK", year=2024, level="bank", basis="gross",
                result="pass" if r["sum_ok"] else "fail",
                detail=f"OCR rows sum {r['sum']:,.0f} vs printed total {r['total']:,.0f} (tolerance {r['tol']:.1f})"),
           dict(check="ocr_loans_note", bank="JAIZBANK", year=2024, level="bank", basis="gross",
                result="pass" if r["loans_note_hits"] else "fail",
                detail="; ".join(f"p{h['page']}: {h['line']}" for h in r["loans_note_hits"])
                or "total not found on the loans-note page")]
    n_ok = sum(c["match_2024"] for c in r["checks"])
    val.append(dict(check="ocr_full_recheck", bank="JAIZBANK", year=2024, level="bank", basis="gross",
                    result="pass" if n_ok == len(r["checks"]) else "fail",
                    detail=f"{n_ok}/{len(r['checks'])} OCR values (13 sectors and the total) equal the FY2025 filing's "
                           f"2024 comparative column (text layer, p. 114); the 2023 column equals the FY2023 filing "
                           f"({sum(c['match_2023'] for c in r['checks'])}/{len(r['checks'])}); every value also read "
                           f"on the rendered page. Details: data/interim/jaiz2024_ocr_check.csv. {r['tesseract']}"))
    keep = r["sum_ok"] and bool(r["loans_note_hits"])
    if not keep:
        return pd.DataFrame(columns=EXPOSURE_COLUMNS), pd.DataFrame(), val
    rows = [dict(bank="JAIZBANK", year=2024, level="bank", basis="not_stated", units_as_printed="N'000",
                 printed_category=label, amount_printed=v, amount_naira=v * 1e3, source_file=pdf,
                 pdf_page=phase1b_ocr.PAGE, extraction_method=phase1b_ocr.METHOD, printed_cells=f"{v:,.0f}",
                 note="no Group/Bank split printed; basis not stated on page")
            for label, v, _ in r["rows"]]
    tot = pd.DataFrame([dict(bank="JAIZBANK", year=2024, level="bank", basis="not_stated", units_as_printed="N'000",
                             total_printed=r["total"], total_naira=r["total"] * 1e3, n_printed_values=len(r["rows"]),
                             total_type="printed total row", source_file=pdf, pdf_page=phase1b_ocr.PAGE, flag="")])
    return pd.DataFrame(rows), tot, val


COMPARATIVE_ROLE = "comparative from the following year's report (main specification)"
RESIDUAL_ROLE = "computed residual (printed total less printed rows)"


def alternative_rows() -> tuple[pd.DataFrame, list[dict]]:
    rows, val = [], []
    for (bank, year, level), a in ALTERNATIVE_SOURCES.items():
        pdf = ROOT / "data" / "raw" / "annual_reports" / a["file"]
        t = tables.parse_rows(cached_lines(pdf, a["page"]), a["start_re"], a["ncols"], total_re=a["total_re"])
        vals = [r.values[a["value_col"]] or 0.0 for r in t.rows]
        total = t.total[a["value_col"]]
        tol = 0.5 * len(vals)
        val.append(dict(check="replacement_source", bank=bank, year=year, level=level, basis=a["basis"],
                        result="pass" if abs(sum(vals) - total) <= tol else "fail",
                        detail=f"{a['file']} p. {a['page']}: {len(vals)} rows sum {sum(vals):,.0f} vs printed total "
                               f"{total:,.0f} (tolerance {tol:.1f}); the FY{year} loans-note gross is the "
                               f"STANBIC {year} basis evidence"))
        for r in t.rows:
            v = r.values[a["value_col"]]
            if v is None:
                continue
            rows.append(dict(bank=bank, year=year, level=level, basis=a["basis"], basis_as_printed="carrying",
                             units_as_printed="N'million", printed_category=r.label, amount_printed=v,
                             amount_naira=v * 1e6, printed_cells=f"{v:,.0f}",
                             source_file=pdf.relative_to(ROOT).as_posix(), pdf_page=a["page"],
                             extraction_method="pdfplumber word positions; layout=rows",
                             source_role=COMPARATIVE_ROLE if a.get("main_spec") else
                             "alternative (not main specification)", note=a["note"]))
    return pd.DataFrame(rows), val


def residual_rows(d: pd.DataFrame) -> pd.DataFrame:
    """Printed total less printed sector rows, as one computed row (RESIDUAL_ROWS)."""
    tot = pd.read_csv(PROCESSED / "loans_totals.csv")
    rows = []
    for (bank, year, level, basis), note in RESIDUAL_ROWS.items():
        t = tot[(tot.bank == bank) & (tot.year == year) & (tot.level == level) & (tot.basis == basis)].iloc[0]
        g = d[(d.bank == bank) & (d.year == year) & (d.level == level) & (d.basis == basis)]
        v = float(t.total_printed) - float(g.amount_printed.sum())
        rows.append(dict(bank=bank, year=year, level=level, basis=basis, basis_as_printed=basis,
                         units_as_printed=g.units_as_printed.iloc[0], printed_category=RESIDUAL_LABEL,
                         amount_printed=v, amount_naira=v * float(t.total_naira) / float(t.total_printed),
                         printed_cells="", source_file=t.source_file, pdf_page=int(t.pdf_page),
                         extraction_method="computed: printed total less the printed sector rows",
                         source_role=RESIDUAL_ROLE, note=note))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Decisions and their evidence


def verify_evidence() -> list[dict]:
    """Re-check that each decision's evidence figure is printed on its page."""
    out = []
    for (bank, year), (printed, resolved, page, fig, reason) in BASIS_DECISIONS.items():
        if (bank, year) == ("JAIZBANK", 2024):
            continue  # scanned filing: checked by OCR in jaiz_2024_rows
        texts = cached_texts(_source(bank, year))
        ok = fig in texts[page - 1]
        out.append(dict(check="basis_evidence", bank=bank, year=year, level="", basis=resolved,
                        result="pass" if ok else "fail",
                        detail=f"{printed} -> {resolved}: '{fig}' on p. {page}: {reason}"))
    for (bank, year), (mult, units, why) in UNIT_DECISIONS.items():
        texts = cached_texts(_source(bank, year))
        sofp, note = WEMA_UNIT_EVIDENCE_PAGES[year]
        ok = all(re.search(r"(?i)in thousands of nigeria", texts[p - 1]) for p in (sofp, note))
        out.append(dict(check="units_evidence", bank=bank, year=year, level="", basis="",
                        result="pass" if ok else "fail", detail=f"applied {units}: {why}"))
    return out


_SOURCES: dict = {}


def _source(bank: str, year: int) -> Path:
    if not _SOURCES:
        t = pd.read_csv(PROCESSED / "loans_totals.csv")
        for _, r in t.iterrows():
            _SOURCES[(r.bank, int(r.year))] = ROOT / r.source_file
    return _SOURCES[(bank, year)]


def apply_decisions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "basis_as_printed" not in df or df["basis_as_printed"].isna().all():
        df["basis_as_printed"] = df["basis"]
    df["basis_as_printed"] = df["basis_as_printed"].fillna(df["basis"])
    for i, r in df.iterrows():
        d = BASIS_DECISIONS.get((r.bank, int(r.year)))
        if d and r.source_role == "extracted" and r.basis_as_printed == d[0]:
            df.at[i, "basis"] = d[1]
        u = UNIT_DECISIONS.get((r.bank, int(r.year)))
        if u:
            df.at[i, "units_applied"] = u[1]
            df.at[i, "amount_naira"] = r.amount_printed * u[0]
    return df


def _units_applied(units_as_printed: str) -> str:
    s = units_as_printed.lower()
    return "millions of naira" if "million" in s or "n'm" in s else "thousands of naira"


def build_exposures(jaiz: pd.DataFrame, alt: pd.DataFrame) -> pd.DataFrame:
    d = pd.read_csv(PROCESSED / "loans_by_sector.csv")
    d["basis_as_printed"] = d["basis"]
    d["source_role"] = "extracted"
    d = pd.concat([d, residual_rows(d), jaiz.assign(basis_as_printed="not_stated", source_role="extracted"), alt],
                  ignore_index=True)
    d["units_applied"] = d["units_as_printed"].map(_units_applied)
    d = apply_decisions(d)
    d["reporting_date"] = d["year"].astype(int).astype(str) + "-12-31"
    d["level_entity"] = [("group (consolidated)" if lv == "group" else BANK_ENTITY.get(b, ""))
                         for b, lv in zip(d.bank, d.level)]
    d["printed_page"] = ""  # PDF page indices are recorded; printed page numbers not read reliably
    flags = []
    for _, r in d.iterrows():
        if r.source_role == COMPARATIVE_ROLE:  # flags describe the replaced table, not the comparative
            flags.append("")
            continue
        f = [PRINTED_INCONSISTENCIES.get((r.bank, int(r.year), r.level, r.basis_as_printed), ""),
             external_flag(r.bank, int(r.year), r.level, r.basis_as_printed)]
        flags.append(" | ".join(x for x in f if x))
    d["flag"] = flags
    # main specification (plan section 3): group where printed, else the reporting
    # entity; gross where printed, else carrying (not stated treated as carrying)
    order = {"gross": 0, "carrying": 1, "not_stated": 2}
    d["main_spec"] = False
    replaced = {(b, y) for (b, y, _), a in ALTERNATIVE_SOURCES.items() if a.get("main_spec")}
    d.loc[d.source_role == COMPARATIVE_ROLE, "main_spec"] = True
    ext = d[d.source_role.isin(["extracted", RESIDUAL_ROLE])]
    for (bank, year), g in ext.groupby(["bank", "year"]):
        if (bank, int(year)) in replaced:
            continue  # defective table replaced by the following year's comparative
        level = "group" if (g.level == "group").any() else "bank"
        gl = g[g.level == level]
        basis = min(gl.basis.unique(), key=lambda b: order[b])
        d.loc[gl[gl.basis == basis].index, "main_spec"] = True
    return d[EXPOSURE_COLUMNS].sort_values(["bank", "year", "level", "basis", "source_role"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Validation records


def internal_checks(exp: pd.DataFrame, tot: pd.DataFrame) -> list[dict]:
    out = []
    for _, t in tot.iterrows():
        g = exp[(exp.bank == t.bank) & (exp.year == t.year) & (exp.level == t.level)
                & (exp.basis_as_printed == t.basis) & (exp.source_role == "extracted")]
        s = g.amount_printed.sum()
        tol = 0.5 * max(len(g), 1)
        diff = s - t.total_printed
        known = PRINTED_INCONSISTENCIES.get((t.bank, int(t.year), t.level, t.basis), "")
        res = "pass" if abs(diff) <= tol else ("flag (printed inconsistency)" if known else "fail")
        out.append(dict(check="internal_sum", bank=t.bank, year=int(t.year), level=t.level, basis=t.basis,
                        result=res, detail=f"rows {s:,.0f} vs printed total {t.total_printed:,.0f}, diff {diff:,.0f}, "
                                           f"tolerance {tol:.1f}" + (f"; {known}" if known else "")))
    return out


def external_checks(tot: pd.DataFrame) -> list[dict]:
    m = table_matches(tot[tot.source_file.str.endswith(".pdf")
                          & ~((tot.bank == "JAIZBANK") & (tot.year == 2024))])
    m.to_csv(INTERIM / "phase1b_total_matches.csv", index=False)
    out = []
    for (bank, year, level, basis), g in m.groupby(["bank", "year", "level", "basis"]):
        hits = g[g.page.astype(str) != ""]
        flag = external_flag(bank, int(year), level, basis)
        if len(hits):
            first = hits.iloc[0]
            res = "pass" if not flag else "flag"
            det = (f"total found on {hits.page.nunique()} other page(s); e.g. p{int(float(first.page))}: "
                   f"{str(first.line)[:150]}")
        else:
            res = "flag" if flag else "fail"
            det = "total not found elsewhere in the report within rounding"
        out.append(dict(check="external_total", bank=bank, year=int(year), level=level, basis=basis, result=res,
                        detail=det + (f"; {flag}" if flag else "")))
    return out


# ---------------------------------------------------------------------------
# Section 8.1: random re-read with a second text engine


def _variants(v: float) -> list[str]:
    a = f"{abs(v):,.0f}"
    plain = a.replace(",", "")
    return [a, plain] if len(plain) > 3 else [a]


def reread_cell(page_text: str, label: str, cells: list[float], derived: bool) -> tuple[str, str]:
    """Check sampled value(s) in the pypdfium2 text of the page."""
    sq = _norm(page_text)
    sq_digits = re.sub(r"[,\s]", "", page_text)
    nonzero = [c for c in cells if abs(c) >= 0.5]
    if not nonzero:
        return "pass (zero)", "printed as a dash or zero; not checkable by text search"
    if derived:
        missing = [c for c in nonzero if not any(x in sq or x in sq_digits for x in _variants(c))]
        return ("pass" if not missing else "fail"), (
            f"{len(nonzero) - len(missing)}/{len(nonzero)} component cells found on the page"
            + (f"; missing {missing}" if missing else ""))
    lab = _norm(label)
    starts = [m.start() for m in re.finditer(re.escape(lab), sq)] or \
             [m.start() for m in re.finditer(re.escape(lab[:12]), sq)]
    for st in starts:
        window = sq[st: st + len(lab) + 400]
        if any(x.lower() in window for x in _variants(nonzero[0])):
            return "pass", "value follows its row label in the second-engine text"
    if any(x in sq or x in sq_digits for x in _variants(nonzero[0])):
        return "pass (value on page)", "value printed on the page; row label not adjacent in the second-engine text"
    return "fail", "value not found on the page by the second engine"


def reread_sample(exp: pd.DataFrame) -> tuple[list[dict], pd.DataFrame]:
    rng = random.Random(SEED)
    pool = exp[(exp.source_role == "extracted") & ~exp.extraction_method.str.startswith("OCR")].copy()
    pool["table"] = pool.bank + "|" + pool.year.astype(str) + "|" + pool.level + "|" + pool.basis_as_printed
    idx = set(rng.sample(sorted(pool.index), max(1, round(SAMPLE_SHARE * len(pool)))))
    full_tables = set()
    for bank in sorted(pool.bank.unique()):
        t = rng.choice(sorted(pool[pool.bank == bank].table.unique()))
        full_tables.add(t)
        idx |= set(pool[pool.table == t].index)
    rows = []
    for i in sorted(idx):
        r = pool.loc[i]
        cells = [float(x.replace(",", "")) for x in str(r.printed_cells).split(" + ") if x and x != "nan"]
        derived = len(cells) > 1 or "layout=columns" in r.extraction_method or "layout=blocks" in r.extraction_method
        text = cached_texts(ROOT / r.source_file)[int(r.pdf_page) - 1]
        res, det = reread_cell(text, r.printed_category, cells or [r.amount_printed], derived)
        rows.append(dict(bank=r.bank, year=int(r.year), level=r.level, basis=r.basis_as_printed,
                         printed_category=r.printed_category, amount_printed=r.amount_printed,
                         printed_cells=r.printed_cells, pdf_page=int(r.pdf_page), table=r.table,
                         complete_table=r.table in full_tables,
                         result=res, detail=det))
    rr = pd.DataFrame(rows)
    summary = dict(check="reread_sample", bank="", year="", level="", basis="",
                   result="pass" if not (rr.result == "fail").any() else "fail",
                   detail=f"seed {SEED}; {len(rr)} values re-read ({len(rr) / len(pool):.1%} of {len(pool)} extracted "
                          f"text-layer values), including one complete table per bank; second engine: pypdfium2 "
                          f"page text; failures: {(rr.result == 'fail').sum()}")
    return [summary], rr


# ---------------------------------------------------------------------------
# sample.csv


def build_sample(exp: pd.DataFrame, val: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for bank in BANKS:
        for year in YEARS:
            base = dict(bank=bank, year=year)
            if (bank, year) in SAMPLE_EXCLUSIONS:
                rows.append(base | dict(status="excluded", reason=SAMPLE_EXCLUSIONS[(bank, year)]))
                continue
            g = exp[(exp.bank == bank) & (exp.year == year) & (exp.source_role == "extracted")]
            if g.empty:
                rows.append(base | dict(status="excluded", reason="no sector table extracted (OCR rule failed)"
                                        if (bank, year) == ("JAIZBANK", 2024) else "no sector table extracted"))
                continue
            m = exp[(exp.bank == bank) & (exp.year == year) & exp.main_spec]
            flags = sorted({f for f in g.flag if f})
            if m.empty:
                status, reason = "flagged: not in main specification", " | ".join(flags)
            else:
                dev = (bank, year) in SOURCE_DEVIATIONS or (bank, year) in LEVEL_DEVIATIONS
                status = "included" + (" (flagged)" if any(m.flag) else "") + (" (deviation)" if dev else "")
                reason = " | ".join(sorted({f for f in m.flag if f}))
            lv = m.level.iloc[0] if len(m) else ""
            rows.append(base | dict(
                status=status, reason=reason,
                main_level=lv, main_basis=m.basis.iloc[0] if len(m) else "",
                main_level_entity=m.level_entity.iloc[0] if len(m) else "",
                units_applied=m.units_applied.iloc[0] if len(m) else "",
                n_categories=len(m), main_total_naira=m.amount_naira.sum() if len(m) else None,
                sensitivity_tables=";".join(sorted({f"{a}/{b}" for a, b in zip(g.level, g.basis)}
                                                   - ({f"{lv}/{m.basis.iloc[0]}"} if len(m) else set()))),
                deviation=" | ".join(x for x in (LEVEL_DEVIATIONS.get((bank, year), ""),
                                                 SOURCE_DEVIATIONS.get((bank, year), "")) if x),
                source_file=(m if len(m) else g).source_file.iloc[0],
                pdf_page=int((m if len(m) else g).pdf_page.iloc[0])))
    return pd.DataFrame(rows)


def main() -> int:
    jaiz, jaiz_tot, val = jaiz_2024_rows()
    alt, alt_val = alternative_rows()
    val += alt_val
    exp = build_exposures(jaiz, alt)
    tot = pd.read_csv(PROCESSED / "loans_totals.csv")
    tot_all = pd.concat([tot, jaiz_tot], ignore_index=True)
    val += verify_evidence()
    val += internal_checks(exp, tot_all)
    val += external_checks(tot)
    summ, rr = reread_sample(exp)
    val += summ
    v = pd.DataFrame(val)
    sample = build_sample(exp, v)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    exp.to_csv(PROCESSED / "exposures_by_sector.csv", index=False)
    sample.to_csv(PROCESSED / "sample.csv", index=False)
    v.to_csv(INTERIM / "extraction_validation.csv", index=False)
    rr.to_csv(INTERIM / "extraction_reread_sample.csv", index=False)
    print(v.groupby(["check", "result"]).size().to_string())
    print(sample.status.value_counts().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
