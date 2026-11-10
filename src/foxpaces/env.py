import os
from pathlib import Path


def parse_env(text: str) -> dict[str, str]:
    pairs = (line.split("=", 1) for line in text.splitlines() if "=" in line)
    return {
        key.strip(): value.strip().strip("\"'")
        for key, value in pairs
        if key.strip() and not key.strip().startswith("#")
    }


def load_env(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for key, value in parse_env(path.read_text()).items():
        os.environ.setdefault(key, value)
