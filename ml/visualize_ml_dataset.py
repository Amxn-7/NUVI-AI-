"""
=============================================================================
NUVI - ML Dataset & Model Evaluation Visualization Generator
=============================================================================
This script processes the NUVI command intent dataset (`commands.csv`), 
performs feature extraction & dataset analytics, executes model evaluation,
and saves high-resolution publication-quality visualization figures to the
`output/` directory for academic evaluation and viva presentations.
=============================================================================
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for reliable PNG export
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib

try:
    from ml.preprocess import clean_text, preprocess_dataset
except ImportError:
    from preprocess import clean_text, preprocess_dataset


def generate_all_visualizations(
    base_dir: Path = None,
    output_dir: Path = None,
):
    if base_dir is None:
        base_dir = Path(__file__).parent.parent
    if output_dir is None:
        output_dir = base_dir / "output"

    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = base_dir / "data" / "commands.csv"

    print("==================================================")
    print("NUVI Machine Learning Visualization Pipeline")
    print("==================================================")
    print(f"Loading dataset: {dataset_path}")

    raw_df = pd.read_csv(dataset_path)
    df = preprocess_dataset(raw_df, text_column="command", label_column="intent")

    # Styling settings
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#cccccc"
    plt.rcParams["axes.linewidth"] = 0.8

    palette = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
        "#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"
    ]

    # -------------------------------------------------------------------------
    # Chart 1: Intent Class Distribution (Bar Chart & Percentage)
    # -------------------------------------------------------------------------
    print("[1/6] Generating intent distribution chart...")
    fig, ax = plt.subplots(figsize=(10, 6))
    intent_counts = df["intent"].value_counts().sort_values(ascending=True)
    total_samples = len(df)

    bars = ax.barh(intent_counts.index, intent_counts.values, color="#34495e", edgecolor="#2c3e50", height=0.65)
    
    # Annotate bars with exact count and percentage
    for bar in bars:
        width = bar.get_width()
        pct = (width / total_samples) * 100
        ax.text(
            width + 0.3,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width)} ({pct:.1f}%)",
            va="center",
            ha="left",
            fontsize=10,
            fontweight="bold",
            color="#2c3e50",
        )

    ax.set_title("NUVI Dataset: Intent Class Frequency Distribution", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Number of Samples", fontsize=11, labelpad=10)
    ax.set_ylabel("Intent Label", fontsize=11)
    ax.set_xlim(0, max(intent_counts.values) * 1.22)
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    plt.tight_layout()
    chart1_path = output_dir / "intent_distribution.png"
    fig.savefig(chart1_path, dpi=300)
    plt.close(fig)
    print(f"      Saved: {chart1_path.name}")

    # -------------------------------------------------------------------------
    # Chart 2: Command Character & Word Length Distribution
    # -------------------------------------------------------------------------
    print("[2/6] Generating command length distribution chart...")
    df["char_length"] = df["command"].apply(len)
    df["word_count"] = df["command"].apply(lambda x: len(x.split()))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Subplot 1: Character Length Histogram & KDE
    ax1.hist(df["char_length"], bins=15, color="#2980b9", edgecolor="#1b4f72", alpha=0.8)
    ax1.axvline(df["char_length"].mean(), color="#e74c3c", linestyle="--", linewidth=2, label=f"Mean: {df['char_length'].mean():.1f} chars")
    ax1.axvline(df["char_length"].median(), color="#2ecc71", linestyle="-.", linewidth=2, label=f"Median: {df['char_length'].median():.1f} chars")
    ax1.set_title("Distribution of Character Length per Command", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Character Count", fontsize=10)
    ax1.set_ylabel("Frequency", fontsize=10)
    ax1.legend(fontsize=9)
    ax1.grid(True, linestyle="--", alpha=0.5)

    # Subplot 2: Word Count Distribution per Intent (Boxplot summary)
    ax2.hist(df["word_count"], bins=range(1, max(df["word_count"]) + 2), color="#8e44ad", edgecolor="#5b2c6f", alpha=0.8, align="left")
    ax2.axvline(df["word_count"].mean(), color="#e74c3c", linestyle="--", linewidth=2, label=f"Mean: {df['word_count'].mean():.1f} words")
    ax2.set_title("Distribution of Word Count per Command", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Word Count", fontsize=10)
    ax2.set_ylabel("Frequency", fontsize=10)
    ax2.legend(fontsize=9)
    ax2.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    chart2_path = output_dir / "command_length_distribution.png"
    fig.savefig(chart2_path, dpi=300)
    plt.close(fig)
    print(f"      Saved: {chart2_path.name}")

    # -------------------------------------------------------------------------
    # Chart 3: Top TF-IDF Features across Dataset
    # -------------------------------------------------------------------------
    print("[3/6] Extracting and visualizing top TF-IDF N-gram features...")
    vectorizer = TfidfVectorizer(preprocessor=clean_text, ngram_range=(1, 2), sublinear_tf=True)
    tfidf_matrix = vectorizer.fit_transform(df["command"])
    feature_names = np.array(vectorizer.get_feature_names_out())
    mean_tfidf = np.asarray(tfidf_matrix.mean(axis=0)).ravel()
    top_indices = np.argsort(mean_tfidf)[::-1][:15]

    top_features = feature_names[top_indices]
    top_scores = mean_tfidf[top_indices]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(top_features[::-1], top_scores[::-1], color="#16a085", edgecolor="#0e6251", height=0.65)
    ax.set_title("Top 15 TF-IDF Discriminative Features (Unigrams & Bigrams)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Mean TF-IDF Score Across Dataset", fontsize=11)
    ax.set_ylabel("Extracted N-Gram Feature", fontsize=11)
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.002, bar.get_y() + bar.get_height()/2, f"{width:.4f}", va="center", fontsize=9, color="#0e6251")

    ax.set_xlim(0, max(top_scores) * 1.18)
    plt.tight_layout()
    chart3_path = output_dir / "top_tfidf_features.png"
    fig.savefig(chart3_path, dpi=300)
    plt.close(fig)
    print(f"      Saved: {chart3_path.name}")

    # -------------------------------------------------------------------------
    # Chart 4: Train / Test Split Breakdown (Donut Chart)
    # -------------------------------------------------------------------------
    print("[4/6] Visualizing Train/Test Split...")
    X_train, X_test, y_train, y_test = train_test_split(
        df["command"], df["intent"], test_size=0.2, random_state=42, stratify=df["intent"]
    )

    fig, ax = plt.subplots(figsize=(7, 7))
    sizes = [len(X_train), len(X_test)]
    labels = [f"Training Set (80%)\n{len(X_train)} samples", f"Testing Set (20%)\n{len(X_test)} samples"]
    colors = ["#2980b9", "#e67e22"]

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        pctdistance=0.75,
        textprops=dict(color="#2c3e50", fontweight="bold", fontsize=11),
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2),
    )
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontsize(12)

    ax.set_title("NUVI ML Dataset Stratified 80/20 Train-Test Partition", fontsize=13, fontweight="bold")
    plt.tight_layout()
    chart4_path = output_dir / "train_test_split.png"
    fig.savefig(chart4_path, dpi=300)
    plt.close(fig)
    print(f"      Saved: {chart4_path.name}")

    # -------------------------------------------------------------------------
    # Model Training & Evaluation for Charts 5 & 6
    # -------------------------------------------------------------------------
    print("Training Logistic Regression model for evaluation visualization...")
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    clf = LogisticRegression(max_iter=1000, random_state=42, C=5.0, solver="lbfgs")
    clf.fit(X_train_tfidf, y_train)
    y_pred = clf.predict(X_test_tfidf)
    classes = list(clf.classes_)

    # -------------------------------------------------------------------------
    # Chart 5: Confusion Matrix Heatmap
    # -------------------------------------------------------------------------
    print("[5/6] Generating confusion matrix heatmap...")
    cm = confusion_matrix(y_test, y_pred, labels=classes)

    fig, ax = plt.subplots(figsize=(9, 7))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.ax.set_ylabel("Sample Count", rotation=-90, va="bottom", fontsize=10)

    ax.set_xticks(np.arange(len(classes)))
    ax.set_yticks(np.arange(len(classes)))
    ax.set_xticklabels(classes, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(classes, fontsize=9)
    ax.set_title("Confusion Matrix Heatmap - NUVI Intent Classification", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Predicted Intent Class", fontsize=11, labelpad=10)
    ax.set_ylabel("True Ground-Truth Intent Class", fontsize=11)

    # Annotate cells with values
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            color = "white" if val > thresh else "black"
            ax.text(j, i, str(val), ha="center", va="center", color=color, fontweight="bold", fontsize=11)

    plt.tight_layout()
    chart5_path = output_dir / "confusion_matrix_heatmap.png"
    fig.savefig(chart5_path, dpi=300)
    plt.close(fig)
    print(f"      Saved: {chart5_path.name}")

    # -------------------------------------------------------------------------
    # Chart 6: Per-Class Evaluation Metrics (Precision, Recall, F1-Score)
    # -------------------------------------------------------------------------
    print("[6/6] Generating per-class evaluation metrics bar chart...")
    report_dict = classification_report(y_test, y_pred, labels=classes, output_dict=True, zero_division=0)
    
    precisions = [report_dict[c]["precision"] for c in classes]
    recalls = [report_dict[c]["recall"] for c in classes]
    f1_scores = [report_dict[c]["f1-score"] for c in classes]

    x = np.arange(len(classes))
    width = 0.25

    fig, ax = plt.subplots(figsize=(11, 6))
    rects1 = ax.bar(x - width, precisions, width, label="Precision", color="#2980b9")
    rects2 = ax.bar(x, recalls, width, label="Recall", color="#2ecc71")
    rects3 = ax.bar(x + width, f1_scores, width, label="F1-Score", color="#e74c3c")

    ax.set_title("Per-Class Machine Learning Evaluation Metrics", fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(classes, rotation=40, ha="right", fontsize=9)
    ax.set_ylabel("Score (0.0 to 1.0)", fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.axhline(1.0, color="#7f8c8d", linestyle="--", linewidth=0.8)
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.6)

    plt.tight_layout()
    chart6_path = output_dir / "per_class_metrics.png"
    fig.savefig(chart6_path, dpi=300)
    plt.close(fig)
    print(f"      Saved: {chart6_path.name}")

    print("==================================================")
    print("All 6 visualization assets successfully generated in:")
    print(f" -> {output_dir}")
    print("==================================================")


if __name__ == "__main__":
    generate_all_visualizations()
