from foxpaces.agent_loop import describe_step
from foxpaces.observation import Observation

OBSERVATION = Observation(
    url="http://x/shop",
    title="Shop",
    elements=[{"index": 0, "label": "Blue Mug"}],
    text="",
)


def test_describe_step_names_the_target_element_and_keeps_thought() -> None:
    action = {"action": "click", "index": 0, "thought": "mug is $12.50"}
    line = describe_step(3, OBSERVATION, action, "ok")
    assert line.startswith("3. at http://x/shop:")
    assert '"thought": "mug is $12.50"' in line
    assert line.endswith('on "Blue Mug" -> ok')


def test_describe_step_without_index() -> None:
    assert describe_step(1, OBSERVATION, {"action": "go_back"}, "ok").endswith(
        '{"action": "go_back"} -> ok'
    )
