"""
=============================================================================
NUVI - Machine Learning Intent Classifier Evaluation Script
=============================================================================
Academic Context (AI & Machine Learning Syllabus):
Evaluating an ML model requires statistical metrics calculated against an 
unseen test dataset to verify generalization:

1. Accuracy: Ratio of correct predictions to total test samples.
   Accuracy = (TP + TN) / (TP + TN + FP + FN)

2. Precision: Out of all instances predicted as Intent X, how many were actually X?
   Precision = TP / (TP + FP) (Measures exactness)

3. Recall (Sensitivity): Out of all actual instances of Intent X, how many did the model find?
   Recall = TP / (TP + FN) (Measures completeness)

4. F1-Score: Harmonic mean of Precision and Recall.
   F1 = 2 * (Precision * Recall) / (Precision + Recall)

5. Confusion Matrix: A tabular matrix where row indices represent ground truth 
   classes and column indices represent predicted classes, showing exact error distributions.
=============================================================================
"""

import sys
from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from .preprocess import clean_text


def evaluate_model(
    model_path: str = None,
    vectorizer_path: str = None,
    test_data_path: str = None,
    show_plot: bool = False,
):
    """
    Evaluates the saved model artifacts on unseen test data.
    """
    base_dir = Path(__file__).parent.parent
    if model_path is None:
        model_path = base_dir / "models" / "intent_classifier.pkl"
    else:
        model_path = Path(model_path)

    if vectorizer_path is None:
        vectorizer_path = base_dir / "models" / "tfidf_vectorizer.pkl"
    else:
        vectorizer_path = Path(vectorizer_path)

    if test_data_path is None:
        test_data_path = base_dir / "data" / "test_commands.csv"
    else:
        test_data_path = Path(test_data_path)

    # If test_commands.csv does not exist yet, we can train first or load from commands.csv
    if not model_path.exists() or not vectorizer_path.exists():
        print("[Notice] Model artifacts not found. Training model first...")
        from .train_model import train_intent_model
        train_intent_model()

    if not test_data_path.exists():
        # Regenerate test set by running training
        from .train_model import train_intent_model
        train_intent_model()

    # Load artifacts
    classifier = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    test_df = pd.read_csv(test_data_path)

    X_test_raw = test_df["command"]
    y_test = test_df["intent"]

    # Transform using pre-fitted TF-IDF vectorizer
    X_test_tfidf = vectorizer.transform(X_test_raw)
    y_pred = classifier.predict(X_test_tfidf)

    accuracy = accuracy_score(y_test, y_pred)
    classes = list(classifier.classes_)
    report = classification_report(y_test, y_pred, labels=classes, zero_division=0)
    matrix = confusion_matrix(y_test, y_pred, labels=classes)

    print("\n" + "=" * 50)
    print("NUVI Intent Classifier Evaluation Report")
    print("=" * 50)
    print(f"Testing Samples Evaluated: {len(test_df)}")
    print(f"Accuracy: {accuracy * 100:.2f}%\n")
    print("Classification Report:")
    print(report)

    print("Confusion Matrix:")
    # Format confusion matrix with clear class labels
    header = f"{'Actual \\ Pred':<20}" + "".join([f"{c[:8]:>10}" for c in classes])
    print(header)
    print("-" * len(header))
    for idx, row in enumerate(matrix):
        row_str = f"{classes[idx]:<20}" + "".join([f"{val:>10}" for val in row])
        print(row_str)
    print("=" * 50 + "\n")

    if show_plot:
        try:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 6))
            im = ax.imshow(matrix, interpolation='nearest', cmap=plt.cm.Blues)
            ax.figure.colorbar(im, ax=ax)
            ax.set(
                xticks=range(len(classes)),
                yticks=range(len(classes)),
                xticklabels=classes,
                yticklabels=classes,
                title="Confusion Matrix - NUVI Intent Classification",
                ylabel="True Intent",
                xlabel="Predicted Intent",
            )
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            plt.tight_layout()
            plot_path = base_dir / "data" / "confusion_matrix.png"
            plt.savefig(plot_path)
            print(f"Confusion matrix plot saved to: {plot_path}")
            plt.close()
        except Exception as e:
            print(f"Note: Could not generate visual confusion matrix plot: {e}")

    return accuracy, report, matrix


if __name__ == "__main__":
    evaluate_model(show_plot=True)
