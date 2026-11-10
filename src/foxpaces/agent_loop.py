import json
from dataclasses import dataclass, field
from time import perf_counter

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

from foxpaces.actions import InvalidAction, parse_action
from foxpaces.config import Limits
from foxpaces.execute import execute_action
from foxpaces.models.completion import Model, ModelError
from foxpaces.observation import Observation, take_observation
from foxpaces.prompt import build_messages
from foxpaces.task import Task

MAX_CONSECUTIVE_INVALID = 3


@dataclass
class AgentOutcome:
    answer: str = ""
    failure: str | None = None
    error: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    trace: list[dict] = field(default_factory=list)


def first_line(error: Exception) -> str:
    return str(error).strip().splitlines()[0][:300] if str(error).strip() else type(error).__name__


def describe_step(step: int, observation: Observation, action: dict, outcome: str) -> str:
    target = observation.elements[action["index"]]["label"] if "index" in action else ""
    on = f' on "{target}"' if target else ""
    return f"{step}. at {observation.url}: {json.dumps(action)}{on} -> {outcome}"


def stop_reason(outcome: AgentOutcome, started: float, limits: Limits) -> str | None:
    if perf_counter() - started > limits.timeout_s:
        return "timeout"
    if outcome.input_tokens + outcome.output_tokens > limits.max_tokens_per_run:
        return "token_limit"
    return None


def run_agent(page: Page, task: Task, model: Model, limits: Limits) -> AgentOutcome:
    outcome = AgentOutcome()
    history: list[str] = []
    consecutive_invalid = 0
    started = perf_counter()
    for step in range(1, task.max_steps + 1):
        outcome.failure = stop_reason(outcome, started, limits)
        if outcome.failure:
            return outcome
        try:
            observation = take_observation(page)
        except PlaywrightError as error:
            outcome.failure, outcome.error = "browser_error", first_line(error)
            return outcome
        call_started = perf_counter()
        try:
            completion = model.complete(build_messages(task, history, observation))
        except ModelError as error:
            outcome.failure, outcome.error = "model_error", first_line(error)
            return outcome
        outcome.input_tokens += completion.input_tokens
        outcome.output_tokens += completion.output_tokens
        record = {
            "step": step,
            "url": observation.url,
            "title": observation.title,
            "element_count": len(observation.elements),
            "response": completion.text,
            "input_tokens": completion.input_tokens,
            "output_tokens": completion.output_tokens,
            "model_latency_s": round(perf_counter() - call_started, 3),
        }
        outcome.trace.append(record)
        try:
            action = parse_action(completion.text, len(observation.elements))
        except InvalidAction as error:
            record["outcome"] = f"invalid: {error}"
            history.append(f"{step}. invalid response -> {error}")
            consecutive_invalid += 1
            if consecutive_invalid >= MAX_CONSECUTIVE_INVALID:
                outcome.failure, outcome.error = "invalid_action", str(error)
                return outcome
            continue
        consecutive_invalid = 0
        record["action"] = action
        if action["action"] == "done":
            record["outcome"] = "done"
            outcome.answer = action["answer"]
            return outcome
        try:
            execute_action(page, action)
            record["outcome"] = "ok"
        except PlaywrightError as error:
            record["outcome"] = f"error: {first_line(error)}"
        history.append(describe_step(step, observation, action, record["outcome"]))
    outcome.failure = "step_limit"
    return outcome
