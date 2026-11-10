import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foxpaces.browser import BROWSERS, CAMOUFOX, open_browser
from foxpaces.config import load_config
from foxpaces.env import load_env
from foxpaces.mock_server import serve_mock_sites
from foxpaces.models.factory import SCRIPTED
from foxpaces.report.labels import label_runs
from foxpaces.report.page import render_site
from foxpaces.results_store import RESULTS_DIR, load_runs, load_traces, save_run
from foxpaces.runner import run_task
from foxpaces.task import load_tasks


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="foxpaces")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Run tasks with one or more models")
    run.add_argument("--model", action="append", dest="models", default=None)
    run.add_argument("--tasks", nargs="+", default=["tasks/mock/*.toml"])
    run.add_argument("--repeats", type=int, default=1)
    run.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    run.add_argument("--browser", choices=BROWSERS, default=CAMOUFOX)
    run.add_argument("--headed", action="store_true")
    report = commands.add_parser("report", help="Build the static HTML leaderboard")
    report.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    report.add_argument("--exclude-model", action="append", default=[SCRIPTED])
    report.add_argument("--out-dir", type=Path, default=Path("site"))
    return parser.parse_args(argv)


def run_benchmark(args: argparse.Namespace) -> int:
    config = load_config()
    models = args.models or [SCRIPTED]
    unknown = [model for model in models if model not in config.pricing]
    if unknown:
        raise SystemExit(f"No pricing in foxpaces.toml for: {', '.join(unknown)}")
    tasks = [task for pattern in args.tasks for task in load_tasks(pattern)]
    if not tasks:
        raise SystemExit(f"No tasks match {' '.join(args.tasks)}")
    spent = 0.0
    all_passed = True
    with (
        serve_mock_sites() as mock_base_url,
        open_browser(args.browser, headless=not args.headed) as browser,
    ):
        for _ in range(args.repeats):
            for model in models:
                for task in tasks:
                    if spent >= config.limits.budget_usd:
                        print(f"Budget of ${config.limits.budget_usd} reached, stopping.")
                        return 1
                    result, trace = run_task(
                        browser, args.browser, task, model, config, mock_base_url
                    )
                    save_run(result, trace, args.results_dir)
                    spent += result.cost_usd
                    all_passed = all_passed and result.success
                    print(json.dumps(asdict(result)))
    print(f"Total cost: ${spent:.4f}")
    return 0 if all_passed else 1


def build_report(args: argparse.Namespace) -> int:
    runs = label_runs(
        [run for run in load_runs(args.results_dir) if run["model"] not in args.exclude_model]
    )
    if not runs:
        raise SystemExit(f"No runs to report in {args.results_dir}")
    for relative_path, html in render_site(runs, load_traces(args.results_dir)).items():
        path = args.out_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html)
    print(f"Wrote {args.out_dir / 'index.html'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    load_env()
    args = parse_args(argv)
    return run_benchmark(args) if args.command == "run" else build_report(args)
