from pytest import approx

from foxpaces.report.aggregate import assign_trials, summarize_models, task_success_matrix
from foxpaces.report.heatmap import shade_index
from foxpaces.report.labels import label_runs
from foxpaces.report.page import render_report, render_site
from foxpaces.report.scatter_chart import rate_floor, spread_positions


def run(model: str, task: str, success: bool, cost: float = 0.001) -> dict:
    return {
        "model": model,
        "task_id": task,
        "success": success,
        "failure": None if success else "wrong_answer",
        "cost_usd": cost,
        "wall_time_s": 2.0,
        "steps": 3,
        "started_at": "2026-11-10T00:00:00+00:00",
        "run_id": f"{task}-{model}",
        "answer": "",
        "final_url": "{mock}/",
        "error": "",
    }


RUNS = [
    run("a", "t1", True),
    run("a", "t2", False),
    run("b", "t1", True),
    run("b", "t2", True),
    run("a", "t1", True),
    run("a", "t2", True),
]


def test_assign_trials_numbers_repeats_per_model_and_task() -> None:
    assert [r["trial"] for r in assign_trials(RUNS)] == [1, 1, 1, 1, 2, 2]


def test_summaries_rank_by_success_and_report_spread() -> None:
    best, second = summarize_models(RUNS)
    assert (best.model, best.success_rate) == ("b", 1.0)
    assert second.success_rate == approx(0.75)
    assert second.success_rate_std == approx(0.25)
    assert second.cost_per_success_usd == approx(0.004 / 3)
    assert second.failures == {"wrong_answer": 1}


def test_task_success_matrix() -> None:
    assert task_success_matrix(RUNS)["t2"] == {"a": 0.5, "b": 1.0}


def test_shade_index_covers_the_full_ramp() -> None:
    assert shade_index(0.0) == 0
    assert shade_index(1.0) == 5


def test_render_report_escapes_names() -> None:
    html = render_report([run("<x>", "t1", True)])
    assert "&lt;x&gt;" in html and "<x>" not in html


def test_render_site_has_a_trace_page_per_run() -> None:
    trace = [
        {
            "step": 1,
            "url": "u",
            "action": {"action": "go_back", "thought": "hm"},
            "outcome": "ok",
            "input_tokens": 1,
            "output_tokens": 1,
            "model_latency_s": 0.1,
        }
    ]
    pages = render_site(RUNS[:2], {"t1-a": trace})
    assert set(pages) == {"index.html", "runs.html", "traces/t1-a.html", "traces/t2-a.html"}
    assert "hm" in pages["traces/t1-a.html"]


def test_label_runs_marks_non_default_browsers() -> None:
    labelled = label_runs([run("m", "t", True) | {"browser": "chromium"}, run("m", "t", True)])
    assert [r["model"] for r in labelled] == ["m [chromium]", "m"]


def test_spread_positions_keeps_order_and_minimum_gap() -> None:
    assert spread_positions([10.0, 10.0, 50.0, 12.0], 16) == [10.0, 26.0, 58.0, 42.0]


def test_rate_floor_leaves_headroom_below_the_worst_model() -> None:
    assert rate_floor([0.85, 1.0]) == 0.8
    assert rate_floor([0.02]) == 0.0
