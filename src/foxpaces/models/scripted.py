import json
import re
from dataclasses import dataclass, field

from foxpaces.models.completion import Completion

ELEMENT_LINE = re.compile(r'^\[(\d+)\] \S+ "(.*?)"', re.MULTILINE)


def find_element_index(observation_text: str, label: str) -> int:
    for match in ELEMENT_LINE.finditer(observation_text):
        if label in match.group(2):
            return int(match.group(1))
    return -1


def resolve_step(step: dict, observation_text: str) -> dict:
    if "label" not in step:
        return step
    resolved = {key: value for key, value in step.items() if key != "label"}
    return resolved | {"index": find_element_index(observation_text, step["label"])}


@dataclass
class ScriptedModel:
    solution: list[dict]
    position: int = field(default=0)

    def complete(self, messages: list[dict]) -> Completion:
        if self.position >= len(self.solution):
            return Completion(json.dumps({"action": "done", "answer": ""}), 0, 0)
        step = resolve_step(self.solution[self.position], messages[-1]["content"])
        self.position += 1
        return Completion(json.dumps(step), 0, 0)
