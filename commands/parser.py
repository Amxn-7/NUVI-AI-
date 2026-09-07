"""
=============================================================================
NUVI - Intelligent Command Parser & Actuator Routing System
=============================================================================
Academic Context (AI Agent Architecture):
In an Intelligent Agent architecture:
1. Perception (Sensors): Raw text / voice transcribed command is received.
2. Preprocessing & Feature Extraction: Normalization and TF-IDF numerical vectorization.
3. Intent Classification (Supervised ML): Logistic Regression computes P(Intent | Command).
4. Decision Layer (Confidence Engine):
   - High Confidence (>= 70%): Actuator execution.
   - Medium Confidence (40% - 69%): Active clarification to prevent erroneous actions.
   - Low Confidence (< 40%): Fallback to Generative AI / Educational Knowledge base.
5. Actuators (Environment Interaction): OS launchers, file management, data analysis, UI feedback.
6. History Logger: Transparent record of user commands and model decisions.
=============================================================================
"""

import csv
from datetime import datetime
import json
import os
from pathlib import Path
import re
from typing import Optional

from .ai_writer import write_file_ai
from .launcher import launch_app
from .llm import LLMError, ask_json, chat, is_configured
from .search import find_file
from .workspace import open_workspace

# Import NUVI Machine Learning and Data Analysis modules
from ml.predict_intent import (
    get_predictor,
    HIGH_CONFIDENCE_THRESHOLD,
    MEDIUM_CONFIDENCE_THRESHOLD,
)
from data_analysis.analyzer import analyze_csv, clean_csv, detect_cleaning_needs
from data_analysis.visualization import plot_dataset


_WORKSPACE_NAMES = set()
_config_path = Path(__file__).parent.parent / "config" / "workspaces.json"
try:
    if _config_path.exists():
        with open(_config_path, "r", encoding="utf-8") as _f:
            _WORKSPACE_NAMES = set(json.load(_f).keys())
except Exception:
    pass


def _log_command_history(command: str, intent: str, confidence: float):
    """
    Logs user commands, predicted intent, confidence score, and timestamp
    into data/command_history.csv for auditing and transparent analysis.
    """
    history_file = Path(__file__).parent.parent / "data" / "command_history.csv"
    history_file.parent.mkdir(parents=True, exist_ok=True)
    file_exists = history_file.exists()

    try:
        with open(history_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["command", "intent", "confidence", "timestamp"])
            writer.writerow([
                command,
                intent,
                f"{confidence:.4f}",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ])
    except Exception as exc:
        print(f"[NUVI History] Failed to log command: {exc}")


def _clean(text: str) -> str:
    """Removes common conversational fillers and courtesies."""
    fillers = [
        "please", "can you", "could you", "hey", "hi", "yo",
        "buddy", "assistant", "pet", "just", "quickly", "now",
        "for me", "the", "my", "a", "an", "up", "me", "i want to",
        "i need to", "i'd like to", "go ahead and", "nuvi",
    ]
    result = text
    for filler in fillers:
        pattern = r"\b" + re.escape(filler) + r"\b"
        result = re.sub(pattern, " ", result, flags=re.IGNORECASE)
    return " ".join(result.split()).strip()


def _contains_workspace_name(text: str) -> Optional[str]:
    for name in _WORKSPACE_NAMES:
        if name in text:
            return name
    return None


def _create_file(filename: str) -> str:
    safe_name = os.path.basename(filename.strip()) or "untitled.txt"
    try:
        with open(safe_name, "w", encoding="utf-8") as f:
            f.write("")
        return f"Created: {safe_name}"
    except Exception as exc:
        return f"Error: {exc}"


def _find_csv_file(raw_command: str) -> Optional[str]:
    """Finds a referenced .csv file in the command or working directories."""
    # Check for explicit filename in command
    match = re.search(r"([\w.\-_\\/]+\.csv)", raw_command, flags=re.IGNORECASE)
    if match:
        candidate = match.group(1).strip()
        if os.path.exists(candidate):
            return candidate
        base_candidate = Path(__file__).parent.parent / candidate
        if base_candidate.exists():
            return str(base_candidate)
        data_candidate = Path(__file__).parent.parent / "data" / candidate
        if data_candidate.exists():
            return str(data_candidate)
        return candidate

    # Check common sample datasets in data/ or workspace
    sample_csv = Path(__file__).parent.parent / "data" / "sample_marks.csv"
    if sample_csv.exists():
        return str(sample_csv)

    for p in Path(__file__).parent.parent.glob("*.csv"):
        return str(p)

    return None


def _answer_educational_question(query: str) -> str:
    """
    Provides instant offline answers for core syllabus AI/ML concepts and general queries,
    with automatic OpenRouter LLM delegation if configured.
    """
    if is_configured():
        try:
            return chat([
                {"role": "system", "content": "You are NUVI, a helpful and knowledgeable AI desktop assistant."},
                {"role": "user", "content": query},
            ], max_tokens=600)
        except LLMError as exc:
            return f"AI Error: {exc}"

    # Offline knowledge base for syllabus concepts
    q = query.lower()
    if "machine learning" in q and "artificial intelligence" in q:
        return "AI is the broad science of creating intelligent systems. Machine Learning (ML) is a subset of AI where systems learn patterns from data rather than following rigid hand-coded rules."
    elif "supervised learning" in q:
        return "Supervised Learning is an ML paradigm where models learn from labeled training pairs (inputs and targets), such as predicting an intent from text commands."
    elif "logistic regression" in q:
        return "Logistic Regression is a supervised classification algorithm that applies a sigmoid/softmax function to a linear combination of features to output class probabilities."
    elif "tf idf" in q or "tfidf" in q:
        return "TF-IDF (Term Frequency - Inverse Document Frequency) converts text into numerical features. It measures word frequency in a document scaled by its rarity across all documents."
    elif "agent" in q or "peas" in q:
        return "An AI Agent perceives its environment through sensors and acts upon it through actuators. PEAS stands for Performance measure, Environment, Actuators, and Sensors."
    elif "train test split" in q or "test split" in q:
        return "Train/Test split divides data into training (e.g., 80%) to fit model parameters and testing (e.g., 20%) to honestly evaluate generalization and prevent overfitting."
    elif "confusion matrix" in q:
        return "A Confusion Matrix summarizes classification performance, mapping true classes against predicted classes to compute Accuracy, Precision, Recall, and F1-score."
    elif "data cleaning" in q or "missing value" in q:
        return "Data Cleaning prepares raw data for analysis by handling missing values (via imputation), removing duplicate rows, and eliminating corrupt records."
    elif "who are you" in q or "what is nuvi" in q or "hello" in q or "hi" in q:
        return "Hello! I am NUVI, an Intelligent AI Desktop Assistant powered by Supervised Machine Learning (TF-IDF + Logistic Regression) and Python automation."
    else:
        return f"NUVI understood: '{query}'. (Set OPENROUTER_API_KEY in .env for open-ended generative AI answers)."


def _extract_filename_for_creation(text: str) -> str:
    """Extracts target filename cleanly for CREATE_FILE intent."""
    patterns = [
        r"(?:create|make)\s+(?:a\s+)?(?:new\s+)?(?:text\s+)?(?:file|document)\s+(?:called\s+|named\s+)?([\w.\-_]+)",
        r"(?:create|make)\s+(?:a\s+)?(?:new\s+)?(?:file|document)?\s*([\w.\-_]+\.[a-zA-Z0-9]{1,5})",
        r"(?:called|named)\s+([\w.\-_]+)",
        r"(?:create|make)\s+([\w.\-_]+)",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            if candidate and candidate.lower() not in ["file", "document", "a", "an", "the", "new"]:
                return candidate
    return "untitled.txt"


def _execute_intent(intent: str, command: str, raw: str, cleaned: str) -> str:
    """Executes the specific actuator corresponding to a high-confidence intent."""
    if intent == "OPEN_APPLICATION":
        match = re.search(r"(?:open|launch|start|run)\s+(.+)", cleaned)
        app_name = match.group(1).strip() if match else cleaned
        app_name = re.sub(r"\s+(for me|now|please)$", "", app_name).strip()
        if not app_name:
            app_name = "notepad"
        return launch_app(app_name)

    elif intent == "FIND_FILE":
        match = re.search(r"(?:find|search|look for|locate|where(?:\s+is)?)\s+(.+)", cleaned)
        filename = match.group(1).strip() if match else cleaned
        if not filename:
            return "Please specify a filename or keyword to search."
        return find_file(filename)

    elif intent == "CREATE_FILE":
        filename = _extract_filename_for_creation(raw)
        return _create_file(filename)

    elif intent == "OPEN_WORKSPACE":
        ws_name = _contains_workspace_name(raw) or _contains_workspace_name(cleaned)
        if ws_name:
            return open_workspace(f"open {ws_name} workspace")
        return open_workspace(raw)

    elif intent == "DOCUMENT_QUERY":
        from .rag import handle_rag_query
        match = re.search(r"([\w.\-_\\/]+\.(?:pdf|csv|txt))", raw)
        if match:
            return handle_rag_query(match.group(1), raw)
        return "Please specify a document to read, e.g. 'summarize report.pdf' or 'read notes.txt'."

    elif intent == "DATA_ANALYSIS":
        csv_file = _find_csv_file(raw)
        if not csv_file:
            return "No CSV file specified or found. Provide a dataset like: 'analyze data/sample_marks.csv'."

        # Sub-action 1: Data Cleaning
        if any(w in raw for w in ["clean", "remove duplicate", "handle missing", "fix null", "dedup"]):
            summary, new_path = clean_csv(csv_file)
            return summary

        # Sub-action 2: Data Visualization
        if any(w in raw for w in ["graph", "plot", "chart", "histogram", "bar", "line", "visualize"]):
            plot_type = "auto"
            if "bar" in raw:
                plot_type = "bar"
            elif "hist" in raw or "distribution" in raw:
                plot_type = "hist"
            elif "line" in raw or "trend" in raw:
                plot_type = "line"

            # Check if a specific column is requested (e.g. 'maths', 'science')
            column = None
            try:
                import pandas as pd
                sample_df = pd.read_csv(csv_file, nrows=1)
                for col in sample_df.columns:
                    if col.lower() in raw:
                        column = col
                        break
            except Exception:
                pass

            msg, plot_path = plot_dataset(csv_file, plot_type=plot_type, column=column)
            return f"{msg}\nChart saved: {plot_path}"

        # Sub-action 3: Descriptive Analysis (Default)
        return analyze_csv(csv_file)

    elif intent == "GENERAL_QUESTION":
        return _answer_educational_question(raw)

    return f"Intent '{intent}' recognized, but no matching actuator is configured."


def parse_and_execute(command: str) -> str:
    """
    Main entry point for command processing in NUVI.

    Architecture Flow:
    1. Input Perception -> Text Preprocessing
    2. ML Intent Classification (TF-IDF + Logistic Regression)
    3. Probability Confidence Evaluation
    4. Actuator Dispatch or Confirmation Clarification
    5. Audit Logging to command_history.csv
    """
    if not command or not command.strip():
        return "Empty command."

    raw = command.strip()
    raw_lower = raw.lower()
    cleaned = _clean(raw_lower)

    # 1. Specialized Direct Feature: AI Writer prompt
    if any(cleaned.startswith(w) for w in ["write ", "generate ", "draft ", "compose "]):
        _log_command_history(raw, "AI_WRITER", 1.0)
        return write_file_ai(raw)

    # 2. ML Intent Classification
    try:
        predictor = get_predictor()
        prediction = predictor.predict(raw)
        intent = prediction["intent"]
        confidence = prediction["confidence"]
        status = prediction["status"]
    except Exception as exc:
        print(f"[NUVI ML] Classifier error: {exc}. Falling back to rule-based routing.")
        intent = "UNKNOWN"
        confidence = 0.0
        status = "LOW"

    # 3. Log to History
    _log_command_history(raw, intent, confidence)

    # 4. Confidence-Based Decision Routing
    # Case A: HIGH CONFIDENCE (>= 70%) -> Execute directly
    if status == "HIGH":
        return _execute_intent(intent, command, raw_lower, cleaned)

    # Case B: MEDIUM CONFIDENCE (40% - 69%) -> Active Clarification
    elif status == "MEDIUM":
        intent_descriptions = {
            "OPEN_APPLICATION": "launch an application",
            "FIND_FILE": "search for a file on your system",
            "CREATE_FILE": "create a new document",
            "OPEN_WORKSPACE": "open a predefined project workspace",
            "DOCUMENT_QUERY": "read and summarize a document",
            "DATA_ANALYSIS": "inspect or visualize a dataset",
            "GENERAL_QUESTION": "answer an educational question",
        }
        desc = intent_descriptions.get(intent, intent.lower().replace("_", " "))
        return (
            f"NUVI: I think you want me to {desc} (Confidence: {confidence * 100:.1f}%).\n"
            f"Please clarify or repeat with more specifics."
        )

    # Case C: LOW CONFIDENCE (< 40%) -> Fallback to Rule-based / General Question / LLM
    else:
        # Check if local keyword rule can assist
        ws_name = _contains_workspace_name(raw_lower) or _contains_workspace_name(cleaned)
        if ws_name:
            return open_workspace(f"open {ws_name} workspace")
        if "workspace" in raw_lower:
            return open_workspace(raw_lower)

        # Fallback to general question answering / OpenRouter
        return _answer_educational_question(raw)
