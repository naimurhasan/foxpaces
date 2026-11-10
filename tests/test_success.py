import pytest

from foxpaces.success import is_success


def test_answer_match_ignores_case_and_whitespace() -> None:
    assert is_success({"answer": "$12.50"}, "  $12.50 \n", "http://x", "")


def test_wrong_answer_fails() -> None:
    assert not is_success({"answer": "$12.50"}, "$9.75", "http://x", "")


def test_all_checks_must_pass() -> None:
    expected = {"answer": "$12.50", "final_url": "http://x/a"}
    assert is_success(expected, "$12.50", "http://x/a", "")
    assert not is_success(expected, "$12.50", "http://x/b", "")


def test_final_text_is_a_normalized_substring() -> None:
    expected = {"final_text": "Order confirmed for Ada"}
    assert is_success(expected, "", "http://x", "Thanks!\nOrder   confirmed for ada.")
    assert not is_success(expected, "", "http://x", "Order failed")


def test_empty_checks_never_succeed() -> None:
    assert not is_success({}, "anything", "http://x", "")


def test_unknown_check_is_rejected() -> None:
    with pytest.raises(ValueError):
        is_success({"title": "x"}, "", "", "")
