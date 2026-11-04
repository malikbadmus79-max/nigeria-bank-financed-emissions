"""Unit tests for Phase 1b validation helpers (no PDFs needed)."""

from bank_emissions.phase1b_build import external_flag, reread_cell
from bank_emissions.phase1b_config import BASIS_DECISIONS, EXTERNAL_FLAGS, UNIT_DECISIONS
from bank_emissions.phase1b_ocr import join_digit_groups
from bank_emissions.phase1b_validate import find_matches
from bank_emissions.tables import Word


def test_ocr_digit_groups_rejoined():
    words = [Word("Education", 10, 60, 100), Word("1999", 400, 420, 100), Word("029", 422, 437, 100),
             Word("2", 500, 505, 100), Word("086", 507, 522, 100), Word("083", 524, 539, 100)]
    assert [w.text for w in join_digit_groups(words)] == ["Education", "1,999,029", "2,086,083"]


def test_ocr_columns_not_joined():
    words = [Word("15", 400, 410, 100), Word("848", 412, 427, 100), Word("25", 480, 490, 100),
             Word("846", 492, 507, 100)]
    assert [w.text for w in join_digit_groups(words)] == ["15,848", "25,846"]


def test_find_matches_comma_and_space_separated():
    texts = ["Gross loans 1,238,195 946,259", "Loans (gross) 2 475 470 182 2 485 078 216", "sector page"]
    assert [m["page"] for m in find_matches(texts, 1238194, 1.0, skip_page=3)] == [1]
    assert [m["page"] for m in find_matches(texts, 2475470182, 1.0, skip_page=3)] == [2]


def test_reread_cell_label_then_value():
    text = "Agriculture 94,115\nBusiness services 48,802\nCommunication 252,804"
    assert reread_cell(text, "Business services", [48802.0], derived=False)[0] == "pass"
    assert reread_cell(text, "Business services", [48803.0], derived=False)[0] == "fail"
    assert reread_cell(text, "Agriculture", [0.0], derived=False)[0] == "pass (zero)"


def test_reread_cell_components():
    text = "- Overdrafts 138,178 66,039\n- Term loans 79,426 422,886"
    assert reread_cell(text, "Agriculture", [138178.0, 79426.0], derived=True)[0] == "pass"
    assert reread_cell(text, "Agriculture", [138178.0, 1.5e6], derived=True)[0] == "fail"


def test_flags_by_basis_take_precedence():
    assert external_flag("WEMABANK", 2022, "group", "carrying")
    assert external_flag("WEMABANK", 2022, "group", "gross") == ""
    assert external_flag("STANBIC", 2025, "group", "carrying") == EXTERNAL_FLAGS[("STANBIC", 2025, "group")]


def test_decisions_cover_the_open_bases():
    for bank in ("STERLINGNG", "JAIZBANK"):
        assert {d[1] for (b, _), d in BASIS_DECISIONS.items() if b == bank} == {"gross"}
    assert all(m == 1e3 for (b, _), (m, _, _) in UNIT_DECISIONS.items() if b == "WEMABANK")
