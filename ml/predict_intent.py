"""
=============================================================================
NUVI - Machine Learning Intent Predictor & Confidence Engine
=============================================================================
Academic Context (AI & Machine Learning Syllabus):
1. Inference Phase:
   Once a model is trained and weights are learned, the model performs "Inference".
   The user's raw string is preprocessed, mapped into the learned TF-IDF vector
   space, and passed through the Logistic Regression decision boundary.

2. Probability Estimation (Softmax / Sigmoid):
   Logistic Regression provides calibrated posterior probabilities P(Intent | Command).
   Using `predict_proba`, we obtain confidence scores across all classes.

3. Confidence Thresholding (Uncertainty Handling in AI Agents):
   Real-world AI agents must avoid catastrophic false actions.
   - High Confidence (>= 0.70): Safe to act autonomously.
   - Medium Confidence (0.40 - 0.69): Ambiguous; ask the user for confirmation.
   - Low Confidence (< 0.40): Fallback to conversational/knowledge reasoning.
=============================================================================
"""

import os
from pathlib import Path
from typing import Dict, Tuple, Optional
import joblib

from .preprocess import clean_text

# =============================================================================
# Configurable Confidence Thresholds
# =============================================================================
HIGH_CONFIDENCE_THRESHOLD = 0.70    # >= 70%: Direct execution
MEDIUM_CONFIDENCE_THRESHOLD = 0.40  # 40% - 69%: Clarification prompt
# Below 40%: Fallback to General Question / LLM


class IntentClassifier:
    """
    Singleton-style wrapper for fast in-memory intent inference.
    """
    _instance = None

    def __init__(self, model_path: Optional[Path] = None, vectorizer_path: Optional[Path] = None):
        base_dir = Path(__file__).parent.parent
        self.model_path = model_path or (base_dir / "models" / "intent_classifier.pkl")
        self.vectorizer_path = vectorizer_path or (base_dir / "models" / "tfidf_vectorizer.pkl")
        self.model = None
        self.vectorizer = None
        self._load_artifacts()

    def _load_artifacts(self):
        """Loads serialized model and vectorizer from disk, auto-training if missing."""
        if not self.model_path.exists() or not self.vectorizer_path.exists():
            print("[NUVI ML] Artifacts not found. Initiating first-time model training...")
            from .train_model import train_intent_model
            train_intent_model()

        try:
            self.model = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)
        except Exception as e:
            print(f"[NUVI ML] Error loading model artifacts: {e}. Retraining...")
            from .train_model import train_intent_model
            train_intent_model()
            self.model = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)

    def predict(self, command: str) -> Dict[str, any]:
        """
        Predicts intent and probability distribution for a given command.

        Returns:
            dict containing:
                - intent: Predicted class string
                - confidence: Float (0.0 to 1.0)
                - status: 'HIGH', 'MEDIUM', or 'LOW'
                - probabilities: Dict mapping each intent class to its probability
        """
        if not command or not command.strip():
            return {
                "intent": "GENERAL_QUESTION",
                "confidence": 0.0,
                "status": "LOW",
                "probabilities": {},
            }

        # Step 1: Preprocess user input
        cleaned = clean_text(command)
        if not cleaned:
            return {
                "intent": "GENERAL_QUESTION",
                "confidence": 0.0,
                "status": "LOW",
                "probabilities": {},
            }

        # Step 2: Transform to TF-IDF numerical vector
        features = self.vectorizer.transform([cleaned])

        # Step 3: Compute probabilities across all classes
        probs = self.model.predict_proba(features)[0]
        classes = self.model.classes_

        class_probabilities = {cls: float(prob) for cls, prob in zip(classes, probs)}

        # Find class with highest probability
        best_index = probs.argmax()
        predicted_intent = classes[best_index]
        confidence = float(probs[best_index])

        # Step 4: Categorize confidence tier
        if confidence >= HIGH_CONFIDENCE_THRESHOLD:
            status = "HIGH"
        elif confidence >= MEDIUM_CONFIDENCE_THRESHOLD:
            status = "MEDIUM"
        else:
            status = "LOW"

        return {
            "intent": predicted_intent,
            "confidence": confidence,
            "status": status,
            "probabilities": class_probabilities,
            "cleaned_command": cleaned,
        }


# Global cached predictor instance
_predictor: Optional[IntentClassifier] = None


def get_predictor() -> IntentClassifier:
    """Returns the shared IntentClassifier instance."""
    global _predictor
    if _predictor is None:
        _predictor = IntentClassifier()
    return _predictor


def predict_intent(command: str) -> Tuple[str, float, str]:
    """
    Convenience wrapper returning (intent, confidence, status).
    Example: ('OPEN_APPLICATION', 0.88, 'HIGH')
    """
    result = get_predictor().predict(command)
    return result["intent"], result["confidence"], result["status"]
