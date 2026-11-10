from html import escape
from math import floor

from foxpaces.report.aggregate import ModelSummary
from foxpaces.report.format import percent, usd

WIDTH = 680
HEIGHT = 360
MARGIN_LEFT = 56
MARGIN_RIGHT = 230
MARGIN_TOP = 16
MARGIN_BOTTOM = 44
TICK_STEP = 0.1
LABEL_GAP = 16


def nice_max(value: float) -> float:
    return value * 1.15 if value > 0 else 1.0


def rate_floor(rates: list[float]) -> float:
    return max(0.0, floor(round((min(rates) - 0.05) * 10, 6)) / 10)


def short_name(model: str) -> str:
    return model.split("/", 1)[-1]


def spread_positions(values: list[float], min_gap: float) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    placed = list(values)
    for previous, current in zip(order, order[1:], strict=False):
        placed[current] = max(placed[current], placed[previous] + min_gap)
    return placed


def cost_accuracy_scatter(summaries: list[ModelSummary]) -> str:
    plot_width = WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    plot_height = HEIGHT - MARGIN_TOP - MARGIN_BOTTOM
    max_cost = nice_max(max(s.mean_cost_usd for s in summaries))
    min_rate = rate_floor([s.success_rate for s in summaries])

    def x_of(cost: float) -> float:
        return MARGIN_LEFT + cost / max_cost * plot_width

    def y_of(rate: float) -> float:
        return MARGIN_TOP + (1 - rate) / (1 - min_rate) * plot_height

    tick_count = round((1 - min_rate) / TICK_STEP) + 1
    ticks = [min_rate + TICK_STEP * i for i in range(tick_count)]
    grid = "".join(
        f'<line class="grid" x1="{MARGIN_LEFT}" x2="{MARGIN_LEFT + plot_width}" '
        f'y1="{y_of(tick):.1f}" y2="{y_of(tick):.1f}"/>'
        f'<text class="tick" x="{MARGIN_LEFT - 8}" y="{y_of(tick) + 4:.1f}" '
        f'text-anchor="end">{percent(tick)}</text>'
        for tick in ticks
    )
    x_ticks = "".join(
        f'<text class="tick" x="{x_of(max_cost * f):.1f}" y="{HEIGHT - 24}" '
        f'text-anchor="middle">{usd(max_cost * f)}</text>'
        for f in (0, 0.5, 1)
    )
    axes = (
        f'<line class="axis" x1="{MARGIN_LEFT}" x2="{MARGIN_LEFT + plot_width}" '
        f'y1="{y_of(min_rate):.1f}" y2="{y_of(min_rate):.1f}"/>'
        f'<text class="tick" x="{MARGIN_LEFT + plot_width / 2}" y="{HEIGHT - 4}" '
        f'text-anchor="middle">Mean cost per run (USD)</text>'
    )
    label_x = MARGIN_LEFT + plot_width + 24
    label_ys = spread_positions([y_of(s.success_rate) for s in summaries], LABEL_GAP)
    points = "".join(
        f"<g><title>{escape(s.model)}: {percent(s.success_rate)} success, "
        f"{usd(s.mean_cost_usd)} per run</title>"
        f'<circle cx="{x_of(s.mean_cost_usd):.1f}" cy="{y_of(s.success_rate):.1f}" r="14" '
        f'fill="transparent"/>'
        f'<line class="grid" x1="{x_of(s.mean_cost_usd) + 6:.1f}" '
        f'y1="{y_of(s.success_rate):.1f}" x2="{label_x - 4}" y2="{label_y:.1f}"/>'
        f'<circle class="dot" cx="{x_of(s.mean_cost_usd):.1f}" '
        f'cy="{y_of(s.success_rate):.1f}" r="5"/>'
        f'<text class="label" x="{label_x}" y="{label_y + 4:.1f}">'
        f"{escape(short_name(s.model))}</text></g>"
        for s, label_y in zip(summaries, label_ys, strict=True)
    )
    return (
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        f'aria-label="Success rate versus mean cost per run">{grid}{axes}{x_ticks}{points}</svg>'
    )
