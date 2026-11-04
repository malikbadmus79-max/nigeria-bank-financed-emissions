"""Unit tests for the Phase 1b table-parsing repairs (no PDFs needed)."""

from bank_emissions.tables import (Line, Num, Word, assign_columns, is_date_header, merge_wrapped,
                                   split_glued_numbers, split_line)


def _texts(words):
    return [w.text for w in words]


def test_glued_numbers_are_split():
    out = split_glued_numbers([Word("83,530,8381,929,584,201", 400, 460, 10)])
    assert _texts(out) == ["83,530,838", "1,929,584,201"]


def test_spilled_digit_moves_to_next_number():
    out = split_glued_numbers([Word("577,3435", 420, 452, 10), Word("20,164", 520, 541, 10)])
    assert _texts(out) == ["577,343", "520,164"]


def test_valid_numbers_are_not_touched():
    words = [Word("1,234", 0, 20, 10), Word("56,789", 40, 60, 10)]
    assert _texts(split_glued_numbers(words)) == ["1,234", "56,789"]


def test_clipped_figure_keeps_its_column_with_no_value():
    ln = split_line([Word("ACTIVITIES", 0, 50, 0), Word("7,269,490", 100, 130, 0),
                     Word("7,178,47", 200, 230, 0), Word("7,178,487", 300, 330, 0)])
    assert ln.label == "ACTIVITIES"
    assert [n.value for n in ln.nums] == [7269490.0, None, 7178487.0]


def _line(label, *xs_vals, top=0.0):
    nums = [Num(str(v), float(v), x) for x, v in xs_vals]
    return Line(top=top, label=label, nums=nums, text=label)


def test_date_headers():
    assert is_date_header(_line("In thousands of Naira", (1, 2021), (2, 2020)))
    assert is_date_header(Line(0, "", [Num("31", 31, 1), Num("31", 31, 2)], "31 31 Dec Dec"))
    assert not is_date_header(_line("Agriculture", (1, 2021), (2, 5000)))


def test_wrapped_label_around_figures_is_a_row_not_a_total():
    lines = [Line(536.0, "Central Bank balance", [], "Central Bank balance"),
             _line("", (264, 863090), top=541.2),
             Line(546.4, "(restricted)", [], "(restricted)")]
    out = merge_wrapped(lines)
    assert len(out) == 1 and out[0].label == "Central Bank balance (restricted)"


def test_low_fragment_merges_into_row_above():
    out = merge_wrapped([_line("Finance and insurance", (347, 1048810), (410, 19227), top=287.3),
                         _line("", (466, 3865), top=290.1)])
    assert len(out) == 1 and [n.value for n in out[0].nums] == [1048810, 19227, 3865]


def test_full_line_assigned_in_order_despite_offset():
    nums = [Num("1", 1, 256), Num("2", 2, 322), Num("3", 3, 557)]
    assert assign_columns(nums, [256, 326, 577]) == [1, 2, 3]
