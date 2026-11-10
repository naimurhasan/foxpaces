from html import escape

from foxpaces.report.format import percent
from foxpaces.report.scatter_chart import short_name

SEQUENTIAL_BLUE = ("#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95")
DARK_TEXT_STEPS = 3


def shade_index(rate: float) -> int:
    return min(int(rate * len(SEQUENTIAL_BLUE)), len(SEQUENTIAL_BLUE) - 1)


def task_heatmap(matrix: dict[str, dict[str, float]], models: list[str]) -> str:
    header = "".join(
        f'<th scope="col" title="{escape(model)}">{escape(short_name(model))}</th>'
        for model in models
    )
    rows = []
    for task, by_model in matrix.items():
        cells = []
        for model in models:
            if model not in by_model:
                cells.append('<td class="cell empty">–</td>')
                continue
            rate = by_model[model]
            step = shade_index(rate)
            ink = "#0b0b0b" if step < DARK_TEXT_STEPS else "#ffffff"
            cells.append(
                f'<td class="cell" style="background:{SEQUENTIAL_BLUE[step]};color:{ink}" '
                f'title="{escape(task)} · {escape(model)}: {percent(rate)}">{percent(rate)}</td>'
            )
        rows.append(f'<tr><th scope="row">{escape(task)}</th>{"".join(cells)}</tr>')
    return (
        f'<table class="heatmap"><thead><tr><th scope="col">Task</th>{header}</tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table>"
    )
