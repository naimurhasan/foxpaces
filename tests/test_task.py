from foxpaces.actions import ACTION_FIELDS
from foxpaces.task import load_tasks


def test_every_mock_task_loads_with_a_scripted_solution() -> None:
    tasks = load_tasks("tasks/mock/*.toml")
    assert len(tasks) >= 10
    assert len({task.id for task in tasks}) == len(tasks)
    for task in tasks:
        assert task.max_steps > 0
        assert task.success
        assert task.solution[-1]["action"] == "done"
        assert all(step["action"] in ACTION_FIELDS for step in task.solution)
