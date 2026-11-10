from foxpaces.observation import Observation, format_observation
from foxpaces.task import Task

SYSTEM_PROMPT = """You are a web browsing agent controlling a real browser.
Each turn you see the task, your previous steps, and the current page.
Reply with exactly one JSON object and nothing else. Available actions:
{"action": "click", "index": 3}
{"action": "type", "index": 2, "text": "hello", "submit": false}
{"action": "select", "index": 4, "option": "Visible option text"}
{"action": "scroll", "direction": "down"}
{"action": "navigate", "url": "https://example.com"}
{"action": "go_back"}
{"action": "done", "answer": "final answer"}
Indexes refer to the current interactive elements list, which only covers the area
around the viewport: scroll to reach elements further down the page.
Add a short "thought" field recording facts you found (such as prices or names);
previous steps, including thoughts, are shown back to you, so you can compare across pages.
Use done as soon as the task is complete.
Give the answer exactly in the format the task asks for."""


def format_history(history: list[str]) -> str:
    return "\n".join(history) or "none"


def build_messages(task: Task, history: list[str], observation: Observation) -> list[dict]:
    user = (
        f"Task: {task.instruction}\n\n"
        f"Previous steps:\n{format_history(history)}\n\n"
        f"Current page:\n{format_observation(observation)}"
    )
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]
