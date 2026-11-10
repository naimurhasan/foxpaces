import json
from dataclasses import asdict
from pathlib import Path

from foxpaces.runner import RunResult

RESULTS_DIR = Path("results")


def save_run(result: RunResult, trace: list[dict], results_dir: Path = RESULTS_DIR) -> None:
    traces_dir = results_dir / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)
    with (results_dir / "runs.jsonl").open("a") as runs:
        runs.write(json.dumps(asdict(result)) + "\n")
    (traces_dir / f"{result.run_id}.jsonl").write_text(
        "".join(json.dumps(step) + "\n" for step in trace)
    )


def load_runs(results_dir: Path = RESULTS_DIR) -> list[dict]:
    path = results_dir / "runs.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load_traces(results_dir: Path = RESULTS_DIR) -> dict[str, list[dict]]:
    return {
        path.stem: [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        for path in (results_dir / "traces").glob("*.jsonl")
    }
