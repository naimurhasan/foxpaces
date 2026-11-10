import json

ACTION_FIELDS: dict[str, dict[str, type]] = {
    "click": {"index": int},
    "type": {"index": int, "text": str},
    "select": {"index": int, "option": str},
    "scroll": {"direction": str},
    "navigate": {"url": str},
    "go_back": {},
    "done": {"answer": str},
}


class InvalidAction(ValueError):
    pass


def extract_json_object(text: str) -> dict:
    start = text.find("{")
    if start == -1:
        raise InvalidAction("Response contains no JSON object")
    try:
        value, _ = json.JSONDecoder().raw_decode(text, start)
    except json.JSONDecodeError as error:
        raise InvalidAction(f"Invalid JSON: {error.msg}") from error
    if not isinstance(value, dict):
        raise InvalidAction("Response JSON is not an object")
    return value


def parse_action(text: str, element_count: int) -> dict:
    action = extract_json_object(text)
    name = action.get("action")
    if name not in ACTION_FIELDS:
        raise InvalidAction(f"Unknown action: {name!r}")
    for field, kind in ACTION_FIELDS[name].items():
        if not isinstance(action.get(field), kind) or isinstance(action.get(field), bool):
            raise InvalidAction(f"{name} needs {field} of type {kind.__name__}")
    if "index" in ACTION_FIELDS[name] and not 0 <= action["index"] < element_count:
        raise InvalidAction(f"No element with index {action['index']}")
    if name == "scroll" and action["direction"] not in ("up", "down"):
        raise InvalidAction("scroll direction must be up or down")
    return action
