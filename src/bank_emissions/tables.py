"""Position-aware table parsing for the bank sector notes (Phase 1b).

The Phase 0 extraction test parsed PDF text line by line. That fails where the
text layer drops dash placeholders for empty cells (UBA 2023 "Others", Fidelity
"Finance and insurance", Unity 2023 "Transportation"), where a page comes back
as one run-on line (GTCO), and where thousands are separated by spaces (FCMB
2025). This module works from word coordinates instead (pdfplumber):

1. ``page_lines`` groups words into visual lines and splits each line into a
   label (text up to the last alphabetic word) and numeric tokens with their
   right-edge x position.
2. Numeric tokens are assigned to columns by matching their right edge to the
   right edges of the tokens in an anchor line (normally the table's total row,
   which has every column filled). Numbers in these reports are right-aligned.
3. Three layout parsers sit on top:
   - ``parse_rows``: sectors are rows, value columns are picked by index
     (Access, Zenith, FCMB, Sterling, Wema, Unity, Jaiz, and the
     multi-asset-class tables of Fidelity and Stanbic).
   - ``parse_sector_columns``: sectors are columns, asset classes are rows; the
     loans-to-customers rows are summed per column (GTCO, UBA).
   - ``parse_blocks``: several consecutive row tables whose last columns are
     added per sector (First HoldCo retail + corporate portfolios).

The functions below take ``Line`` objects so they can be tested without PDFs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

DASHES = {"-", "–", "—", "‐", "−"}
_NUM_RE = re.compile(r"^\(?-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\)?$")
# A comma-grouped figure whose last group is cut short ('7,178,47'), printed
# that way in the PDF (Wema FY2025). It is kept as an unreadable cell (value
# None) so that it holds its column and does not break the row.
_CLIPPED_RE = re.compile(r"^\(?\d{1,3}(?:,\d{3})*,\d{1,2}\)?$")
_PCT_RE = re.compile(r"^\(?-?\d+(?:\.\d+)?%\)?$")
_ALPHA_RE = re.compile(r"[A-Za-z]")


@dataclass
class Word:
    text: str
    x0: float
    x1: float
    top: float


@dataclass
class Num:
    raw: str
    value: float | None  # 0.0 for a dash; None for an unreadable (clipped) figure
    x1: float
    is_dash: bool = False
    x0: float | None = None  # left edge, for centre-aligned columns

    def pos(self, align: str = "right") -> float:
        if align == "center" and self.x0 is not None:
            return (self.x0 + self.x1) / 2
        if align == "left" and self.x0 is not None:
            return self.x0
        return self.x1


@dataclass
class Line:
    top: float
    label: str
    nums: list[Num] = field(default_factory=list)
    text: str = ""
    pcts: list[str] = field(default_factory=list)


def to_number(raw: str) -> float:
    """'1,234' -> 1234.0; '(1,234)' -> -1234.0; '-' -> 0.0; '1 234' -> 1234.0."""
    s = raw.strip()
    if s in DASHES:
        return 0.0
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace(",", "").replace(" ", "")
    v = float(s)
    return -v if neg else v


def is_numeric_token(t: str) -> bool:
    return t in DASHES or bool(_NUM_RE.match(t))


def merge_space_thousands(words: list[Word], max_gap: float = 3.0) -> list[Word]:
    """Join '2' '868' '168' printed with narrow spaces into '2868168'.

    A word is appended to the previous numeric word when it is exactly three
    digits (optionally followed by ')') and the horizontal gap is below
    ``max_gap`` points. Column gaps in the affected reports are 20+ points.
    """
    out: list[Word] = []
    for w in words:
        if (out and re.fullmatch(r"\d{3}\)?", w.text)
                and re.fullmatch(r"\(?\d{1,3}(?:\d{3})*", out[-1].text)
                and 0 <= w.x0 - out[-1].x1 < max_gap):
            prev = out[-1]
            out[-1] = Word(prev.text + w.text, prev.x0, w.x1, prev.top)
        else:
            out.append(w)
    return out


_GLUED_RE = re.compile(r"^(\(?\d{1,3}(?:,\d{3})+(?:\.\d+)?\)?)(\(?\d{1,3}(?:,\d{3})+(?:\.\d+)?\)?)$")


_SPILL_RE = re.compile(r"^(\d{1,3}(?:,\d{3})+)(\d{1,2})$")
_HEAD_RE = re.compile(r"^\d{1,2}(?:,\d{3})+$")


def _move_spilled_digits(words: list[Word]) -> list[Word]:
    """'577,3435' '20,164' -> '577,343' '520,164' (Jaiz FY2021 Mining row): the
    first digit of a number is attached to the previous word. Repaired only
    when the moved digits turn the next word on the same line into a valid
    comma-grouped number, so both results are well formed."""
    words = sorted(words, key=lambda w: (round(w.top), w.x0))
    for i in range(len(words) - 1):
        w, nx = words[i], words[i + 1]
        m = _SPILL_RE.match(w.text)
        if not m or abs(nx.top - w.top) > 1.5:
            continue
        head, tail = m.group(1), m.group(2)
        if not _HEAD_RE.match(nx.text) or not _NUM_RE.match(tail + nx.text) or len(tail + nx.text.split(",")[0]) > 3:
            continue
        xm = w.x0 + (w.x1 - w.x0) * len(head) / len(w.text)
        words[i] = Word(head, w.x0, xm, w.top)
        words[i + 1] = Word(tail + nx.text, xm, nx.x1, nx.top)
    return words


def split_glued_numbers(words: list[Word]) -> list[Word]:
    """Split two comma-grouped numbers printed without a gap and returned as one
    word ('83,530,8381,929,584,201' -> '83,530,838', '1,929,584,201'; FCMB
    2023 total row). With thousands separators the split point is unique: a
    group of exactly three digits after a comma ends the first number. The
    x-extent is shared out in proportion to the characters of each part."""
    words = _move_spilled_digits(words)
    out = []
    for w in words:
        m = _GLUED_RE.match(w.text)
        if not m:
            out.append(w)
            continue
        a, b = m.group(1), m.group(2)
        xm = w.x0 + (w.x1 - w.x0) * len(a) / len(w.text)
        out += [Word(a, w.x0, xm, w.top), Word(b, xm, w.x1, w.top)]
    return out


def words_to_lines(words: list[Word], y_tol: float = 2.5, space_thousands: bool = False) -> list[Line]:
    """Group words into visual lines (by top coordinate) and split label/numbers."""
    words = sorted(split_glued_numbers(words), key=lambda w: (round(w.top, 1), w.x0))
    groups: list[list[Word]] = []
    for w in words:
        if groups and abs(groups[-1][0].top - w.top) <= y_tol:
            groups[-1].append(w)
        else:
            groups.append([w])
    lines = []
    for g in groups:
        g.sort(key=lambda w: w.x0)
        if space_thousands:
            g = merge_space_thousands(g)
        lines.append(split_line(g))
    return lines


_MONTH_RE = re.compile(r"(?i)^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?$")
_YEAR_RE = re.compile(r"^(19|20)\d\d$")


def split_line(g: list[Word]) -> Line:
    """Split a visual line into label and numeric tokens.

    The numbers are the longest run of consecutive numeric/dash/percent tokens;
    the label is the text before that run (so 'General - Others' keeps its dash)
    and words after the run (page furniture such as 'Page') are ignored. A
    four-digit year directly after a month word ('Total at 31 December 2024')
    belongs to the label. Percentages are kept separately from numbers."""
    kinds = []
    for w in g:
        t = w.text.strip()
        kinds.append("p" if _PCT_RE.match(t) else ("n" if is_numeric_token(t) or _CLIPPED_RE.match(t) else "a"))
    # years after a month word are label text
    for i in range(1, len(g)):
        if kinds[i] == "n" and _YEAR_RE.match(g[i].text) and _MONTH_RE.match(g[i - 1].text):
            kinds[i] = "a"
    # a day number directly before a month word ('31 December') is label text
    for i in range(len(g) - 1):
        if kinds[i] == "n" and re.fullmatch(r"\d{1,2}", g[i].text) and _MONTH_RE.match(g[i + 1].text):
            kinds[i] = "a"
    best = (0, 0)  # (start, end) of longest numeric run
    i = 0
    while i < len(g):
        if kinds[i] in "np":
            j = i
            while j < len(g) and kinds[j] in "np":
                j += 1
            if j - i >= best[1] - best[0]:
                best = (i, j)
            i = j
        else:
            i += 1
    s, e = best
    if e == s:  # no numbers
        s = e = len(g)
    label = " ".join(w.text for w in g[:s]).strip()
    nums, pcts = [], []
    for w, k in zip(g[s:e], kinds[s:e]):
        t = w.text.strip()
        if k == "p":
            pcts.append(t)
        else:
            val = None if _CLIPPED_RE.match(t) and not _NUM_RE.match(t) else to_number(t)
            nums.append(Num(t, val, w.x1, t in DASHES, w.x0))
    return Line(top=g[0].top, label=label, nums=nums, text=" ".join(w.text for w in g), pcts=pcts)


def drop_overlapping_spaces(chars: list[dict], min_overlap: float = 0.3) -> list[dict]:
    """Remove space characters that overlap a printed character on the same line.

    Some reports (Unity Bank) place spurious space glyphs on top of digits, which
    split numbers such as '699,539' into '6' and '99,539'. Genuine spaces sit in
    the gap between characters and are kept."""
    solid = [c for c in chars if c["text"].strip()]
    buckets: dict[int, list[dict]] = {}
    for c in solid:
        buckets.setdefault(int(c["top"] // 4), []).append(c)
    out = []
    for c in chars:
        if c["text"].strip():
            out.append(c)
            continue
        k = int(c["top"] // 4)
        near = buckets.get(k, []) + buckets.get(k - 1, []) + buckets.get(k + 1, [])
        if any(abs(o["top"] - c["top"]) < 2 and min(o["x1"], c["x1"]) - max(o["x0"], c["x0"]) > min_overlap
               for o in near):
            continue
        out.append(c)
    return out


def page_lines(pdf_path: Path, page_no: int, space_thousands: bool = False, crop: tuple | None = None,
               x_tolerance: float = 3.0, crop_frac: tuple | None = None) -> list[Line]:
    """Lines of one PDF page (1-based page number). ``crop`` = (x0, top, x1, bottom)
    restricts the page area, for pages with two tables side by side;
    ``crop_frac`` gives the same box as fractions of the page size (for
    two-page spreads, (0.5, 0, 1, 1) is the right-hand page)."""
    import pdfplumber
    from pdfplumber.utils.text import extract_words

    with pdfplumber.open(str(pdf_path)) as pdf:
        page = pdf.pages[page_no - 1]
        if crop_frac:
            x0, t, x1, b = crop_frac
            crop = (x0 * float(page.width), t * float(page.height), x1 * float(page.width), b * float(page.height))
        if crop:
            page = page.crop(crop)
        chars = page.chars
        rotated = [c for c in chars if abs(c["matrix"][1]) > abs(c["matrix"][0])]  # "upright" flag is unreliable
        if len(rotated) > len(chars) / 2:
            # Table printed sideways (GTCO): map each character into the reading
            # frame and keep only the rotated text. The direction of rotation is
            # read from the text matrix.
            h, w = page.height, page.width
            ccw = sum(1 for c in rotated if c["matrix"][1] > 0) >= len(rotated) / 2
            if ccw:  # read bottom to top
                chars = [dict(c, x0=h - c["bottom"], x1=h - c["top"], top=c["x0"], bottom=c["x1"],
                              doctop=c["x0"], upright=True) for c in rotated]
            else:  # rotated clockwise, read top to bottom
                chars = [dict(c, x0=c["top"], x1=c["bottom"], top=w - c["x1"], bottom=w - c["x0"],
                              doctop=w - c["x1"], upright=True) for c in rotated]
        chars = drop_overlapping_spaces(chars)
        ws = extract_words(chars, x_tolerance=x_tolerance, y_tolerance=2)
    words = [Word(w["text"], w["x0"], w["x1"], w["top"]) for w in ws]
    return words_to_lines(words, space_thousands=space_thousands)


# ---------------------------------------------------------------------------
# Column assignment


def assign_columns(nums: list[Num], anchors: list[float], tol: float = 12.0,
                   align: str = "right") -> list[float | None]:
    """Map numeric tokens to anchor columns by nearest right edge.

    Returns one value per anchor (None where no token fell in the column).
    Raises ValueError if a token is farther than ``tol`` from every anchor or
    two tokens land in the same column. A line with exactly one token per
    column is assigned in order (its column is unambiguous), which handles
    total rows printed slightly offset from the body (Wema FY2025)."""
    out: list[float | None] = [None] * len(anchors)
    xs = [n.pos(align) for n in nums]
    if len(nums) == len(anchors) and xs == sorted(xs):
        return [n.value for n in nums]
    for n in nums:
        dists = [abs(n.pos(align) - a) for a in anchors]
        j = min(range(len(anchors)), key=lambda k: dists[k])
        if dists[j] > tol:
            raise ValueError(f"token {n.raw!r} at x={n.pos(align):.1f} is {dists[j]:.1f}pt from nearest column")
        if out[j] is not None:
            raise ValueError(f"two tokens in column {j} ({n.raw!r})")
        out[j] = n.value
    return out


# ---------------------------------------------------------------------------
# Layout parsers


@dataclass
class ParsedRow:
    label: str
    values: list[float | None]
    top: float


@dataclass
class ParsedTable:
    rows: list[ParsedRow]
    total: list[float | None] | None
    total_label: str
    anchors: list[float]
    notes: list[str] = field(default_factory=list)


def _find(lines: list[Line], pattern: str, start: int = 0, occurrence: int = 1) -> int:
    rx = re.compile(pattern, re.I)
    k = 0
    for i in range(start, len(lines)):
        if rx.search(lines[i].text):
            k += 1
            if k == occurrence:
                return i
    raise LookupError(f"pattern not found: {pattern!r} (occurrence {occurrence})")


_DAY_RE = re.compile(r"^\d{1,2}$")


def is_date_header(line: Line) -> bool:
    """Column-heading lines whose numeric tokens are only years and day numbers
    ('In thousands of Naira 2021 2020 2021 2020', '31 31 31 Dec Dec Dec 2023
    2022 ...'). They are not data rows. A line counts as a date header when it
    has at least one year token and every token is a year or a day number
    (1-31), or when its text contains month names and every token is a year
    or day."""
    if not line.nums:
        return False
    toks = [n.raw for n in line.nums]
    years = [t for t in toks if _YEAR_RE.match(t)]
    days = [t for t in toks if _DAY_RE.match(t) and 1 <= int(t) <= 31]
    if len(years) + len(days) != len(toks):
        return False
    return bool(years) or bool(re.search(r"(?i)\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b", line.text))


def _is_total(line: Line, total_re: str) -> bool:
    if not line.nums:
        return False
    return (not line.label) or bool(re.search(total_re, line.label, re.I))


def merge_wrapped(lines: list[Line], frag_gap: float = 4.0, wrap_gap: float = 8.0) -> list[Line]:
    """Repair two text-layer artefacts before rows are read.

    1. A row whose figures are printed slightly lower than its label for one
       cell comes back as a labelled line plus an unlabelled numeric fragment
       a few points below (Fidelity FY2025 'Finance and insurance'). The
       fragment is merged into the line above when it is within ``frag_gap``
       points.
    2. A label wrapped over two lines with the figures vertically centred
       ('Central Bank balance' / figures / '(restricted)') comes back as
       label-only, unlabelled numeric, label-only. The numeric line takes the
       label lines within ``wrap_gap`` points above and below.

    Without this the unlabelled numeric line would be read as a total row."""
    out: list[Line] = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.nums and not ln.label:
            prev = out[-1] if out else None
            nxt = lines[i + 1] if i + 1 < len(lines) else None
            if prev and prev.nums and prev.label and 0 <= ln.top - prev.top <= frag_gap:
                nums = sorted(prev.nums + ln.nums, key=lambda n: n.x1)
                out[-1] = Line(top=prev.top, label=prev.label, nums=nums, text=prev.text + " " + ln.text, pcts=prev.pcts)
                i += 1
                continue
            if prev and not prev.nums and prev.label and 0 <= ln.top - prev.top <= wrap_gap:
                label = prev.label
                if nxt and not nxt.nums and nxt.label and 0 <= nxt.top - ln.top <= wrap_gap:
                    label += " " + nxt.label
                    i += 1
                out[-1] = Line(top=ln.top, label=label, nums=ln.nums, text=label + " " + ln.text, pcts=ln.pcts)
                i += 1
                continue
        out.append(ln)
        i += 1
    return out


def parse_rows(lines: list[Line], start_re: str, ncols: int, total_re: str = r"^(grand\s*)?total",
               occurrence: int = 1, skip_re: str | None = None, join_labels: bool = True,
               join_gap: float = 14.0, anchor_re: str | None = None, join_first: bool = False,
               tol: float = 12.0, align: str = "right") -> ParsedTable:
    """Sector-as-row table. Rows run from the line after the ``start_re`` match
    to the first total line (unlabelled numeric line or label matching
    ``total_re``). Column anchors come from the total line, or from the first
    line matching ``anchor_re`` inside the block if given.

    A single label-only line directly above a numeric row (within ``join_gap``
    points) is joined to its label (multi-line labels such as 'ADMINISTRATIVE
    AND SUPPORT SERVICE / ACTIVITIES'). Before the first numeric row such lines
    are column headings and are not joined unless ``join_first`` is set (for a
    table whose first row label wraps). ``skip_re`` drops heading lines.
    ``tol`` is the column-matching tolerance in points (widened for reports
    whose figures and dashes are centred rather than right-aligned); ``align``
    = "center" ("left") matches tokens on their mid-points (left edges)
    instead of right edges."""
    i0 = _find(lines, start_re, occurrence=occurrence) + 1
    block: list[Line] = []
    total_line = None
    seen_row = False
    for ln in merge_wrapped(lines[i0:]):
        if is_date_header(ln):  # column headings such as '2021 2020 2021 2020' or '31 Dec 2023'
            continue
        if _is_total(ln, total_re) and any(not n.is_dash for n in ln.nums) and seen_row:
            total_line = ln
            break
        if ln.label and ln.nums and not (skip_re and re.search(skip_re, ln.label, re.I)):
            seen_row = True
        block.append(ln)
    if total_line is None:
        raise LookupError("no total line after start pattern")
    anchor_line = total_line
    if anchor_re:
        anchor_line = next(ln for ln in block + [total_line] if re.search(anchor_re, ln.text, re.I))
    if len(anchor_line.nums) != ncols:
        # fall back to the fullest numeric row in the block
        full = [ln for ln in block + [total_line] if len(ln.nums) == ncols]
        if not full:
            raise ValueError(f"no line with {ncols} numeric tokens to anchor columns")
        anchor_line = full[-1]
    anchors = [n.pos(align) for n in anchor_line.nums]

    rows: list[ParsedRow] = []
    pending: list[Line] = []
    notes: list[str] = []
    for ln in block:
        if skip_re and ln.label and re.search(skip_re, ln.label, re.I):
            pending = []
            continue
        if not ln.nums:
            if ln.label and join_labels and (rows or join_first):
                pending = [ln]
            continue
        label = ln.label
        if join_labels and pending and ln.top - pending[-1].top <= join_gap:
            label = " ".join([p.label for p in pending] + ([label] if label else []))
        pending = []
        if not label:
            notes.append(f"numeric line without label at top={ln.top:.0f} skipped: {ln.text[:60]}")
            continue
        for n in ln.nums:
            if n.value is None:
                notes.append(f"unreadable printed figure {n.raw!r} in row '{label.strip()}' left empty")
        rows.append(ParsedRow(label=re.sub(r"\s+", " ", label).strip(),
                              values=assign_columns(ln.nums, anchors, tol=tol, align=align), top=ln.top))
    total = assign_columns(total_line.nums, anchors, tol=tol, align=align)
    return ParsedTable(rows=rows, total=total, total_label=total_line.label, anchors=anchors, notes=notes)


def parse_sector_columns(lines: list[Line], start_re: str, sectors: list[str], row_res: list[str],
                         end_re: str, anchor_re: str, occurrence: int = 1) -> ParsedTable:
    """Sector-as-column table (GTCO, UBA). ``sectors`` are the printed column
    headers in order, followed by the Total column (so ``len(sectors) + 1``
    numeric columns). Rows whose label matches any of ``row_res`` between the
    ``start_re`` match and the ``end_re`` match are returned; anchors come from
    the first line matching ``anchor_re`` after the start (a fully filled total
    row)."""
    i0 = _find(lines, start_re, occurrence=occurrence)
    i1 = _find(lines, end_re, start=i0 + 1)
    ncols = len(sectors) + 1
    ia = _find(lines, anchor_re, start=i0 + 1)
    anchor_line = lines[ia]
    if len(anchor_line.nums) != ncols:
        raise ValueError(f"anchor line has {len(anchor_line.nums)} tokens, expected {ncols}: {anchor_line.text[:80]}")
    anchors = [n.x1 for n in anchor_line.nums]
    rows = []
    for ln in lines[i0 + 1:i1]:
        if ln.nums and any(re.search(r, ln.label, re.I) for r in row_res):
            rows.append(ParsedRow(label=ln.label, values=assign_columns(ln.nums, anchors), top=ln.top))
    if not rows:
        raise LookupError("no loans-to-customers rows found")
    return ParsedTable(rows=rows, total=None, total_label="(row totals)", anchors=anchors)


def column_sums(table: ParsedTable) -> list[float]:
    n = len(table.anchors)
    return [sum((r.values[j] or 0.0) for r in table.rows) for j in range(n)]
