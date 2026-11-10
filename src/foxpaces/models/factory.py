from foxpaces.config import Limits
from foxpaces.models.completion import Model
from foxpaces.models.openrouter import OpenRouterModel
from foxpaces.models.scripted import ScriptedModel
from foxpaces.task import Task

SCRIPTED = "scripted"


def make_model(name: str, task: Task, limits: Limits) -> Model:
    if name == SCRIPTED:
        return ScriptedModel(task.solution)
    return OpenRouterModel(name, limits.max_output_tokens)
