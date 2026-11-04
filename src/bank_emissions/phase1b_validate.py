"""Phase 1b validation (plan section 8): external consistency of the sector tables.

For every extracted table (bank, year, level, basis) the printed total is looked
for on the other pages of the same report: any printed number within the
section 8.2 rounding tolerance (half a printed unit per sector row, at least 1)
counts as a match. Each match is recorded with its page and the text of the
line it sits on, so the label it carries ("Gross loans and receivables", "Net
loans and advances to customers", a statement-of-financial-position line) can
be read. Those matches are the evidence for the basis and units decisions in
phase1b_config.LOANS_NOTE_DECISIONS.

    python -m bank_emissions.phase1b_validate
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .phase1b_extract import INTERIM, PROCESSED, ROOT, cached_texts

_NUM = re.compile(r"(?<![\d,.])\(?\d{1,3}(?:,\d{3})+(?:\.\d+)?\)?(?![\d,])")


def _value(tok: str) -> float:
    return float(tok.strip("()").replace(",", ""))


def find_matches(texts: list[str], total: float, tol: float, skip_page: int) -> list[dict]:
    """Printed numbers within ``tol`` of ``total`` on pages other than ``skip_page``."""
    out = []
    for p, tx in enumerate(texts, start=1):
        if p == skip_page:
            continue
        lines = tx.splitlines()
        # not preceded by a digit or 'digit + space' (that would make it the tail of a longer spaced number)
        spaced = re.compile(r"(?<!\d)(?<!\d )" + re.escape(f"{int(round(abs(total))):,}".replace(",", " ")) + r"(?![\d])")
        for i, ln in enumerate(lines):
            found = [(m.group(), _value(m.group())) for m in _NUM.finditer(ln)]
            # reports that separate thousands with spaces (FCMB FY2025): exact printed form only
            found += [(m.group(), abs(total)) for m in spaced.finditer(ln)]
            for printed, v in found:
                if abs(v - abs(total)) <= tol:
                    prev = lines[i - 1].strip() if i else ""
                    out.append(dict(page=p, printed=printed, diff=v - abs(total),
                                    line=re.sub(r"\s+", " ", ln.strip())[:200],
                                    prev_line=re.sub(r"\s+", " ", prev)[:120]))
    return out


def table_matches(tot: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in tot.iterrows():
        texts = cached_texts(ROOT / r.source_file)
        tol = max(1.0, 0.5 * r.n_printed_values)
        ms = find_matches(texts, r.total_printed, tol, int(r.pdf_page))
        if not ms:
            rows.append(dict(bank=r.bank, year=r.year, level=r.level, basis=r.basis, total_printed=r.total_printed,
                             page="", printed="", diff="", line="", prev_line=""))
        for m in ms:
            rows.append(dict(bank=r.bank, year=r.year, level=r.level, basis=r.basis,
                             total_printed=r.total_printed, **m))
    return pd.DataFrame(rows)


def main() -> int:
    tot = pd.read_csv(PROCESSED / "loans_totals.csv")
    m = table_matches(tot)
    m.to_csv(INTERIM / "phase1b_total_matches.csv", index=False)
    n = m[m.page != ""].groupby(["bank", "year", "level", "basis"]).size()
    print(f"{len(tot)} tables, {len(n)} with at least one match elsewhere in the report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
