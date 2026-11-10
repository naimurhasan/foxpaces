import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from foxpaces.models.completion import Completion, ModelError

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
RETRY_DELAYS_S = (2, 5, 10)
RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}
REQUEST_TIMEOUT_S = 60


def build_request(model: str, messages: list[dict], max_tokens: int, api_key: str):
    body = {"model": model, "messages": messages, "temperature": 0, "max_tokens": max_tokens}
    return urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Title": "FoxPaces",
        },
    )


def parse_response(payload: dict) -> Completion:
    if "error" in payload:
        raise ModelError(str(payload["error"]))
    usage = payload.get("usage", {})
    return Completion(
        text=payload["choices"][0]["message"].get("content") or "",
        input_tokens=usage.get("prompt_tokens", 0),
        output_tokens=usage.get("completion_tokens", 0),
    )


@dataclass
class OpenRouterModel:
    name: str
    max_tokens: int

    def complete(self, messages: list[dict]) -> Completion:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ModelError("OPENROUTER_API_KEY is not set")
        request = build_request(self.name, messages, self.max_tokens, api_key)
        for delay in (*RETRY_DELAYS_S, None):
            try:
                with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_S) as response:
                    return parse_response(json.load(response))
            except urllib.error.HTTPError as error:
                if error.code not in RETRYABLE_STATUS or delay is None:
                    raise ModelError(f"HTTP {error.code}: {error.read().decode()[:300]}") from error
            except (urllib.error.URLError, TimeoutError) as error:
                if delay is None:
                    raise ModelError(str(error)) from error
            time.sleep(delay)
        raise ModelError("unreachable")
