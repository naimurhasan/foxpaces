from foxpaces.observation import Observation, format_observation


def element(index: int, tag: str, label: str, **extra) -> dict:
    return {
        "index": index,
        "tag": tag,
        "type": "",
        "label": label,
        "value": "",
        "checked": None,
        "options": [],
    } | extra


def test_formats_elements_with_state() -> None:
    observation = Observation(
        url="http://x/",
        title="Shop",
        elements=[
            element(0, "input", "Search", type="search", value="mug"),
            element(1, "input", "Agree", type="checkbox", checked=False),
            element(2, "select", "Shipping", options=["Standard", "Express"]),
        ],
        text="Welcome",
    )
    text = format_observation(observation)
    assert '[0] input[search] "Search" value="mug"' in text
    assert '[1] input[checkbox] "Agree" checked=false' in text
    assert "[2] select \"Shipping\" options=['Standard', 'Express']" in text
    assert text.endswith("Page text:\nWelcome")
