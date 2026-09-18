# Intelligent Financial Opportunity Analysis & Recommendation Engine

## 1. Project Overview

The Intelligent Financial Opportunity Analysis & Recommendation Engine is a Python-based system that extracts, normalizes, and ranks financial opportunities based on user queries written in natural language.

The system combines textual similarity with structured financial preference matching to retrieve relevant opportunities from the supplied dataset.

It displays ranked results along with matching reasons and source-document references to help users understand why an opportunity was retrieved.

## 2. Problem Statement

Financial opportunity documents contain information such as minimum investment, tenure, risk category, and expected returns. Comparing multiple documents manually can be time-consuming.

This project aims to automate the extraction and organization of opportunity information and provide a retrieval and ranking mechanism that matches user preferences expressed in natural language.

## 3. Key Features

- Extracts financial opportunity details from the supplied documents.
- Normalizes investment amounts, tenure, and expected-return ranges.
- Processes natural-language queries.
- Identifies preferences such as budget, risk, tenure, and expected returns.
- Combines TF-IDF text similarity with rule-based matching.
- Ranks opportunities using weighted scoring.
- Displays matching reasons and source-document references.
- Evaluates retrieval using Precision@5, Recall@5, and Hit Rate@5.
- Handles queries requesting guaranteed returns with a message explaining that guarantees are not verified.

## 4. Technologies Used

| Technology           | Purpose                                        |
| -------------------- | -----------------------------------------------|
| Python               | Core implementation                            |
| scikit-learn         | TF-IDF and cosine similarity                   |
| Regular Expressions  | Extracting and parsing structured information  |
| JSON                 | Storing normalized opportunity data            |
| Pandas               | Evaluation and result analysis                 |

## 5. Project Structure

```
project/
│
├── data/
│   └── opportunities/
│       └── (supplied opportunity documents)
│
├── labelled_examples.csv
├── normalized_opportunities.json
├── schema.json
├── test_queries.json
│
├── src/
│   ├── extractor.py
│   ├── normalizer.py
│   ├── retrieval.py
│   └── main.py
│
├── tests/
│   └── evaluate.py
│
├── results/
│   └── evaluation_results.txt
│
├── requirements.txt
├── README.md
├── TECHNICAL_NOTE.md
└── .gitignore
```

## 6. How It Works

The system follows these steps:

1. **Extraction**: Reads the supplied opportunity documents and extracts relevant information.
2. **Normalization**: Converts extracted fields into a consistent structured format.
3. **Query processing**: Parses user preferences from natural-language input.
4. **Similarity calculation**: Uses TF-IDF and cosine similarity to measure textual relevance.
5. **Structured matching**: Evaluates budget, risk, tenure, and expected-return preferences.
6. **Ranking**: Combines the component scores using predefined weights.
7. **Output**: Displays ranked opportunities with matching reasons and source references.
8. **Evaluation**: Compares retrieved results against labelled examples.

## 7. Ranking Algorithm

The system uses a hybrid ranking algorithm.

| Component              | Weight   |
| -----------------------| -------- |
| Text similarity        | 0.15     |
| Budget match           | 0.25     |
| Risk compatibility     | 0.25     |
| Tenure match           | 0.20     |
| Expected-return match  | 0.15     |
| **Total**              | **1.00** |

The final score is calculated as:

```
S = 0.15T + 0.25B + 0.25R + 0.20N + 0.15E
```

Where T, B, R, N, and E represent the respective component scores.

The weights are predefined design choices and have not been learned from training data.

## 8. Installation

### Prerequisites

- Python 3.10 or later recommended
- pip
- The supplied assessment dataset

### Setup

1. Extract or copy the project folder to your local machine, then navigate into it:

   ```bash
   cd <project-folder>
   ```

2. (Recommended) Create and activate a virtual environment:

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Ensure the supplied opportunity documents and required dataset files are placed in the expected project directories (see Section 5, Project Structure):

   - Opportunity documents → `data/opportunities/`
   - `labelled_examples.csv`, `schema.json`, `test_queries.json` → project root

## 9. Running the Application

From the project root directory, run:

```bash
python -m src.main --query "I want a low-risk investment for 12 months"
```

Replace the example query with your own natural-language query.

### Example Queries

```
I want a low-risk investment for 12 months.
I have a budget of 50000 INR and prefer a short-term opportunity.
Find opportunities with a minimum investment below 100000 INR.
I want a guaranteed 50% return in 1 month.
```

For queries requesting guaranteed returns, the system displays a message explaining that it does not verify guarantees. This does not establish whether any particular opportunity actually provides a guarantee.

## 10. Evaluation

The retrieval engine was evaluated using the 8 labelled queries supplied in `labelled_examples.csv`.

| Metric              | Result |
| --------------------| ------ |
| Mean Precision@5    | 0.525  |
| Mean Recall@5       | 0.781  |
| Hit Rate@5          | 1.000  |
| Number of queries   | 8      |

All 8 queries returned at least one labelled relevant opportunity in the top 5.

The results apply only to the supplied labelled examples and do not establish performance on unseen queries.

### Run Evaluation

From the project root directory:

```bash
python tests/evaluate.py
```

The evaluation script compares the retrieved top-5 opportunities with the labelled relevant opportunities and reports the metrics.

## 11. Limitations

- Evaluation is based on only 8 labelled queries.
- Query parsing uses predefined rules.
- Ranking weights are fixed.
- Missing or incorrectly extracted information may affect matching.
- The extraction confidence value of 1.0 is a placeholder and is not calibrated.
- Ranking scores indicate query matching, not financial success or investment suitability.
- Expected returns are not guaranteed.

## 12. Future Improvements

- Expand the labelled evaluation dataset.
- Improve natural-language query parsing.
- Test alternative ranking weights using held-out data.
- Improve extraction accuracy and confidence estimation.
- Add more robust handling of missing or ambiguous attributes.
- Investigate scalable indexing and candidate retrieval for larger datasets.
- Add stronger validation and safeguards for financial information.

## 13. Disclaimer

This project is an educational prototype developed for the AI/ML assessment.

The results are based on the supplied documents and extracted information. The system does not independently verify financial products, guarantee returns, or provide personalized financial advice. Users should verify relevant information with the original source documents and qualified professionals before making financial decisions.

## 14. Author

**Name:** Brijesh Niranjan K
**Project:** Intelligent Financial Opportunity Analysis & Recommendation Engine
