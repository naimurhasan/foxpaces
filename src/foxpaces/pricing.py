from foxpaces.config import Price


def cost_usd(price: Price, input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens * price.input_usd_per_mtok + output_tokens * price.output_usd_per_mtok
    ) / 1_000_000
