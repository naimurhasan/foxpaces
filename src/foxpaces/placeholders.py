def resolve_mock_url(text: str, mock_base_url: str) -> str:
    return text.replace("{mock}", mock_base_url)
