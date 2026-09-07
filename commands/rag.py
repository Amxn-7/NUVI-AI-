import os

from .llm import LLMError, chat


def handle_rag_query(filepath: str, query: str) -> str:
    """
    Read PDF, CSV, or TXT content and answer the user's question using OpenRouter.
    """
    if not filepath or not os.path.exists(filepath):
        return f"File not found: {filepath}"

    ext = os.path.splitext(filepath)[1].lower()
    text_content = ""

    try:
        if ext == ".pdf":
            import PyPDF2
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text_content = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif ext == ".csv":
            import pandas as pd
            df = pd.read_csv(filepath)
            text_content = df.head(100).to_string()
        elif ext == ".txt":
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                text_content = f.read()
        else:
            return f"Unsupported file type: {ext}. Use PDF, CSV, or TXT."

        if not text_content.strip():
            return "File appears to be empty or unreadable."

        max_chars = 10000
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars] + "\n...[truncated]..."

        system_prompt = (
            "Answer the user's question using only the document content below. "
            "If the document does not contain the answer, say so briefly.\n\n"
            f"{text_content}"
        )

        return chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query if query else "Summarize this document."},
        ], max_tokens=900)
    except LLMError as exc:
        return str(exc)
    except Exception as exc:
        return f"Error processing file: {exc}"
