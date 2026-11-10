def normalize_text(text: str) -> str:
    return " ".join(text.split()).casefold()


def is_success(expected: dict[str, str], answer: str, final_url: str, final_text: str) -> bool:
    checks = {
        "answer": lambda value: normalize_text(answer) == normalize_text(value),
        "final_url": lambda value: final_url == value,
        "final_text": lambda value: normalize_text(value) in normalize_text(final_text),
    }
    unknown = expected.keys() - checks.keys()
    if unknown:
        raise ValueError(f"Unknown success checks: {sorted(unknown)}")
    return bool(expected) and all(checks[name](value) for name, value in expected.items())
