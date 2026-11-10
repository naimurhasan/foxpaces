from dataclasses import dataclass

from playwright.sync_api import Page

MAX_PAGE_TEXT_CHARS = 3000

SNAPSHOT_JS = """
() => {
  const selector = 'a[href], button, input:not([type=hidden]), select, textarea, [role=button], [onclick]';
  document.querySelectorAll('[data-fp-index]').forEach((el) => el.removeAttribute('data-fp-index'));
  const isVisible = (el) => {
    const rect = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    const nearViewport = rect.top < innerHeight * 2 && rect.bottom > -innerHeight;
    return nearViewport && rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
  };
  const labelOf = (el) => (
    el.getAttribute('aria-label') || el.labels?.[0]?.innerText || el.innerText ||
    el.getAttribute('placeholder') || el.getAttribute('name') || el.getAttribute('title') || ''
  ).trim().replace(/\\s+/g, ' ').slice(0, 80);
  const elements = [...document.querySelectorAll(selector)].filter(isVisible).map((el, index) => {
    el.setAttribute('data-fp-index', String(index));
    return {
      index,
      tag: el.tagName.toLowerCase(),
      type: el.getAttribute('type') || '',
      label: labelOf(el),
      value: typeof el.value === 'string' && el.tagName !== 'BUTTON' ? el.value : '',
      checked: ['checkbox', 'radio'].includes(el.type) ? el.checked : null,
      options: el.tagName === 'SELECT' ? [...el.options].map((o) => o.text) : [],
    };
  });
  return { url: location.href, title: document.title, elements, text: document.body.innerText };
}
"""


@dataclass(frozen=True)
class Observation:
    url: str
    title: str
    elements: list[dict]
    text: str


def take_observation(page: Page) -> Observation:
    return Observation(**page.evaluate(SNAPSHOT_JS))


def format_element(element: dict) -> str:
    kind = f"{element['tag']}[{element['type']}]" if element["type"] else element["tag"]
    parts = [f'[{element["index"]}] {kind} "{element["label"]}"']
    if element["value"]:
        parts.append(f'value="{element["value"]}"')
    if element["checked"] is not None:
        parts.append(f"checked={str(element['checked']).lower()}")
    if element["options"]:
        parts.append(f"options={element['options']}")
    return " ".join(parts)


def format_observation(observation: Observation) -> str:
    elements = "\n".join(format_element(element) for element in observation.elements) or "none"
    return (
        f"URL: {observation.url}\nTitle: {observation.title}\n"
        f"Interactive elements:\n{elements}\n"
        f"Page text:\n{observation.text[:MAX_PAGE_TEXT_CHARS]}"
    )
