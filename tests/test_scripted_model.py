import json

from foxpaces.models.scripted import ScriptedModel, find_element_index

OBSERVATION = 'Interactive elements:\n[0] a "Back to shop"\n[1] a "Cart"\n[2] button "Add to cart"'


def test_find_element_index_matches_label_substring() -> None:
    assert find_element_index(OBSERVATION, "Cart") == 1
    assert find_element_index(OBSERVATION, "Add") == 2
    assert find_element_index(OBSERVATION, "Missing") == -1


def test_scripted_model_resolves_labels_then_finishes() -> None:
    model = ScriptedModel([{"action": "click", "label": "Cart"}])
    messages = [{"role": "user", "content": OBSERVATION}]
    assert json.loads(model.complete(messages).text) == {"action": "click", "index": 1}
    assert json.loads(model.complete(messages).text)["action"] == "done"
