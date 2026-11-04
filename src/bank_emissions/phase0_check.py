"""Phase 0 feasibility checks.

Run from the project root:

    python -m bank_emissions.phase0_check            # all stages
    python -m bank_emissions.phase0_check --stage banks

Stages: banks, annual, sustainability, intensity, report.
Outputs:
    data/raw/...                      downloaded files (gitignored)
    data/interim/phase0_sources.csv   one row per document checked
    data/interim/phase0_banks.csv     bank list from the NGX directory
    data/interim/phase0_*.json        stage caches used by the report stage
    docs/phase0_results.md            written by the report stage
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import pandas as pd
import requests

from . import ngx, pdfscan
from .fetch import UA, download, sha256_file
from .sources import (BANKS, INTENSITY_SOURCES, IR_ANNUAL_REPORTS, IR_NOTES,
                      SUSTAINABILITY_REPORTS, YEARS)

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
DOCS = ROOT / "docs"
TODAY = dt.date.today().isoformat()


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _save_json(name: str, obj) -> None:
    INTERIM.mkdir(parents=True, exist_ok=True)
    (INTERIM / name).write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")


def _load_json(name: str):
    p = INTERIM / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _rel(p: str | Path) -> str:
    try:
        return Path(p).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


# --- stage a: bank list --------------------------------------------------

def stage_banks() -> None:
    rows, raw = ngx.company_directory()
    dest = RAW / "ngx" / f"ngx_company_directory_{TODAY}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    by_sym = {r["Symbol"]: r for r in rows}
    out = []
    for sym, meta in BANKS.items():
        r = by_sym.get(sym)
        out.append({
            "symbol": sym,
            "name_in_registry": meta["name"],
            "listed_on_ngx_directory": r is not None,
            "ngx_company_name": (r or {}).get("CompanyName", ""),
            "ngx_subsector": (r or {}).get("SubSector", ""),
            "ngx_board": (r or {}).get("MarketClassification", ""),
            "ngx_date_listed": ((r or {}).get("DateListed") or "")[:10],
            "ngx_nature_of_business": ((r or {}).get("NatureofBusiness") or "").strip(),
            "ngx_website": (r or {}).get("Website", ""),
        })
    # Any other NGX issuer in the Banking subsector not in the registry
    extra = [r["Symbol"] for r in rows if r.get("SubSector") == "Banking" and r["Symbol"] not in BANKS]
    _save_json("phase0_banks.json", {
        "checked_utc": _now(),
        "directory_file": _rel(dest),
        "directory_sha256": sha256_file(dest),
        "directory_records": len(rows),
        "banking_subsector_not_in_registry": extra,
        "banks": out,
    })
    pd.DataFrame(out).to_csv(INTERIM / "phase0_banks.csv", index=False)
    print(f"banks: {sum(b['listed_on_ngx_directory'] for b in out)}/{len(out)} found; extra banking issuers: {extra}")


# --- stage b: annual reports --------------------------------------------

def _ngx_filings_cached(symbol: str, attempts: int = 4) -> list[dict]:
    """NGX filings for a symbol, retried, cached in data/raw/ngx/ (one file per day)."""
    cache = RAW / "ngx" / f"filings_{symbol}_{TODAY}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    last = None
    for i in range(attempts):
        try:
            rows = ngx.filings(symbol)
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(rows, indent=1), encoding="utf-8")
            return rows
        except requests.RequestException as exc:
            last = exc
            import time
            time.sleep(10 * (i + 1))
    raise last


def _ngx_audited(sym: str) -> dict[int, dict]:
    merged: dict[int, dict] = {}
    for s in BANKS[sym]["ngx_symbols"]:
        for fy, row in ngx.audited_fy_filings(_ngx_filings_cached(s)).items():
            # first symbol listed takes precedence (current listed entity)
            merged.setdefault(fy, row)
    return merged


def stage_annual(workers: int = 7) -> None:
    """Banks are processed in parallel (hosts differ in speed); years in sequence."""
    import threading
    from concurrent.futures import ThreadPoolExecutor

    results: list[dict] = []
    lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(lambda s: _annual_for([s], results, lock), BANKS))
    order = {s: i for i, s in enumerate(BANKS)}
    results.sort(key=lambda r: (order[r["symbol"]], r["year"]))
    _save_json("phase0_annual.json", results)


def _annual_for(syms: list[str], results: list[dict], lock) -> None:
    for sym in syms:
        try:
            ngx_rows = _ngx_audited(sym)
        except requests.RequestException as exc:
            ngx_rows, ngx_err = {}, str(exc)
        else:
            ngx_err = ""
        for year in YEARS:
            ir_url = IR_ANNUAL_REPORTS.get((sym, year), "")
            ngx_row = ngx_rows.get(year)
            ngx_url = ngx_row["url"] if ngx_row else ""
            rec = {"doc_type": "annual_report", "symbol": sym, "bank": BANKS[sym]["name"],
                   "year": year, "ir_url": ir_url, "ngx_url": ngx_url,
                   "ngx_description": ngx_row["description"] if ngx_row else "",
                   "ngx_posted": ngx_row["posted"] if ngx_row else "",
                   "ir_note": IR_NOTES.get(sym, ""), "checked_utc": _now()}
            tried = []
            fetched = None
            for src, url in (("ir", ir_url), ("ngx", ngx_url)):
                if not url:
                    continue
                dest = RAW / "annual_reports" / f"{sym}_{year}_{src}.pdf"
                fr = download(url, dest)
                tried.append(f"{src}: {fr.error or 'ok'}")
                if not fr.error and fr.is_pdf:
                    fetched = (src, fr)
                    break
            rec["download_attempts"] = " | ".join(tried) if tried else ("no URL found" + (f"; NGX query error {ngx_err}" if ngx_err else ""))
            if fetched:
                src, fr = fetched
                rec.update(source_used=src, url=fr.url, local_path=_rel(fr.local_path),
                           file_size_bytes=fr.file_size_bytes, sha256=fr.sha256)
                try:
                    texts = pdfscan.page_texts(Path(fr.local_path))
                    sc = pdfscan.scan_sector_table(texts, year=year)
                    rec.update(n_pages=sc.n_pages, text_pages=sc.text_pages,
                               text_layer="yes" if sc.text_pages >= 0.8 * max(sc.n_pages, 1) else
                               ("partial" if sc.text_pages else "no (scanned images)"),
                               sector_table_found=sc.best_page is not None,
                               sector_best_page=sc.best_page,
                               sector_candidate_pages=";".join(map(str, sc.candidate_pages)),
                               sector_gross_net_auto=sc.gross_or_net,
                               sector_level_auto=sc.level,
                               sector_categories_auto=sc.categories)
                    if year == max(YEARS):
                        countries, cpages = pdfscan.foreign_countries(texts)
                        rec["foreign_countries_auto"] = "; ".join(countries)
                        rec["foreign_country_pages"] = ";".join(map(str, cpages[:30]))
                        disc = pdfscan.scan_disclosures(texts)
                        rec["ar_disclosures"] = json.dumps(disc)
                except Exception as exc:  # keep going; record the failure
                    rec["scan_error"] = f"{type(exc).__name__}: {exc}"[:300]
            else:
                rec["source_used"] = ""
            with lock:
                results.append(rec)
                print(sym, year, rec.get("source_used") or "MISSING", rec.get("sector_best_page"), rec["download_attempts"][:120], flush=True)
                _save_json("phase0_annual.json", results)


# --- stage c: sustainability reports ------------------------------------

def stage_sustainability() -> None:
    results = []
    for sym, item in SUSTAINABILITY_REPORTS.items():
        rec = {"doc_type": "sustainability_report", "symbol": sym, "bank": BANKS[sym]["name"],
               "checked_utc": _now()}
        if item is None:
            rec.update(year="", url="", download_attempts="no standalone sustainability report located")
            results.append(rec)
            continue
        year, url = item
        rec.update(year=year, url=url)
        dest = RAW / "sustainability" / f"{sym}_{year}_sustainability.pdf"
        fr = download(url, dest)
        rec["download_attempts"] = fr.error or "ok"
        if not fr.error:
            rec.update(local_path=_rel(fr.local_path), file_size_bytes=fr.file_size_bytes, sha256=fr.sha256)
            texts = pdfscan.page_texts(dest)
            rec["n_pages"] = len(texts)
            rec["text_pages"] = sum(1 for t in texts if len(t.strip()) > 50)
            rec["disclosures"] = json.dumps(pdfscan.scan_disclosures(texts))
        results.append(rec)
        print(sym, year, rec["download_attempts"][:100], flush=True)
        _save_json("phase0_sustainability.json", results)
    _save_json("phase0_sustainability.json", results)


# --- stage d: emission-intensity sources --------------------------------

def stage_intensity() -> None:
    results = []
    for key, url in INTENSITY_SOURCES.items():
        rec = {"doc_type": "intensity_source", "symbol": "", "bank": "", "year": "",
               "source_key": key, "url": url, "checked_utc": _now()}
        if key == "climate_watch_api":
            try:
                ds = requests.get(url + "/data_sources", headers=UA, timeout=60).json()["data"]
                cov = {}
                for d in ds:
                    rows, page = [], 1
                    while True:
                        r = requests.get(url, params={"regions[]": "NGA", "source_ids[]": d["id"],
                                                      "per_page": 200, "page": page},
                                         headers=UA, timeout=60).json()["data"]
                        rows += r
                        if len(r) < 200:
                            break
                        page += 1
                    yrs = sorted({e["year"] for x in rows for e in x["emissions"] if e["value"] is not None})
                    cov[d["name"]] = {"rows": len(rows), "first_year": yrs[0] if yrs else None,
                                      "last_year": yrs[-1] if yrs else None,
                                      "sectors": sorted({x["sector"] for x in rows})}
                    if rows:
                        p = RAW / "intensity" / f"climatewatch_NGA_{d['name']}_{TODAY}.json"
                        p.parent.mkdir(parents=True, exist_ok=True)
                        p.write_text(json.dumps(rows), encoding="utf-8")
                rec["download_attempts"] = "ok"
                rec["coverage"] = json.dumps(cov)
            except Exception as exc:
                rec["download_attempts"] = f"{type(exc).__name__}: {exc}"[:300]
            results.append(rec)
            continue
        name = {"unfccc_btr1": "Nigeria_BTR1.pdf", "unfccc_btr1_nid": "Nigeria_BTR1_NID_2024.pdf",
                "nbs_rebased_gdp": "nbs_microdata_147_1256.pdf",
                "pcaf_database_sheet": "PCAF-2025Database-2Pager-R2.pdf"}[key]
        dest = RAW / "intensity" / name
        fr = download(url, dest)
        rec["download_attempts"] = fr.error or ("ok (local copy)" if fr.http_status == 0 else "ok")
        if not fr.error:
            rec.update(local_path=_rel(dest), file_size_bytes=fr.file_size_bytes, sha256=fr.sha256)
            texts = pdfscan.page_texts(dest)
            rec["n_pages"] = len(texts)
        results.append(rec)
        print(key, rec["download_attempts"][:120], flush=True)
    _save_json("phase0_intensity.json", results)


# --- combined source log ------------------------------------------------

SOURCE_COLS = ["doc_type", "symbol", "bank", "year", "source_used", "url", "ir_url", "ngx_url",
               "ngx_description", "ngx_posted", "download_attempts", "local_path",
               "file_size_bytes", "sha256", "n_pages", "text_pages", "text_layer",
               "sector_table_found", "sector_best_page", "sector_candidate_pages",
               "sector_gross_net_auto", "sector_level_auto", "sector_categories_auto",
               "source_key", "ir_note", "checked_utc"]


def write_source_log() -> pd.DataFrame:
    rows = []
    for name in ("phase0_annual.json", "phase0_sustainability.json", "phase0_intensity.json"):
        rows += _load_json(name) or []
    banks = _load_json("phase0_banks.json")
    if banks:
        rows.append({"doc_type": "ngx_company_directory", "url": ngx.DIRECTORY_URL,
                     "local_path": banks["directory_file"], "sha256": banks["directory_sha256"],
                     "download_attempts": "ok", "checked_utc": banks["checked_utc"]})
    df = pd.DataFrame(rows)
    for c in SOURCE_COLS:
        if c not in df.columns:
            df[c] = ""
    df = df[SOURCE_COLS]
    df.to_csv(INTERIM / "phase0_sources.csv", index=False)
    return df


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=["banks", "annual", "sustainability", "intensity", "report", "all"], default="all")
    args = ap.parse_args(argv)
    stages = {"banks": stage_banks, "annual": stage_annual, "sustainability": stage_sustainability,
              "intensity": stage_intensity}
    run = list(stages) if args.stage == "all" else ([args.stage] if args.stage != "report" else [])
    for s in run:
        print(f"== stage {s}", flush=True)
        stages[s]()
    write_source_log()
    if args.stage in ("report", "all"):
        from .phase0_report import write_report
        write_report()
    return 0


if __name__ == "__main__":
    sys.exit(main())
