"""
=============================================================================
NUVI - Matplotlib Data Visualization Module
=============================================================================
Academic Context (AI & Machine Learning Syllabus):
Data Visualization is a core component of Exploratory Data Analysis (EDA).
Visualizing distributions and relationships helps identify:
1. Skewness and central tendencies (Histograms)
2. Category comparisons and rankings (Bar Charts)
3. Trends and continuous progressions (Line Charts)

This module generates lightweight, focused charts using Matplotlib without
relying on heavy dashboard frameworks, keeping it ideal for student vivas.
=============================================================================
"""

import os
from pathlib import Path
from typing import Optional, Tuple
import matplotlib
# Use TkAgg or default GUI backend so plt.show() works smoothly on Windows desktop
try:
    matplotlib.use("TkAgg")
except Exception:
    pass
import matplotlib.pyplot as plt
import pandas as pd


def plot_dataset(
    filepath: str,
    plot_type: str = "auto",
    column: Optional[str] = None,
    output_image: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Generates a clear, academic Matplotlib plot for a dataset.

    Supported plot types:
    - 'hist' / 'histogram': Frequency distribution of a numerical column.
    - 'bar' / 'bar_chart': Category comparison or discrete frequencies.
    - 'line' / 'line_chart': Trend or sequential value progression.
    - 'auto': Automatically chooses the best plot type based on data.

    Returns:
        Tuple[str, str]: (Status message, Absolute path of saved chart image)
    """
    path = Path(filepath)
    if not path.exists():
        return f"File not found: {filepath}", ""

    try:
        df = pd.read_csv(path)
    except Exception as e:
        return f"Failed to read CSV for plotting: {e}", ""

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        return f"No numerical columns found in '{path.name}' to visualize.", ""

    # Choose column
    target_col = column
    if not target_col or target_col not in df.columns:
        # Prefer non-ID numeric columns if available (e.g. Marks, Scores, Sales)
        data_cols = [c for c in numeric_cols if not c.lower().endswith("id") and c.lower() != "index"]
        target_col = data_cols[0] if data_cols else numeric_cols[0]

    # Handle plot type determination
    plot_type = plot_type.lower().strip()
    if plot_type in ["auto", ""]:
        if len(df) <= 20:
            plot_type = "bar"
        else:
            plot_type = "hist"

    fig, ax = plt.subplots(figsize=(8, 5))

    col_data = df[target_col].dropna()

    if plot_type in ["hist", "histogram", "distribution"]:
        ax.hist(col_data, bins=min(15, max(5, len(col_data) // 3)), color="#3498db", edgecolor="#2980b9", alpha=0.85)
        ax.set_title(f"Histogram: Distribution of {target_col}", fontsize=13, fontweight="bold")
        ax.set_xlabel(target_col, fontsize=11)
        ax.set_ylabel("Frequency", fontsize=11)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

    elif plot_type in ["bar", "bar_chart"]:
        # If there is a categorical/text column, use it as labels
        cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
        if cat_cols:
            label_col = cat_cols[0]
            labels = df[label_col].astype(str).head(15)
            values = df[target_col].head(15)
            ax.bar(labels, values, color="#2ecc71", edgecolor="#27ae60", alpha=0.85)
            ax.set_xlabel(label_col, fontsize=11)
            plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
        else:
            sample_df = df[target_col].head(15)
            ax.bar([f"Row {i+1}" for i in range(len(sample_df))], sample_df, color="#2ecc71", alpha=0.85)
            plt.setp(ax.get_xticklabels(), rotation=35, ha="right")

        ax.set_title(f"Bar Chart of {target_col}", fontsize=13, fontweight="bold")
        ax.set_ylabel(target_col, fontsize=11)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

    elif plot_type in ["line", "line_chart", "trend"]:
        ax.plot(col_data.values, marker="o", color="#e74c3c", linewidth=2, markersize=4)
        ax.set_title(f"Line Plot: {target_col} Sequence", fontsize=13, fontweight="bold")
        ax.set_xlabel("Sample Index", fontsize=11)
        ax.set_ylabel(target_col, fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.7)

    else:
        # Fallback default: Histogram
        ax.hist(col_data, bins=10, color="#9b59b6", edgecolor="#8e44ad", alpha=0.85)
        ax.set_title(f"Distribution of {target_col}", fontsize=13, fontweight="bold")
        ax.set_xlabel(target_col, fontsize=11)
        ax.set_ylabel("Count", fontsize=11)

    plt.tight_layout()

    # Save output image
    if output_image:
        out_path = Path(output_image)
    else:
        charts_dir = path.parent
        out_path = charts_dir / f"chart_{path.stem}_{target_col}_{plot_type}.png"

    fig.savefig(out_path, dpi=120)
    plt.close(fig)

    msg = f"Generated {plot_type.capitalize()} for '{target_col}' in '{path.name}'. Saved to {out_path.name}."
    return msg, str(out_path.resolve())
