from html import escape

from foxpaces.report.aggregate import assign_trials
from foxpaces.report.format import usd
from foxpaces.report.shell import page_shell


def runs_page(runs: list[dict]) -> str:
    ordered = sorted(assign_trials(runs), key=lambda r: (r["model"], r["task_id"], r["trial"]))
    rows = "".join(
        f'<tr><th scope="row"><a href="traces/{escape(r["run_id"])}.html">'
        f"{escape(r['task_id'])}</a></th>"
        f"<td>{escape(r['model'])}</td><td>{r['trial']}</td>"
        f"<td>{'pass' if r['success'] else 'fail'}</td>"
        f"<td>{escape(r['failure'] or '–')}</td><td>{r['steps']}</td>"
        f"<td>{usd(r['cost_usd'])}</td><td>{r['wall_time_s']:.1f}s</td></tr>"
        for r in ordered
    )
    body = (
        '<p class="lede"><a href="index.html">← Leaderboard</a></p>'
        "<h1>All runs</h1><section>"
        '<table><thead><tr><th scope="col">Task</th><th scope="col">Model</th>'
        '<th scope="col">Trial</th><th scope="col">Result</th><th scope="col">Failure</th>'
        '<th scope="col">Steps</th><th scope="col">Cost</th><th scope="col">Time</th>'
        f"</tr></thead><tbody>{rows}</tbody></table></section>"
    )
    return page_shell("FoxPaces Runs", body)
