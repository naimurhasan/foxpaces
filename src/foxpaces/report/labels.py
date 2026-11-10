from foxpaces.browser import CAMOUFOX


def run_label(run: dict) -> str:
    browser = run.get("browser", CAMOUFOX)
    return run["model"] if browser == CAMOUFOX else f"{run['model']} [{browser}]"


def label_runs(runs: list[dict]) -> list[dict]:
    return [run | {"model": run_label(run)} for run in runs]
