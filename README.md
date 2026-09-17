# DHEIS — District Health & Education Intelligence System

**Integrated analytics for evidence-based district priority identification, combining India's health and education survey data into a single, actionable decision-support system.**

🔗 **Live Application:** [dheis-app.streamlit.app](https://dheis-app.streamlit.app/)
📊 **Power BI Dashboard:** *[Add your Power BI link or note it is demoed from Desktop]*

---

## Table of Contents

- [Overview](#overview)
- [The Problem](#the-problem)
- [Key Results](#key-results)
- [System Architecture](#system-architecture)
- [Methodology](#methodology)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Data Sources](#data-sources)
- [Limitations](#limitations)
- [Future Scope](#future-scope)
- [Responsible Use](#responsible-use)

---

## Overview

DHEIS combines district-level **health data (NFHS-5)** and **education data (DISE)** for 602 Indian districts into a single composite **Priority Index**, classifying every district into a **High / Medium / Low** priority tier. It identifies whether a district's challenge is primarily health-driven, education-driven, or both — and delivers the results through an interactive Power BI dashboard and a publicly deployed, AI-enhanced Streamlit web application.

The system is built for **government program officers** making quarterly health and education resource-allocation decisions — deciding where to send mobile health camps, deploy teachers, or fund school infrastructure.

## The Problem

Health and education departments typically review district performance separately, using different reports and review cycles. Districts struggling on **both** fronts simultaneously — arguably the highest-priority districts for intervention — are not systematically identified as a distinct group under this siloed process. DHEIS answers three questions for a decision-maker: **where** are the priority districts, **why** — which indicators are driving it — and **what** should be funded as a result.

## Key Results

| Metric | Value |
|---|---|
| Districts covered | 602 (reconciled from two independent government surveys) |
| Indicators used in the Priority Index | 14 core indicators (8 health, 6 education) |
| High / Medium / Low priority districts | 125 / 359 / 118 |
| Machine learning model | Logistic Regression (hyperparameter-tuned) |
| Model accuracy (held-out test set) | 95% |
| Model recall on High Priority districts | 96% |
| Baseline (majority-class) comparison | 59.5% accuracy, 0% High-tier recall |

## System Architecture

```
Raw Survey Data (NFHS-5, DISE)
        │
        ▼
PostgreSQL (Supabase) — reconciled schema, data-quality checks
        │
        ▼
Databricks (PySpark) — Bronze → Silver → Gold layered pipeline
        │  • Percentile-rank normalization
        │  • Priority Index & tier classification
        │  • ML training, tuning, fairness audit (MLflow)
        │
        ├──────────────┬──────────────
        ▼              ▼
   Power BI        Streamlit App
  (8-page report)  (public, AI-enhanced)
```

## Methodology

- **Data reconciliation:** district and state names were matched between the two independently-collected surveys using state-aware fuzzy matching, with every ambiguous match manually verified against real district lists.
- **Normalization:** all 14 core indicators are rescaled to a 0–100 vulnerability scale using **percentile-rank normalization** (not min-max), chosen after an initial min-max version was found to introduce a systematic scaling bias between the health and education dimensions.
- **Priority Index:** Health Sub-score and Education Sub-score (each an average of their normalized indicators) are combined via an equal-weighted average; districts are tiered using percentile cutoffs (top 20% High, bottom 20% Low, middle 60% Medium).
- **Machine learning:** a Logistic Regression classifier predicts `priority_tier` directly from raw indicators — explicitly excluding the Priority Index and sub-scores as features to prevent data leakage. Model selection used stratified 5-fold cross-validation on an 80% split; final performance was measured once on a genuinely untouched 20% held-out test set.
- **Fairness audit:** model accuracy was checked across gender-literacy-gap and SC/ST-population groups (used only for auditing, never as model features), with no material accuracy gap found between groups.

## Tech Stack

| Layer | Tools |
|---|---|
| Data cleaning & validation | Microsoft Excel |
| Database | PostgreSQL (Supabase), managed via pgAdmin |
| Data engineering | Databricks, PySpark, Delta Lake |
| Machine learning | scikit-learn, MLflow |
| Dashboard | Power BI |
| Web application | Streamlit, deployed on Streamlit Community Cloud |
| AI-generated insights | Groq API (`openai/gpt-oss-20b`) |

## Repository Structure

```
dheis/
├── app.py                          # Streamlit application
├── requirements.txt                # Python dependencies
├── notebooks/
│   └── DHEIS_pipeline.ipynb        # Full Databricks pipeline (bronze → gold, ML)
├── sql/
│   └── schema.sql                  # PostgreSQL schema and data-quality checks
├── data/
│   └── district_priority_snapshot.csv   # Gold-table snapshot used by the app
└── README.md
```

## Getting Started

**Run the Streamlit app locally:**

```bash
git clone https://github.com/<your-username>/dheis.git
cd dheis
pip install -r requirements.txt
```

Create a `.env` file with your Groq API key (free tier available at [console.groq.com](https://console.groq.com)):

```
GROQ_API_KEY=your_key_here
```

Then run:

```bash
streamlit run app.py
```

**Reproduce the full pipeline:** open `notebooks/DHEIS_pipeline.ipynb` in Databricks (Free Edition supported), connect it to a PostgreSQL/Supabase instance loaded via `sql/schema.sql`, and run all cells in order.

## Data Sources

- **NFHS-5** (National Family Health Survey), Ministry of Health and Family Welfare, Government of India — 2019–21
- **DISE** (District Information System for Education), Ministry of Education, Government of India — 2015–16

Both datasets are official, publicly available, and aggregated at the district level — no individual-level or personally identifiable data is used anywhere in this project.

## Limitations

- Health and education data reflect different survey years (2019–21 vs. 2015–16); this vintage gap is a documented, known limitation.
- 78 of 680 original education-file districts (11.5%) were excluded from the final matched dataset due to genuine administrative differences between the two surveys (e.g. regions sub-divided differently), rather than a data error.
- The AI-generated district brief is a decision-support aid, validated against real indicator data — it is not a substitute for expert review.

## Future Scope

- Automated alerting (e.g. via n8n) when a district newly enters the High Priority tier.
- Deeper integration of Tier 2 diagnostic data (individual vaccine coverage, teacher training, repeater rates).
- Updating the education data source to a more recent UDISE+ release.
- Formal user testing with real government program officers.

## Responsible Use

DHEIS is a **decision-support system**. It does not automatically allocate funding and does not replace human judgement. All priority scores, driver classifications, and resource recommendations are intended to inform — not determine — a real administrative decision.
