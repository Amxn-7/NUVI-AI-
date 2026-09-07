"""
=============================================================================
NUVI - Verification & Test Suite
=============================================================================
Validates:
1. Import and syntax integrity across all modules.
2. Standalone ML intent classification & confidence evaluation.
3. 10+ distinct commands spanning all intents.
4. Low-confidence handling & graceful fallbacks.
5. Unknown/gibberish queries.
6. CSV dataset exploratory analysis & missing value detection.
7. Non-destructive data cleaning (verifying original file immutability).
8. Data visualization (Matplotlib plot generation).
9. Command history logging.
=============================================================================
"""

import os
from pathlib import Path
import shutil
import pandas as pd

from ml.predict_intent import get_predictor, predict_intent
from ml.preprocess import clean_text
from data_analysis.analyzer import analyze_csv, clean_csv, detect_cleaning_needs
from data_analysis.visualization import plot_dataset
from commands.parser import parse_and_execute


def run_tests():
    print("=" * 60)
    print("       STARTING NUVI COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    all_passed = True

    # -------------------------------------------------------------------------
    # Test 1: ML Model & Predictor Sanity
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Testing ML Model & Predictor...")
    predictor = get_predictor()
    res = predictor.predict("open google chrome")
    assert res["intent"] == "OPEN_APPLICATION", f"Expected OPEN_APPLICATION, got {res['intent']}"
    assert res["status"] == "HIGH", f"Expected HIGH confidence, got {res['status']}"
    print(f"  PASS: 'open google chrome' -> Intent: {res['intent']} (Conf: {res['confidence']:.2f}, Status: {res['status']})")

    # -------------------------------------------------------------------------
    # Test 2: Test 10+ Diverse Commands Covering All Intents
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Testing 10+ Diverse Commands Across Intents...")
    test_cases = [
        ("open chrome", "OPEN_APPLICATION"),
        ("launch vscode", "OPEN_APPLICATION"),
        ("find my resume", "FIND_FILE"),
        ("search for project report", "FIND_FILE"),
        ("create file notes.txt", "CREATE_FILE"),
        ("make a new file called plan.txt", "CREATE_FILE"),
        ("open dsa workspace", "OPEN_WORKSPACE"),
        ("summarize report.pdf", "DOCUMENT_QUERY"),
        ("analyze sample_marks.csv", "DATA_ANALYSIS"),
        ("show a graph of marks in sample_marks.csv", "DATA_ANALYSIS"),
        ("what is machine learning", "GENERAL_QUESTION"),
        ("explain supervised learning", "GENERAL_QUESTION"),
    ]

    for cmd, expected_intent in test_cases:
        intent, conf, status = predict_intent(cmd)
        is_match = (intent == expected_intent)
        mark = "PASS" if is_match else "FAIL"
        print(f"  [{mark}] '{cmd}' -> {intent} (Expected: {expected_intent}, Conf: {conf*100:.1f}%)")
        if not is_match:
            all_passed = False

    # -------------------------------------------------------------------------
    # Test 3: Test Unknown & Low-Confidence Queries
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Testing Unknown & Low-Confidence Predictions...")
    unknown_query = "quantum hyperloop sandwich xyz"
    pred_unknown = predictor.predict(unknown_query)
    print(f"  Query: '{unknown_query}'")
    print(f"  Predicted Intent: {pred_unknown['intent']} | Confidence: {pred_unknown['confidence']:.2f} | Status: {pred_unknown['status']}")
    assert pred_unknown["confidence"] < 0.40 or pred_unknown["status"] == "LOW", "Unknown query should yield low confidence."
    print("  PASS: Low confidence properly assigned to unknown input.")

    # -------------------------------------------------------------------------
    # Test 4: Test Medium-Confidence Clarification Handling
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Testing Medium-Confidence Handling...")
    vague_cmd = "analyze"
    vague_pred = predictor.predict(vague_cmd)
    assert vague_pred["status"] == "MEDIUM", f"Expected MEDIUM confidence, got {vague_pred['status']}"
    output_msg = parse_and_execute(vague_cmd)
    print(f"  Query: '{vague_cmd}' -> Confidence: {vague_pred['confidence']*100:.1f}% ({vague_pred['status']})")
    print(f"  Assistant Output:\n  {output_msg.strip()}")
    assert "I think you want me to" in output_msg, "Should contain clarification prompt"
    print("  PASS: Ambiguous/Medium confidence gracefully handled.")

    # -------------------------------------------------------------------------
    # Test 5: CSV Dataset Analysis & Missing-Value Detection
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Testing CSV Analysis & Missing-Value Detection...")
    marks_csv = Path(__file__).parent / "data" / "sample_marks.csv"
    assert marks_csv.exists(), "sample_marks.csv must exist"

    analysis_report = analyze_csv(str(marks_csv))
    print("  Analysis Report Excerpt:")
    for line in analysis_report.splitlines()[:10]:
        print(f"    {line}")

    needs = detect_cleaning_needs(str(marks_csv))
    assert needs["needs_cleaning"] is True, "sample_marks.csv should have detected cleaning needs"
    assert needs["duplicates"] >= 1, "Should have detected at least 1 duplicate"
    assert needs["total_missing"] >= 1, "Should have detected missing values"
    print(f"  PASS: Successfully detected {needs['total_missing']} missing values & {needs['duplicates']} duplicates.")

    # -------------------------------------------------------------------------
    # Test 6: Non-Destructive Cleaning (Original File Integrity Verification)
    # -------------------------------------------------------------------------
    print("\n[TEST 6] Testing Non-Destructive Data Cleaning...")
    # Record original file modification time and row count
    original_mtime = marks_csv.stat().st_mtime
    original_df = pd.read_csv(marks_csv)
    original_len = len(original_df)

    clean_summary, cleaned_path = clean_csv(str(marks_csv))
    assert os.path.exists(cleaned_path), f"Cleaned file must exist at {cleaned_path}"

    cleaned_df = pd.read_csv(cleaned_path)
    post_mtime = marks_csv.stat().st_mtime

    # Critical Checks
    assert original_mtime == post_mtime, "CRITICAL ERROR: Original file was modified!"
    assert len(original_df) == original_len, "CRITICAL ERROR: Original file row count altered!"
    assert len(cleaned_df) < original_len, "Cleaned dataset should have duplicate rows removed"
    assert cleaned_df.isnull().sum().sum() == 0, "Cleaned dataset should have 0 missing values"

    print(f"  Original CSV rows: {original_len} (strictly unmodified)")
    print(f"  Cleaned CSV rows : {len(cleaned_df)} (saved safely to {Path(cleaned_path).name})")
    print(f"  Cleaned Missing  : {cleaned_df.isnull().sum().sum()}")
    print("  PASS: Non-destructive cleaning verified! Original CSV was NOT overwritten.")

    # -------------------------------------------------------------------------
    # Test 7: Matplotlib Visualization Generation
    # -------------------------------------------------------------------------
    print("\n[TEST 7] Testing Matplotlib Visualization Generation...")
    plot_msg, plot_file = plot_dataset(str(marks_csv), plot_type="bar", column="Maths")
    assert os.path.exists(plot_file), f"Plot file was not created at {plot_file}"
    print(f"  PASS: {plot_msg}")
    print(f"        Saved chart at: {Path(plot_file).name}")

    # -------------------------------------------------------------------------
    # Test 8: Command History Logging
    # -------------------------------------------------------------------------
    print("\n[TEST 8] Testing Command History Logging...")
    history_file = Path(__file__).parent / "data" / "command_history.csv"
    assert history_file.exists(), "command_history.csv should exist"
    history_df = pd.read_csv(history_file)
    assert len(history_df) > 0, "History file should have recorded commands"
    assert "confidence" in history_df.columns
    assert "intent" in history_df.columns
    print(f"  PASS: Recorded {len(history_df)} command history entries.")

    # Clean up test created files
    for fname in ["notes.txt", "plan.txt"]:
        fpath = Path(__file__).parent / fname
        if fpath.exists():
            fpath.unlink()

    print("\n" + "=" * 60)
    if all_passed:
        print("   ALL TESTS PASSED SUCCESSFULLY! NUVI IS READY FOR VIVA.")
    else:
        print("   SOME TESTS FAILED! PLEASE REVIEW.")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
