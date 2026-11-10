from html import escape
from pathlib import Path

STYLE = (Path(__file__).parent / "style.css").read_text()


def page_shell(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>{STYLE}</style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""
