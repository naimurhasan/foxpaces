from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

from playwright.sync_api import Browser
from playwright.sync_api import Error as PlaywrightError

from foxpaces.agent_loop import AgentOutcome, first_line, run_agent
from foxpaces.config import Config
from foxpaces.models.factory import make_model
from foxpaces.placeholders import resolve_mock_url
from foxpaces.pricing import cost_usd
from foxpaces.success import is_success
from foxpaces.task import Task


@dataclass(frozen=True)
class RunResult:
    run_id: str
    started_at: str
    model: str
    browser: str
    task_id: str
    success: bool
    failure: str | None
    error: str
    answer: str
    final_url: str
    steps: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    wall_time_s: float


def make_run_id(model: str, task_id: str) -> str:
    return f"{task_id}--{model.replace('/', '_')}--{uuid4().hex[:8]}"


def final_failure(outcome: AgentOutcome, success: bool) -> str | None:
    if outcome.failure:
        return outcome.failure
    return None if success else "wrong_answer"


def run_task(
    browser: Browser,
    browser_name: str,
    task: Task,
    model_name: str,
    config: Config,
    mock_base_url: str,
) -> tuple[RunResult, list[dict]]:
    started_at = datetime.now(UTC).isoformat(timespec="seconds")
    started = perf_counter()
    context = browser.new_context()
    context.set_default_timeout(config.limits.action_timeout_ms)
    context.set_default_navigation_timeout(config.limits.navigation_timeout_ms)
    page = context.new_page()
    try:
        page.goto(resolve_mock_url(task.start_url, mock_base_url))
        model = make_model(model_name, task, config.limits)
        outcome = run_agent(page, task, model, config.limits)
        final_text = page.inner_text("body")
    except PlaywrightError as error:
        outcome = AgentOutcome(failure="browser_error", error=first_line(error))
        final_text = ""
    final_url = page.url
    context.close()
    expected = {
        name: resolve_mock_url(value, mock_base_url) for name, value in task.success.items()
    }
    success = not outcome.failure and is_success(expected, outcome.answer, final_url, final_text)
    result = RunResult(
        run_id=make_run_id(model_name, task.id),
        started_at=started_at,
        model=model_name,
        browser=browser_name,
        task_id=task.id,
        success=success,
        failure=final_failure(outcome, success),
        error=outcome.error,
        answer=outcome.answer,
        final_url=final_url.replace(mock_base_url, "{mock}"),
        steps=len(outcome.trace),
        input_tokens=outcome.input_tokens,
        output_tokens=outcome.output_tokens,
        cost_usd=round(
            cost_usd(config.pricing[model_name], outcome.input_tokens, outcome.output_tokens), 6
        ),
        wall_time_s=round(perf_counter() - started, 3),
    )
    return result, outcome.trace
