from collections import Counter, defaultdict
from dataclasses import dataclass
from statistics import mean, median, pstdev


@dataclass(frozen=True)
class ModelSummary:
    model: str
    runs: int
    trials: int
    success_rate: float
    success_rate_std: float
    total_cost_usd: float
    mean_cost_usd: float
    cost_per_success_usd: float | None
    median_wall_time_s: float
    mean_steps: float
    failures: dict[str, int]


def assign_trials(runs: list[dict]) -> list[dict]:
    seen: Counter[tuple[str, str]] = Counter()
    numbered = []
    for run in runs:
        key = (run["model"], run["task_id"])
        seen[key] += 1
        numbered.append(run | {"trial": seen[key]})
    return numbered


def success_rate(runs: list[dict]) -> float:
    return mean(run["success"] for run in runs) if runs else 0.0


def summarize_model(model: str, runs: list[dict]) -> ModelSummary:
    by_trial: dict[int, list[dict]] = defaultdict(list)
    for run in runs:
        by_trial[run["trial"]].append(run)
    trial_rates = [success_rate(trial_runs) for trial_runs in by_trial.values()]
    successes = sum(run["success"] for run in runs)
    total_cost = sum(run["cost_usd"] for run in runs)
    return ModelSummary(
        model=model,
        runs=len(runs),
        trials=len(by_trial),
        success_rate=success_rate(runs),
        success_rate_std=pstdev(trial_rates),
        total_cost_usd=total_cost,
        mean_cost_usd=total_cost / len(runs),
        cost_per_success_usd=total_cost / successes if successes else None,
        median_wall_time_s=median(run["wall_time_s"] for run in runs),
        mean_steps=mean(run["steps"] for run in runs),
        failures=dict(Counter(run["failure"] for run in runs if run["failure"])),
    )


def summarize_models(runs: list[dict]) -> list[ModelSummary]:
    by_model: dict[str, list[dict]] = defaultdict(list)
    for run in assign_trials(runs):
        by_model[run["model"]].append(run)
    summaries = [summarize_model(model, model_runs) for model, model_runs in by_model.items()]
    return sorted(summaries, key=lambda s: (-s.success_rate, s.mean_cost_usd))


def task_success_matrix(runs: list[dict]) -> dict[str, dict[str, float]]:
    cells: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for run in runs:
        cells[run["task_id"]][run["model"]].append(run)
    return {
        task: {model: success_rate(model_runs) for model, model_runs in by_model.items()}
        for task, by_model in sorted(cells.items())
    }
