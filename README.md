# TrialsIntel 🧬

AI-powered clinical trial intelligence — fetch, analyze, and explore trials with Claude.

## Quick Start

```bash
git clone https://github.com/rtdatasci/TrialsIntel.git
cd TrialsIntel
pip install -r requirements.txt
cp .env.example .env  # add your ANTHROPIC_API_KEY
python run_pipeline.py  # fetch & analyze ~50 trials
streamlit run app.py    # launch dashboard
```

## What It Does

1. **Fetches** ~50 real clinical trials from [ClinicalTrials.gov](https://clinicaltrials.gov) (free public API)
2. **Extracts** structured entities (drug, disease, sponsor, phase, mechanism) using Claude AI
3. **Stores** results in a local SQLite database
4. **Explores** via an interactive Streamlit dashboard with filters and charts

## Tech Stack

| Layer | Technology |
|---|---|
| Data source | ClinicalTrials.gov API v2 |
| AI extraction | Anthropic Claude (claude-haiku) |
| Storage | SQLite (stdlib) |
| Data wrangling | pandas |
| Dashboard | Streamlit |

## Project Structure

```
TrialsIntel/
├── app.py                  # Streamlit dashboard
├── run_pipeline.py         # One-shot fetch + extract + store
├── src/
│   ├── fetch_trials.py     # ClinicalTrials.gov API client
│   ├── extract_entities.py # Claude entity extraction
│   ├── database.py         # SQLite operations
│   └── search.py           # Keyword filtering
├── examples/demo.ipynb     # Step-by-step walkthrough
└── tests/                  # pytest unit tests
```

## What This Demonstrates

- **LLM integration:** Structured entity extraction with Claude API
- **Data pipelines:** API → transform → store → query
- **Life sciences domain:** Clinical trial data, phases, mechanisms
- **Clean code:** Modular design, unit tests, clear interfaces
