def percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def usd(value: float | None) -> str:
    if value is None:
        return "–"
    return f"${value:.4f}" if value < 0.01 else f"${value:.2f}"
