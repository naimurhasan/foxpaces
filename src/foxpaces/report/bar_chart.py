from html import escape

from foxpaces.report.aggregate import ModelSummary
from foxpaces.report.format import percent

ROW_HEIGHT = 36
BAR_HEIGHT = 20
LABEL_WIDTH = 290
PLOT_WIDTH = 360
VALUE_WIDTH = 90


def success_bar_chart(summaries: list[ModelSummary]) -> str:
    width = LABEL_WIDTH + PLOT_WIDTH + VALUE_WIDTH
    height = ROW_HEIGHT * len(summaries) + 8
    rows = []
    for row, summary in enumerate(summaries):
        y = row * ROW_HEIGHT + 8
        bar_width = max(summary.success_rate * PLOT_WIDTH, 2)
        spread = f" ± {percent(summary.success_rate_std)}" if summary.trials > 1 else ""
        tooltip = (
            f"{summary.model}: {percent(summary.success_rate)}{spread} over {summary.runs} runs"
        )
        rows.append(
            f"<g><title>{escape(tooltip)}</title>"
            f'<rect x="0" y="{y - 6}" width="{width}" height="{ROW_HEIGHT}" fill="transparent"/>'
            f'<text class="label" x="{LABEL_WIDTH - 12}" y="{y + 14}" text-anchor="end">'
            f"{escape(summary.model)}</text>"
            f'<rect class="bar" x="{LABEL_WIDTH}" y="{y}" width="{bar_width:.1f}" '
            f'height="{BAR_HEIGHT}" rx="4"/>'
            f'<text class="value" x="{LABEL_WIDTH + bar_width + 8:.1f}" y="{y + 14}">'
            f"{percent(summary.success_rate)}{spread}</text></g>"
        )
    baseline = f'<line class="axis" x1="{LABEL_WIDTH}" y1="0" x2="{LABEL_WIDTH}" y2="{height}"/>'
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Success rate by model">{baseline}{"".join(rows)}</svg>'
    )
