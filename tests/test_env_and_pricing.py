from foxpaces.config import Price, load_config
from foxpaces.env import parse_env
from foxpaces.models.openrouter import parse_response
from foxpaces.pricing import cost_usd


def test_parse_env_skips_comments_and_strips_quotes() -> None:
    text = '# comment\nOPENROUTER_API_KEY="sk-1"\nEMPTY=\nnot a pair\n'
    assert parse_env(text) == {"OPENROUTER_API_KEY": "sk-1", "EMPTY": ""}


def test_cost_uses_per_million_token_prices() -> None:
    assert cost_usd(Price(0.10, 0.50), 40, 17) == 1.25e-05


def test_every_configured_price_is_non_negative() -> None:
    config = load_config()
    assert config.limits.budget_usd > 0
    assert all(
        p.input_usd_per_mtok >= 0 and p.output_usd_per_mtok >= 0 for p in config.pricing.values()
    )


def test_parse_openrouter_response() -> None:
    payload = {
        "choices": [{"message": {"content": None}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 3},
    }
    completion = parse_response(payload)
    assert (completion.text, completion.input_tokens, completion.output_tokens) == ("", 10, 3)
