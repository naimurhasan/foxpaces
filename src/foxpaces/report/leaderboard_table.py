from html import escape

from foxpaces.report.aggregate import ModelSummary
from foxpaces.report.format import percent, usd


def format_failures(failures: dict[str, int]) -> str:
    return (
        "<br>".join(f"{escape(name)} ×{count}" for name, count in sorted(failures.items())) or "–"
    )


def leaderboard_table(summaries: list[ModelSummary]) -> str:
    rows = "".join(
        f'<tr><th scope="row">{rank}. {escape(s.model)}</th>'
        f"<td>{percent(s.success_rate)}</td>"
        f"<td>{'± ' + percent(s.success_rate_std) if s.trials > 1 else '–'}</td>"
        f"<td>{usd(s.cost_per_success_usd)}</td>"
        f"<td>{usd(s.total_cost_usd)}</td>"
        f"<td>{s.median_wall_time_s:.1f}s</td>"
        f"<td>{s.mean_steps:.1f}</td>"
        f"<td>{s.runs}</td>"
        f'<td class="failures">{format_failures(s.failures)}</td></tr>'
        for rank, s in enumerate(summaries, start=1)
    )
    return (
        '<table class="leaderboard"><thead><tr>'
        '<th scope="col">Model</th><th scope="col">Success</th><th scope="col">Spread</th>'
        '<th scope="col">Cost / success</th><th scope="col">Total cost</th>'
        '<th scope="col">Median time</th><th scope="col">Mean steps</th>'
        '<th scope="col">Runs</th><th scope="col">Failures</th>'
        f"</tr></thead><tbody>{rows}</tbody></table>"
    )
