from collections.abc import Iterator
from contextlib import contextmanager

from camoufox.sync_api import Camoufox
from playwright.sync_api import Browser, sync_playwright

CAMOUFOX = "camoufox"
CHROMIUM = "chromium"
BROWSERS = (CAMOUFOX, CHROMIUM)


@contextmanager
def open_browser(name: str = CAMOUFOX, headless: bool = True) -> Iterator[Browser]:
    if name == CHROMIUM:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=headless)
            yield browser
            browser.close()
        return
    with Camoufox(headless=headless) as browser:
        yield browser
