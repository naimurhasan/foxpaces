import json
import re
from html import escape

from foxpaces.report.format import usd
from foxpaces.report.shell import page_shell

MOCK_ORIGIN = re.compile(r"http://127\.0\.0\.1:\d+")


def step_card(step: dict) -> str:
    action = dict(step.get("action") or {})
    thought = action.pop("thought", "")
    action_text = json.dumps(action) if action else escape(step.get("response", ""))[:300]
    return (
        f'<li class="step"><div class="step-head"><strong>Step {step["step"]}</strong>'
        f"<span>{escape(MOCK_ORIGIN.sub('{mock}', step['url']))}</span></div>"
        + (f'<p class="thought">{escape(thought)}</p>' if thought else "")
        + f"<code>{escape(action_text)}</code>"
        f'<p class="note">→ {escape(step.get("outcome", ""))} · '
        f"{step['input_tokens']} in / {step['output_tokens']} out tokens · "
        f"{step['model_latency_s']:.1f}s</p></li>"
    )


def trace_page(run: dict, trace: list[dict]) -> str:
    verdict = "pass" if run["success"] else f"fail ({run['failure']})"
    error = f"<dt>Error</dt><dd>{escape(run['error'])}</dd>" if run.get("error") else ""
    body = (
        '<p class="lede"><a href="../runs.html">← All runs</a></p>'
        f"<h1>{escape(run['task_id'])}</h1>"
        f'<section><dl class="meta">'
        f"<dt>Model</dt><dd>{escape(run['model'])}</dd>"
        f"<dt>Result</dt><dd>{escape(verdict)}</dd>"
        f"<dt>Answer</dt><dd>{escape(run['answer']) or '–'}</dd>"
        f"<dt>Final URL</dt><dd>{escape(run['final_url'])}</dd>"
        f"<dt>Steps</dt><dd>{run['steps']}</dd>"
        f"<dt>Cost</dt><dd>{usd(run['cost_usd'])}</dd>"
        f"<dt>Time</dt><dd>{run['wall_time_s']:.1f}s</dd>{error}</dl></section>"
        f'<section><ol class="steps">{"".join(step_card(step) for step in trace)}</ol></section>'
    )
    return page_shell(f"Trace: {run['task_id']}", body)
