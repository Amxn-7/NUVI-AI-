"""
=============================================================================
NUVI - Dataset Analysis and Safe Data Cleaning Module
=============================================================================
Academic Context (AI & Machine Learning Syllabus):
1. Exploratory Data Analysis (EDA):
   Before building or deploying models, data scientists must inspect the 
   structural properties of raw datasets: shape (rows, columns), data types,
   and distributions.

2. Data Quality & Data Cleaning:
   Real-world data often suffers from noise, duplicates, and missing values (NaN).
   - Duplicate rows bias statistical summaries and cause data leakage.
   - Missing values can crash linear algebra solvers and distort estimates.
   
3. Imputation Strategies:
   - Median Imputation: Preferred for skewed numerical data as it is robust to outliers.
   - Mode Imputation / Constant: Suitable for categorical features.

4. Non-Destructive Integrity Principle:
   Original datasets must NEVER be mutated or overwritten. Cleaned data is saved 
   as a separate entity (`cleaned_<filename>.csv`) to maintain data provenance.
=============================================================================
"""

import os
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd


def analyze_csv(filepath: str) -> str:
    """
    Performs comprehensive basic exploratory data analysis on a CSV file using pandas.

    Returns:
        str: Formatted text report describing rows, columns, types, missing values,
             duplicates, and 5-number numerical summary.
    """
    path = Path(filepath)
    if not path.exists():
        return f"Dataset not found: {filepath}"

    if path.suffix.lower() != ".csv":
        return f"File '{path.name}' is not a CSV. Please provide a .csv file."

    try:
        df = pd.read_csv(path)
    except Exception as e:
        return f"Failed to read CSV '{path.name}': {e}"

    num_rows, num_cols = df.shape
    duplicate_count = int(df.duplicated().sum())

    # Missing values count per column
    missing_series = df.isnull().sum()
    columns_with_missing = {col: int(count) for col, count in missing_series.items() if count > 0}
    total_missing = int(missing_series.sum())

    # Build formatted report
    lines = [
        "Dataset Analysis",
        "----------------",
        f"File: {path.name}",
        f"Rows: {num_rows} | Columns: {num_cols}",
        f"Duplicate Rows: {duplicate_count}",
        "",
        "Columns & Data Types:",
    ]

    for col in df.columns:
        dtype_str = str(df[col].dtype)
        lines.append(f"  - {col} ({dtype_str})")

    lines.append("")
    lines.append("Missing Values:")
    if columns_with_missing:
        for col, count in columns_with_missing.items():
            lines.append(f"  {col}: {count}")
    else:
        lines.append("  None (Dataset has no missing values)")

    # Numerical statistics summary
    numeric_df = df.select_dtypes(include=["number"])
    if not numeric_df.empty:
        lines.append("")
        lines.append("Numerical Summary (Mean, Median, Min, Max):")
        for col in numeric_df.columns:
            col_mean = numeric_df[col].mean()
            col_median = numeric_df[col].median()
            col_min = numeric_df[col].min()
            col_max = numeric_df[col].max()
            lines.append(f"  {col}:")
            lines.append(f"    Mean={col_mean:.2f}, Median={col_median:.2f}, Min={col_min:.2f}, Max={col_max:.2f}")

    # Helpful prompt if cleaning is recommended
    if duplicate_count > 0 or total_missing > 0:
        lines.append("")
        lines.append(f"[Suggestion] Found {total_missing} missing values & {duplicate_count} duplicates.")
        lines.append(f"To clean safely, run: 'clean {path.name}'")

    return "\n".join(lines)


def detect_cleaning_needs(filepath: str) -> Dict[str, Any]:
    """
    Inspects whether a CSV contains missing values, duplicates, or empty columns.
    """
    path = Path(filepath)
    if not path.exists():
        return {"error": f"File '{filepath}' does not exist."}

    try:
        df = pd.read_csv(path)
    except Exception as e:
        return {"error": str(e)}

    duplicates = int(df.duplicated().sum())
    missing_by_col = {col: int(cnt) for col, cnt in df.isnull().sum().items() if cnt > 0}
    total_missing = sum(missing_by_col.values())
    empty_cols = [col for col in df.columns if df[col].isnull().all()]

    needs_cleaning = duplicates > 0 or total_missing > 0 or len(empty_cols) > 0

    return {
        "filepath": str(path),
        "filename": path.name,
        "needs_cleaning": needs_cleaning,
        "duplicates": duplicates,
        "total_missing": total_missing,
        "missing_by_col": missing_by_col,
        "empty_cols": empty_cols,
    }


def clean_csv(filepath: str, output_path: str = None) -> Tuple[str, str]:
    """
    Performs non-destructive data cleaning on a CSV file.
    - Removes duplicate rows.
    - Imputes missing numerical values with column median.
    - Imputes missing categorical values with mode or 'Unknown'.
    - Drops completely empty columns.
    - NEVER overwrites the original file; saves to a new file prefixed with 'cleaned_'.

    Returns:
        Tuple[str, str]: (Summary message, Path to the newly created cleaned CSV)
    """
    src_path = Path(filepath)
    if not src_path.exists():
        return f"File not found: {filepath}", ""

    if src_path.suffix.lower() != ".csv":
        return f"File '{src_path.name}' is not a CSV.", ""

    try:
        df = pd.read_csv(src_path)
    except Exception as e:
        return f"Failed to read CSV: {e}", ""

    initial_rows = len(df)
    duplicates_removed = int(df.duplicated().sum())

    # Step 1: Remove duplicate rows
    df_clean = df.drop_duplicates().copy()

    # Step 2: Drop completely empty columns
    empty_cols = [col for col in df_clean.columns if df_clean[col].isnull().all()]
    if empty_cols:
        df_clean = df_clean.drop(columns=empty_cols)

    # Step 3: Impute missing values
    missing_fixed_count = 0
    for col in df_clean.columns:
        col_missing = df_clean[col].isnull().sum()
        if col_missing > 0:
            missing_fixed_count += int(col_missing)
            if pd.api.types.is_numeric_dtype(df_clean[col]):
                # Median imputation for numerical features
                median_val = df_clean[col].median()
                df_clean[col] = df_clean[col].fillna(median_val)
            else:
                # Mode imputation for categorical features
                mode_series = df_clean[col].mode()
                fill_val = mode_series[0] if not mode_series.empty else "Unknown"
                df_clean[col] = df_clean[col].fillna(fill_val)

    # Step 4: Determine output destination (NEVER overwrite original)
    if output_path:
        dest_path = Path(output_path)
    else:
        dest_path = src_path.parent / f"cleaned_{src_path.name}"

    # Critical Safety Guarantee: Original file is never overwritten
    if dest_path.resolve() == src_path.resolve():
        dest_path = src_path.parent / f"cleaned_copy_{src_path.name}"

    df_clean.to_csv(dest_path, index=False)

    summary = (
        f"Data Cleaning Complete!\n"
        f"----------------------\n"
        f"Original File : {src_path.name} (preserved, unchanged)\n"
        f"Cleaned File  : {dest_path.name}\n"
        f"Rows Before   : {initial_rows} -> Rows After: {len(df_clean)}\n"
        f"Duplicates Removed: {duplicates_removed}\n"
        f"Missing Values Imputed: {missing_fixed_count}\n"
        f"Empty Columns Dropped: {len(empty_cols)}"
    )

    return summary, str(dest_path)
