from foxpaces.report.aggregate import summarize_models, task_success_matrix
from foxpaces.report.bar_chart import success_bar_chart
from foxpaces.report.heatmap import task_heatmap
from foxpaces.report.leaderboard_table import leaderboard_table
from foxpaces.report.runs_page import runs_page
from foxpaces.report.scatter_chart import cost_accuracy_scatter
from foxpaces.report.shell import page_shell
from foxpaces.report.trace_page import trace_page


def run_dates(runs: list[dict]) -> str:
    dates = sorted(run["started_at"][:10] for run in runs)
    return dates[0] if dates[0] == dates[-1] else f"{dates[0]} to {dates[-1]}"


def render_report(runs: list[dict]) -> str:
    summaries = summarize_models(runs)
    models = [summary.model for summary in summaries]
    tasks = {run["task_id"] for run in runs}
    total_cost = sum(run["cost_usd"] for run in runs)
    body = f"""<h1>FoxPaces Leaderboard</h1>
<p class="lede">LLM browser agents driving a real Camoufox browser through deterministic mock web
tasks. Success is checked programmatically; cost comes from per-token prices.</p>
<section>
<dl class="meta">
<dt>Runs</dt><dd>{len(runs)} across {len(models)} models and {len(tasks)} tasks ·
<a href="runs.html">browse every run and its trace</a></dd>
<dt>Dates</dt><dd>{run_dates(runs)}</dd>
<dt>Total spend</dt><dd>${total_cost:.4f}</dd>
</dl>
</section>
<section>
<h2>Leaderboard</h2>
{leaderboard_table(summaries)}
<p class="note">Spread is the standard deviation of the success rate across repeated trials.
Cost / success is total cost divided by successful runs.</p>
</section>
<section>
<h2>Success rate by model</h2>
{success_bar_chart(summaries)}
</section>
<section>
<h2>Cost vs. accuracy</h2>
{cost_accuracy_scatter(summaries)}
<p class="note">Up and to the left is better.</p>
</section>
<section>
<h2>Success rate per task</h2>
{task_heatmap(task_success_matrix(runs), models)}
</section>"""
    return page_shell("FoxPaces Leaderboard", body)


def render_site(runs: list[dict], traces: dict[str, list[dict]]) -> dict[str, str]:
    pages = {"index.html": render_report(runs), "runs.html": runs_page(runs)}
    for run in runs:
        pages[f"traces/{run['run_id']}.html"] = trace_page(run, traces.get(run["run_id"], []))
    return pages
