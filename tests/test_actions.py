import pytest

from foxpaces.actions import InvalidAction, parse_action


def test_parses_json_wrapped_in_prose_and_fences() -> None:
    text = 'Sure:\n```json\n{"action": "click", "index": 2, "thought": "open"}\n```'
    assert parse_action(text, 5) == {"action": "click", "index": 2, "thought": "open"}


def test_takes_first_of_several_json_objects() -> None:
    text = '{"action": "go_back"}\n{"action": "done", "answer": "x"}'
    assert parse_action(text, 0) == {"action": "go_back"}


def test_done_needs_answer() -> None:
    assert parse_action('{"action": "done", "answer": "$1"}', 0)["answer"] == "$1"
    with pytest.raises(InvalidAction):
        parse_action('{"action": "done"}', 0)


@pytest.mark.parametrize(
    "text",
    [
        "no json here",
        "{not json}",
        '{"action": "fly"}',
        '{"action": "click", "index": 9}',
        '{"action": "click", "index": "1"}',
        '{"action": "click", "index": true}',
        '{"action": "scroll", "direction": "left"}',
        '["click"]',
    ],
)
def test_rejects_invalid_actions(text: str) -> None:
    with pytest.raises(InvalidAction):
        parse_action(text, 3)
