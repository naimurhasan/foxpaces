import tomllib
from dataclasses import dataclass, field
from glob import glob
from pathlib import Path


@dataclass(frozen=True)
class Task:
    id: str
    start_url: str
    instruction: str
    max_steps: int
    success: dict[str, str]
    solution: list[dict] = field(default_factory=list)


def load_task(path: Path) -> Task:
    data = tomllib.loads(path.read_text())
    return Task(
        id=data["id"],
        start_url=data["start_url"],
        instruction=data["instruction"],
        max_steps=data["max_steps"],
        success=data["success"],
        solution=data.get("solution", []),
    )


def load_tasks(pattern: str) -> list[Task]:
    return [load_task(Path(path)) for path in sorted(glob(pattern))]
