"""
=============================================================================
NUVI - Machine Learning Intent Classifier Training Pipeline
=============================================================================
Academic Context (AI & Machine Learning Syllabus):
1. Supervised Learning:
   We provide labeled pairs (X = text command, y = intent). The algorithm learns
   a mapping function f(X) -> y to predict the intent of unseen user commands.

2. Why Numerical Feature Extraction (TF-IDF)?
   Traditional machine learning algorithms (like Logistic Regression) operate on
   mathematical vectors and matrices in Euclidean space, not raw text strings.
   
   TF-IDF (Term Frequency - Inverse Document Frequency) converts textual data 
   into numerical feature vectors:
   - Term Frequency (TF): Measures how frequently a word occurs in a command.
   - Inverse Document Frequency (IDF): Penalizes common generic words (e.g., 'the',
     'is') and boosts discriminative keywords (e.g., 'chrome', 'resume', 'csv').
   - Formula: TF-IDF(t, d, D) = TF(t, d) * log(|D| / (1 + |{d in D : t in d}|))

3. Train/Test Split:
   To honestly evaluate how well the model generalizes to new, unseen user 
   queries, we split our dataset:
   - 80% Training Set: Used by the learning algorithm to adjust model weights.
   - 20% Testing Set: Kept strictly unseen during training to evaluate real-world
     accuracy, precision, recall, and prevent overfitting.
   - random_state=42 ensures reproducibility across experiments.

4. Logistic Regression:
   A foundational linear classification model that applies the sigmoid/softmax
   activation function to a weighted linear combination of TF-IDF input features,
   outputting well-calibrated probability distributions for each intent class.
=============================================================================
"""

import os
from pathlib import Path
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from .preprocess import clean_text, preprocess_dataset


def train_intent_model(
    dataset_path: str = None,
    models_dir: str = None,
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict:
    """
    Executes the end-to-end Machine Learning training workflow:
    Dataset Loading -> Data Cleaning -> 80/20 Train/Test Split ->
    TF-IDF Vectorization -> Logistic Regression Training -> Evaluation -> Model Persistence.
    """
    base_dir = Path(__file__).parent.parent
    if dataset_path is None:
        dataset_path = base_dir / "data" / "commands.csv"
    else:
        dataset_path = Path(dataset_path)

    if models_dir is None:
        models_dir = base_dir / "models"
    else:
        models_dir = Path(models_dir)

    models_dir.mkdir(parents=True, exist_ok=True)

    print("==================================================")
    print("NUVI Machine Learning Training Pipeline")
    print("==================================================")

    # 1. Load Dataset
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset file not found at: {dataset_path}")

    print(f"[Step 1] Loading dataset from: {dataset_path.name}")
    raw_df = pd.read_csv(dataset_path)
    print(f"         Total raw samples: {len(raw_df)}")

    # 2. Data Preprocessing & Cleaning
    print("[Step 2] Applying text preprocessing and deduplication...")
    df = preprocess_dataset(raw_df, text_column="command", label_column="intent")
    print(f"         Cleaned unique samples: {len(df)}")
    print(f"         Intent classes ({df['intent'].nunique()}): {sorted(df['intent'].unique())}")

    X = df["command"]
    y = df["intent"]

    # 3. Train / Test Split (80% Train, 20% Test with stratification)
    print(f"[Step 3] Splitting dataset into {int((1-test_size)*100)}% Train / {int(test_size*100)}% Test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )
    print(f"         Training Samples: {len(X_train)}")
    print(f"         Testing Samples : {len(X_test)}")

    # Also save the test set to data/test_data_commands.csv for standalone evaluation
    test_export_path = base_dir / "data" / "test_commands.csv"
    pd.DataFrame({"command": X_test, "intent": y_test}).to_csv(test_export_path, index=False)

    # 4. Feature Extraction: TF-IDF Vectorizer
    # We include unigrams and bigrams (ngram_range=(1, 2)) to capture word pairs (e.g. 'open chrome')
    print("[Step 4] Extracting TF-IDF features (unigrams + bigrams)...")
    vectorizer = TfidfVectorizer(
        preprocessor=clean_text,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    print(f"         Vocabulary Size (Number of Features): {len(vectorizer.get_feature_names_out())}")

    # 5. Model Training: Logistic Regression
    print("[Step 5] Training Logistic Regression classifier...")
    classifier = LogisticRegression(
        max_iter=1000,
        random_state=random_state,
        C=5.0,
        solver="lbfgs",
    )
    classifier.fit(X_train_tfidf, y_train)
    print("         Model training completed successfully.")

    # 6. Evaluation on Unseen Test Data
    print("[Step 6] Evaluating on 20% unseen test dataset...")
    y_pred = classifier.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=0)
    matrix = confusion_matrix(y_test, y_pred, labels=classifier.classes_)

    print("\n--------------------------------------------------")
    print("Model Evaluation Summary")
    print("--------------------------------------------------")
    print(f"Accuracy: {accuracy * 100:.2f}%\n")
    print("Classification Report:")
    print(report)

    # 7. Model Serialization using Joblib
    model_path = models_dir / "intent_classifier.pkl"
    vectorizer_path = models_dir / "tfidf_vectorizer.pkl"

    print("[Step 7] Saving artifacts for runtime inference...")
    joblib.dump(classifier, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    print(f"         Saved Classifier : {model_path}")
    print(f"         Saved Vectorizer : {vectorizer_path}")
    print("==================================================")
    print("Training pipeline finished successfully!\n")

    return {
        "accuracy": accuracy,
        "classification_report": report,
        "confusion_matrix": matrix,
        "classes": list(classifier.classes_),
        "num_train": len(X_train),
        "num_test": len(X_test),
    }


if __name__ == "__main__":
    train_intent_model()
