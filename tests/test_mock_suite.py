import json
from pathlib import Path

import pytest

from foxpaces.cli import main


@pytest.mark.browser
def test_scripted_model_passes_mock_suite(tmp_path: Path) -> None:
    assert main(["run", "--model", "scripted", "--results-dir", str(tmp_path)]) == 0
    runs = [json.loads(line) for line in (tmp_path / "runs.jsonl").read_text().splitlines()]
    assert len(runs) >= 10
    assert all(run["success"] and run["cost_usd"] == 0 for run in runs)
    assert len(list((tmp_path / "traces").glob("*.jsonl"))) == len(runs)
