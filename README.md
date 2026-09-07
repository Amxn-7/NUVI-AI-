# NUVI – Intelligent AI Desktop Assistant

NUVI is an intelligent, Python-based Desktop Assistant that pairs a transparent, interactive desktop pet interface with a **Supervised Machine Learning Intent Recognition** pipeline and **Exploratory Data Analysis** capabilities. Designed to align with college Artificial Intelligence and Machine Learning curricula, NUVI demonstrates key principles of Intelligent Agents, Natural Language Processing, Supervised Classification, and Data Science without unnecessary complexity.

---

## 1. Project Overview

NUVI operates as an autonomous agent on Windows desktop environments. Instead of blindly executing commands via brittle keyword matching, NUVI perceives spoken or typed inputs, normalizes and vectorizes natural language into numerical features via **TF-IDF**, predicts the underlying user intent using a **Logistic Regression** classifier, evaluates prediction confidence, and routes actions to appropriate OS actuators (launching apps, searching files, generating documents, analyzing tabular data, or providing educational explanations).

---

## 2. System Features

### Existing Preserved Features
- **Transparent Desktop Pet Interface**: Floating animated desktop pet with event-based reactions (greeting, listening, thinking, success, error) and draggable position.
- **Voice & Speech Recognition (2 Clicks)**: Double-click the pet to trigger microphone input with Google Speech-to-Text transcription.
- **Two-Way Text Chatbox (3 Clicks)**: Triple-click the pet to open an interactive floating chat window to chat with the Gemini AI, ask questions, or execute desktop commands directly via text.
- **Application Launcher**: Native launching of desktop applications (e.g., `open chrome`, `launch vscode`, `start notepad`).
- **Configurable Workspaces**: Launch multi-application environments configured in `config/workspaces.json` (e.g., LeetCode, DSA, Dev).
- **Local File Search**: Fast directory search for user documents (e.g., `find resume`, `search project report`).
- **File Creation**: Instant creation of text and code files (e.g., `create notes.txt`, `make todo.txt`).
- **AI Document Q&A & Writer**: OpenRouter LLM integration for open-ended document summarization and text composition.

### New Machine Learning & Data Science Features
- **Supervised ML Intent Classification**: 7-class intent recognition using scikit-learn.
- **Confidence Engine**: Decision thresholds for safe execution ($\ge 70\%$), active clarification ($40\% - 69\%$), and low-confidence conversational fallback ($< 40\%$).
- **Audit History Logging**: Real-time logging of user queries, predicted intent, confidence score, and timestamp into `data/command_history.csv`.
- **Exploratory Data Analysis (EDA)**: Automatic reporting of rows, columns, data types, missing values, duplicate counts, and numerical 5-number statistics via Pandas.
- **Non-Destructive Data Cleaning**: Safe dataset cleaning that creates a `cleaned_<filename>.csv` copy without ever modifying or overwriting the original dataset.
- **Matplotlib Visualization**: Generation of histograms, bar charts, and line plots for numerical columns.
- **Interactive Floating Answer Card**: Persistent, scrollable, and copyable card matching pet theme for viewing detailed Q&A answers.
- **Academic CLI Mode**: `--cli` flag allowing text-based testing and viva demonstration in terminal environments.

---

## 3. AI Agent Architecture

NUVI is architected as an **Intelligent Agent** that perceives its environment through sensors, decides on actions using an internal ML model and decision layer, and interacts with the operating system via actuators.

```
                    ┌─────────────────────────┐
                    │          USER           │
                    └────────────┬────────────┘
                                 │ Voice / Text
                                 ▼
                    ┌─────────────────────────┐
                    │    PERCEPTION / SENSORS │
                    │ (Microphone / Keyboard) │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    TEXT PREPROCESSING   │
                    │  (Lowercase, Strip,     │
                    │   Punctuation Normal.)  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  TF-IDF VECTORIZATION   │
                    │ (Numerical Matrix X)    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ ML INTENT CLASSIFIER    │
                    │  (Logistic Regression)  │
                    └────────────┬────────────┘
                                 │ Intent + P(Intent|X)
                                 ▼
                    ┌─────────────────────────┐
                    │     DECISION LAYER      │
                    │  (Confidence Threshold) │
                    └──────┬─────┬─────┬──────┘
       High (≥70%)         │     │     │ Low (<40%)
   ┌───────────────────────┘     │     └────────────────────────┐
   ▼                             ▼                              ▼
┌──────────────┐     ┌───────────────────────┐       ┌────────────────────┐
│  ACTUATORS   │     │  MEDIUM (40% - 69%)   │       │  GENERAL QUESTION  │
│ - Launch App │     │  Active Clarification │       │  (Offline Knowledge│
│ - Find File  │     │  "I think you want... │       │   or OpenRouter)   │
│ - Create File│     │   Should I proceed?"  │       └────────────────────┘
│ - Workspace  │     └───────────────────────┘
│ - Analyze CSV│
│ - Plot Graph │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                 DESKTOP COMPUTER ENVIRONMENT                │
│       (Filesystem, Running Apps, Datasets, Shell)           │
└──────────────────────────────┬──────────────────────────────┘
                               │ Feedback
                               ▼
                    ┌─────────────────────────┐
                    │   USER RESPONSE / UI    │
                    │ (Speech Bubble / Speech)│
                    └─────────────────────────┘
```

---

## 4. PEAS Representation

In Classical Artificial Intelligence, rational agents are formally characterized by their **PEAS** description:

| Component | Description in NUVI |
| :--- | :--- |
| **P – Performance Measure** | High command classification accuracy ($\ge 95\%$), correct actuator dispatch, low false-action rate via confidence thresholding, and sub-second execution response. |
| **E – Environment** | Windows desktop operating system, file system (PDFs, CSVs, text documents), running application processes, network/web browser. |
| **A – Actuators** | Windows process launcher (`os.startfile`, `subprocess`), file creator, file system search scanner, Matplotlib plotting engine, Pandas CSV cleaning engine, GUI pet speech bubbles. |
| **S – Sensors** | Microphone (voice audio captured via SpeechRecognition), keyboard text input (Tkinter entry or CLI terminal), local file system state. |

---

## 5. Machine Learning Workflow & Pipeline

The intent recognition subsystem follows the standard supervised machine learning lifecycle:

```
[Raw Dataset] ➔ [Preprocessing] ➔ [80/20 Train-Test Split] ➔ [TF-IDF Vectorization] ➔ [Logistic Regression] ➔ [Evaluation & Persistence]
```

### 1. Dataset (`data/commands.csv`)
A curated dataset containing over 230 realistic command examples across 7 distinct intent classes:
1. `OPEN_APPLICATION`: Commands to launch applications.
2. `FIND_FILE`: Commands to locate documents and files.
3. `CREATE_FILE`: Commands to create new files and scripts.
4. `OPEN_WORKSPACE`: Commands to open specialized multi-app environments.
5. `DOCUMENT_QUERY`: Commands to read and summarize PDFs, text files, etc.
6. `DATA_ANALYSIS`: Commands to inspect, clean, or visualize CSV datasets.
7. `GENERAL_QUESTION`: Conceptual AI/ML questions and conversational greetings.

### 2. Text Preprocessing (`ml/preprocess.py`)
- Converts all text to lowercase.
- Normalizes punctuation to prevent token concatenation (e.g., `report.pdf` $\rightarrow$ `report pdf`).
- Strips redundant whitespaces and removes duplicate entries to avoid train/test contamination.

### 3. Feature Extraction (TF-IDF)
Traditional machine learning algorithms cannot directly ingest raw strings. They require vectors in $\mathbb{R}^n$.
- **TF (Term Frequency)**: Measures how frequently term $t$ appears in a command $d$.
- **IDF (Inverse Document Frequency)**: Down-weights omnipresent filler words and amplifies discriminative tokens (e.g., `chrome`, `resume`, `dataset`):
$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\left(\frac{|D|}{1 + |\{d \in D : t \in d\}|}\right)$$
- NUVI uses unigrams and bigrams (`ngram_range=(1, 2)`) to capture compound phrases like "open chrome" or "machine learning".

### 4. Train / Test Split
- **80% Training Set** (185 samples): Used to optimize model weights.
- **20% Testing Set** (47 samples): Kept strictly unseen during training to evaluate real-world generalization.
- Stratified sampling preserves proportional representation of every class.
- Fixed `random_state=42` ensures exact scientific reproducibility.

### 5. Logistic Regression Classifier
Logistic Regression is a foundational linear model for classification. For multiclass intent classification, the algorithm fits hyperplanes separating each class in the TF-IDF feature space and applies the Softmax function to compute well-calibrated class probabilities:
$$P(y = k \mid \mathbf{x}) = \frac{e^{\mathbf{w}_k^T \mathbf{x} + b_k}}{\sum_{j=1}^{K} e^{\mathbf{w}_j^T \mathbf{x} + b_j}}$$

### 6. Model Persistence (`models/`)
The trained model (`intent_classifier.pkl`) and TF-IDF vectorizer (`tfidf_vectorizer.pkl`) are serialized using `joblib`. NUVI loads these in-memory artifacts at startup, enabling instantaneous sub-millisecond inference without retraining.

---

## 6. Model Evaluation Results

Evaluation is performed strictly on the unseen 20% test dataset:

```text
==================================================
NUVI Intent Classifier Evaluation Report
==================================================
Testing Samples Evaluated: 47
Accuracy: 97.87%

Classification Report:
                  precision    recall  f1-score   support

     CREATE_FILE       1.00      1.00      1.00         7
   DATA_ANALYSIS       1.00      1.00      1.00         6
  DOCUMENT_QUERY       1.00      0.83      0.91         6
       FIND_FILE       1.00      1.00      1.00         7
GENERAL_QUESTION       0.88      1.00      0.93         7
OPEN_APPLICATION       1.00      1.00      1.00         8
  OPEN_WORKSPACE       1.00      1.00      1.00         6

        accuracy                           0.98        47
       macro avg       0.98      0.98      0.98        47
    weighted avg       0.98      0.98      0.98        47
```

### Confusion Matrix
The script automatically exports a visual heatmap to `data/confusion_matrix.png`:

```text
Actual \ Pred         CREATE_F  DATA_ANA  DOCUMENT  FIND_FIL  GENERAL_  OPEN_APP  OPEN_WOR
------------------------------------------------------------------------------------------
CREATE_FILE                  7         0         0         0         0         0         0
DATA_ANALYSIS                0         6         0         0         0         0         0
DOCUMENT_QUERY               0         0         5         0         1         0         0
FIND_FILE                    0         0         0         7         0         0         0
GENERAL_QUESTION             0         0         0         0         7         0         0
OPEN_APPLICATION             0         0         0         0         0         8         0
OPEN_WORKSPACE               0         0         0         0         0         0         6
```

---

## 7. Data Analysis & Non-Destructive Cleaning

NUVI incorporates standard Pandas data analysis tools:

### Dataset Inspection
Command: `analyze sample_marks.csv`
- Displays row/column dimensions.
- Lists data types and null value counts per column.
- Detects duplicate rows.
- Computes mean, median, min, and max for all numerical attributes.

### Non-Destructive Cleaning
Command: `clean sample_marks.csv`
- Deduplicates rows.
- Performs median imputation for missing numerical features and mode imputation for categorical attributes.
- **Safety Guarantee**: The original dataset is **never** modified or overwritten. A new sanitized file is generated (e.g., `cleaned_sample_marks.csv`).

### Matplotlib Plotting
Command: `show a graph of maths in sample_marks.csv`
- Generates Bar Charts, Histograms, or Line Plots.
- Automatically handles axis labels, grids, and formatting.
- Saves generated plots to image files (e.g. `chart_sample_marks_Maths_bar.png`).

---

## 8. Installation & Setup

### 1. Prerequisites
- Python 3.10+ installed on Windows.

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. (Optional) OpenRouter Configuration
To enable open-ended generative writing and document Q&A:
```powershell
$env:OPENROUTER_API_KEY="your_api_key_here"
```
*(Note: NUVI functions completely offline for all ML classification, application launching, file management, data analysis, and core syllabus questions even if an API key is not provided).*

---

## 9. How to Train and Run NUVI

### Train the ML Model
```powershell
python -m ml.train_model
```
*Trains the TF-IDF vectorizer and Logistic Regression classifier, outputting `.pkl` artifacts to `models/`.*

### Evaluate the ML Model
```powershell
python -m ml.evaluate_model
```
*Evaluates the model on unseen test data, prints precision/recall/F1 metrics, and creates `data/confusion_matrix.png`.*

### Run Comprehensive Automated Verification
```powershell
python test_nuvi.py
```
*Runs the full 8-point verification test suite.*

### Run NUVI Desktop Pet (GUI Mode)
```powershell
python main.py
```
*The animated pet appears in the bottom-right corner. Drag to move, double-click to speak!*

### Run NUVI in Academic CLI Mode (Ideal for Vivas)
```powershell
python main.py --cli
```
*Interactive terminal prompt allowing quick demonstration of commands without GUI dependencies.*

---

## 10. Example Commands for Demonstration

| Category | Example Command | Expected Intent & Action |
| :--- | :--- | :--- |
| **App Launching** | `open chrome` | `OPEN_APPLICATION` $\rightarrow$ Launches Google Chrome |
| **App Launching** | `launch vscode` | `OPEN_APPLICATION` $\rightarrow$ Launches Visual Studio Code |
| **File Search** | `find my resume` | `FIND_FILE` $\rightarrow$ Scans user directory and prints matches |
| **File Creation** | `create notes.txt` | `CREATE_FILE` $\rightarrow$ Generates new empty file `notes.txt` |
| **Workspaces** | `open dsa workspace` | `OPEN_WORKSPACE` $\rightarrow$ Launches LeetCode in browser + code editor |
| **Data Analysis** | `analyze sample_marks.csv` | `DATA_ANALYSIS` $\rightarrow$ Outputs EDA report (rows, missing, stats) |
| **Data Visualization**| `show a graph of marks in sample_marks.csv` | `DATA_ANALYSIS` $\rightarrow$ Renders Matplotlib bar/distribution plot |
| **Data Cleaning** | `clean sample_marks.csv` | `DATA_ANALYSIS` $\rightarrow$ Generates `cleaned_sample_marks.csv` safely |
| **Syllabus Q&A** | `what is supervised learning` | `GENERAL_QUESTION` $\rightarrow$ Explains supervised learning concept |
| **Syllabus Q&A** | `explain tf idf in nlp` | `GENERAL_QUESTION` $\rightarrow$ Explains Term Frequency - Inverse Document Frequency |
| **Clarification** | `analyze` | *Medium Confidence ($53\%$)* $\rightarrow$ Asks user for clarification |
| **Unknown Query** | `quantum xyz 999` | *Low Confidence ($<40\%$)* $\rightarrow$ Graceful fallback response |

---

## 11. Project Directory Structure

```text
DesktopAssistant/
├── main.py                     # Main application entry (supports GUI pet & --cli mode)
├── requirements.txt            # Dependency list
├── README.md                   # Complete academic documentation
├── test_nuvi.py                # Automated test and verification suite
│
├── config/
│   └── workspaces.json         # Workspace URLs and apps configuration
│
├── data/
│   ├── commands.csv            # 230+ labeled command training dataset
│   ├── test_commands.csv       # Unseen 20% test partition for evaluation
│   ├── command_history.csv     # Runtime audit log (query, intent, confidence, time)
│   ├── sample_marks.csv        # Sample student dataset with missing/duplicate entries
│   └── confusion_matrix.png    # Visual confusion matrix generated by evaluation
│
├── ml/
│   ├── __init__.py
│   ├── preprocess.py           # Text normalization and cleaning functions
│   ├── train_model.py          # End-to-end training pipeline & 80/20 train-test split
│   ├── evaluate_model.py       # Metrics: Accuracy, Precision, Recall, F1, Confusion Matrix
│   └── predict_intent.py       # Runtime inference with confidence thresholding
│
├── models/
│   ├── intent_classifier.pkl   # Serialized Logistic Regression model
│   └── tfidf_vectorizer.pkl    # Serialized TF-IDF feature extractor
│
├── data_analysis/
│   ├── __init__.py
│   ├── analyzer.py             # Pandas EDA and non-destructive CSV cleaner
│   └── visualization.py        # Matplotlib plotting (Histogram, Bar, Line)
│
├── commands/
│   ├── parser.py               # Central routing layer connecting ML to actuators
│   ├── launcher.py             # Application launcher actuator
│   ├── search.py               # Local file search actuator
│   ├── workspace.py            # Workspace orchestrator actuator
│   ├── ai_writer.py            # OpenRouter text writer actuator
│   ├── rag.py                  # Document question-answering actuator
│   └── llm.py                  # OpenRouter API client wrapper
│
└── ui/
    ├── widget.py               # Transparent desktop pet Tkinter GUI
    └── voice.py                # Speech recognition microphone wrapper
```

---

## 12. College Viva & AI/ML Syllabus Alignment

When presenting NUVI for a college project evaluation or viva, you can discuss the following syllabus concepts:

1. **Intelligent Agents & PEAS**: How NUVI maps to the standard Russell & Norvig definition of a goal-based agent acting in a software environment.
2. **Supervised Learning**: Mapping inputs $X$ (commands) to discrete classes $y$ (intents) using ground-truth annotations.
3. **Feature Extraction in NLP**: Why mathematical models cannot process ASCII strings directly, and how TF-IDF forms a vector space model with term weighting.
4. **Train / Test Split & Generalization**: Why testing on unseen data is essential to detect overfitting and evaluate real-world performance.
5. **Evaluation Metrics**: Why Accuracy alone can be misleading in imbalanced datasets, and how Precision, Recall, and F1-Score provide a complete performance picture.
6. **Exploratory Data Analysis (EDA)**: The role of Pandas in assessing data distribution and data cleanliness.
7. **Safe Data Cleaning**: Handling missing values via median/mode imputation and the principle of preserving raw source data integrity.
8. **Uncertainty & Confidence Thresholds**: How probability estimation ($P(\text{Intent} \mid \text{Input})$) enables an agent to distinguish between certain commands and ambiguous inputs, asking for clarification when appropriate.
