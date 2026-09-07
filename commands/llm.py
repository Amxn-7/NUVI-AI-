import json
import os
import urllib.error
import urllib.request


from pathlib import Path

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o-mini"


class LLMError(RuntimeError):
    pass


def _load_dotenv():
    base_dir = Path(__file__).parent.parent
    for filename in [".env", ".env.example"]:
        env_path = base_dir / filename
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, val = line.split("=", 1)
                            key = key.strip()
                            val = val.strip().strip("'\"")
                            if key and key not in os.environ:
                                os.environ[key] = val
            except Exception:
                pass
            if os.getenv("OPENROUTER_API_KEY"):
                break


def get_model() -> str:
    _load_dotenv()
    return os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)


def is_configured() -> bool:
    _load_dotenv()
    return bool(os.getenv("OPENROUTER_API_KEY"))



def chat(messages: list[dict[str, str]], *, temperature: float = 0.2, max_tokens: int = 700) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise LLMError("Set OPENROUTER_API_KEY before using AI commands.")

    payload = {
        "model": get_model(),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    request = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost/desktop-assistant",
            "X-Title": "Desktop AI Assistant",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LLMError(f"OpenRouter error {exc.code}: {detail[:240]}") from exc
    except Exception as exc:
        raise LLMError(f"OpenRouter request failed: {exc}") from exc

    try:
        return body["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("OpenRouter returned an unexpected response.") from exc


def ask_json(messages: list[dict[str, str]], *, max_tokens: int = 400) -> dict:
    text = chat(messages, temperature=0.0, max_tokens=max_tokens)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise LLMError("The model did not return JSON.")
    return json.loads(text[start:end + 1])
