import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Limits:
    budget_usd: float
    max_tokens_per_run: int
    timeout_s: float
    action_timeout_ms: int
    navigation_timeout_ms: int
    max_output_tokens: int


@dataclass(frozen=True)
class Price:
    input_usd_per_mtok: float
    output_usd_per_mtok: float


@dataclass(frozen=True)
class Config:
    limits: Limits
    pricing: dict[str, Price]


def load_config(path: Path = Path("foxpaces.toml")) -> Config:
    data = tomllib.loads(path.read_text())
    return Config(
        limits=Limits(**data["limits"]),
        pricing={model: Price(**price) for model, price in data["pricing"].items()},
    )
