from playwright.sync_api import Locator, Page

SCROLL_PIXELS = 600


def element_at(page: Page, index: int) -> Locator:
    return page.locator(f'[data-fp-index="{index}"]')


def execute_action(page: Page, action: dict) -> None:
    match action["action"]:
        case "click":
            element_at(page, action["index"]).click()
        case "type":
            element = element_at(page, action["index"])
            element.fill(action["text"])
            if action.get("submit"):
                element.press("Enter")
        case "select":
            element_at(page, action["index"]).select_option(label=action["option"])
        case "scroll":
            page.mouse.wheel(0, SCROLL_PIXELS if action["direction"] == "down" else -SCROLL_PIXELS)
        case "navigate":
            page.goto(action["url"])
        case "go_back":
            page.go_back()
    page.wait_for_load_state()
