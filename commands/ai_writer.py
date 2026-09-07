import re
from pathlib import Path

from .llm import LLMError, chat


def _target_file_from_request(command_text: str) -> str:
    match = re.search(r"(?:to|in|as|called|named)\s+([\w.\- ]+\.[a-zA-Z0-9]{1,8})\b", command_text)
    if match:
        return Path(match.group(1).strip()).name
    return "ai_output.txt"


def write_file_ai(command_text: str) -> str:
    """
    Use OpenRouter to write content to a file.
    Example: 'write a README for my movie recommendation project to README.md'
    """
    prompt = command_text.replace("write ", "", 1).strip()
    if not prompt:
        return "Please specify what to write."

    try:
        content = chat([
            {
                "role": "system",
                "content": "Write the requested file content only. Do not include markdown fences or extra commentary.",
            },
            {"role": "user", "content": prompt},
        ], temperature=0.4, max_tokens=1600)

        output_file = _target_file_from_request(command_text)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Generated and saved: {output_file}"
    except LLMError as exc:
        return str(exc)
    except Exception as exc:
        return f"Failed to generate text: {exc}"
