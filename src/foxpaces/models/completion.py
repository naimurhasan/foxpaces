from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Completion:
    text: str
    input_tokens: int
    output_tokens: int


class ModelError(RuntimeError):
    pass


class Model(Protocol):
    def complete(self, messages: list[dict]) -> Completion: ...
