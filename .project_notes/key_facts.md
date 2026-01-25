# Key Facts

# Literature Monitoring Pipeline - Evaluator Implementation Plan

## Project Vision (Updated)

**Current Focus:** Build and validate the filtering/evaluation system before any deployment

**End Goal (Post-Evaluation):** Once evaluator is proven, deploy as automated pipeline

**Scope for Now:** Develop modular evaluator that can:

- Score papers using multiple models in parallel
- Track your manual evaluations
- Compute performance metrics over time
- Allow prompt iteration and improvement
- Validate model selection before deployment

---

## Model Selection:

koesn/llama3-openbiollm-8b:latest    069ab18bd45f    4.9 GB
jsk/bio-mistral:latest               ce9609fd854f    4.1 GB
llama3:8b                            365c0bd3c000    4.7 GB
qwen2.5:7b-instruct-q8_0             2d9500c94841    8.1 GB

## Evaluation Architecture

### Daily Automated Flow

```
MORNING (Cron Job - 6:00 AM)
┌──────────────────────────────────────────────────────────────┐
│ pubmed.py - Fetch Yesterday's Papers                          │
│ ├─ Search PubMed for papers from previous day                │
│ ├─ Save: papers_raw_YYYY-MM-DD.json                          │
│ └─ Save: papers_for_manual_YYYY-MM-DD.json (title-only)      │
└──────────────────────────────────────────────────────────────┘
                            ↓
MID-MORNING (Cron Job - 7:00 AM)
┌──────────────────────────────────────────────────────────────┐
│ model_scorer.py - Score with All Models (Parallel)           │
│ ├─ Load papers_raw_YYYY-MM-DD.json                           │
│ ├─ Score with: Frontier Model (Claude API)                  │
│ ├─ Score with: OpenBioLLM-8B (Local)                        │
│ ├─ Score with: Me-LLaMA-13B (Local)                         │
│ ├─ Save: frontier_YYYY-MM-DD.json                            │
│ ├─ Save: openbiollm_YYYY-MM-DD.json                          │
│ └─ Save: mellama_YYYY-MM-DD.json                             │
└──────────────────────────────────────────────────────────────┘
                            ↓
WHENEVER (Manual - Your Time)
┌──────────────────────────────────────────────────────────────┐
│ You - Manual Scoring                                          │
│ ├─ Edit: papers_for_manual_YYYY-MM-DD.json                   │
│ ├─ Add your_score values (0, 1, or 2)                        │
│ └─ Save back to manual/ directory                            │
└──────────────────────────────────────────────────────────────┘
                            ↓
ANYTIME (Manual Trigger)
┌──────────────────────────────────────────────────────────────┐
│ evaluate.py - Compute Metrics & Analysis                     │
│ ├─ Merge model scores + your manual scores                   │
│ ├─ Compute: Spearman correlation, Precision, Recall, F1      │
│ ├─ Analyze by journal, score category                        │
│ ├─ Identify disagreements & error patterns                   │
│ ├─ Save: papers_evaluated_YYYY-MM-DD.json                    │
│ ├─ Log: metrics_log.jsonl with timestamps                    │
│ └─ Generate: correlation_trend.png                           │
└──────────────────────────────────────────────────────────────┘
                            ↓
EVERY 3 DAYS (Cron Job - Morning)
┌──────────────────────────────────────────────────────────────┐
│ prompt_iterator.py - Improve Prompts                         │
│ ├─ Analyze disagreements from past 3 days                    │
│ ├─ Extract success examples (you scored higher)              │
│ ├─ Extract failure examples (you scored lower)               │
│ ├─ Build new prompts with embedded examples                  │
│ ├─ Save new prompt versions                                  │
│ ├─ Optionally re-score past 3 days with new prompts          │
│ └─ Log prompt version updates                                │
└──────────────────────────────────────────────────────────────┘
```

### Key Decoupling

- **pubmed.py** - Independent, runs daily (automated)
- **model_scorer.py** - Independent, runs daily after pubmed.py (automated)
- **evaluate.py** - Independent, runs whenever needed (manual or periodic)
- **prompt_iterator.py** - Independent, runs every 3 days (automated)

Each script:

- Reads from data/ directory
- Writes results to appropriate subdirectory
- Logs results with timestamps
- Can be run independently without dependencies

---

## Modular Implementation Plan

### File Organization

```
src/literature_search_agent/
├── pubmed.py                 (existing - runs daily via cron)
├── models/
│   ├── model_scorer.py       (runs daily after pubmed.py)
│   └── model_types.py        (Pydantic models, shared by all)
├── evaluation/
│   ├── evaluator.py          (runs independently, computes metrics)
│   ├── metrics_tracker.py    (loads evaluation data, builds history)
│   └── prompt_iterator.py    (runs every 3 days, updates examples)
└── config/
    └── config.py             (paths, model names, etc)

data/
├── raw/
│   └── papers_raw_2025-01-24.json
├── model_scores/
│   ├── frontier_2025-01-24.json
│   ├── openbiollm_2025-01-24.json
│   └── mellama_2025-01-24.json
├── manual/
│   └── papers_for_manual_2025-01-24.json  (you edit these)
├── evaluated/
│   └── papers_evaluated_2025-01-24.json
├── prompts/
│   ├── frontier_v1.txt
│   ├── openbiollm_v1.txt
│   └── mellama_v1.txt
└── metrics/
    ├── metrics_log.jsonl
    └── plots/
```


## Security Note

- DO NOT store secrets, passwords, or API keys here
- Use environment variables or secret management tools
- This file is for configuration VALUES, not credentials

## Project Information

- **Project Name**: literature-search-agent
- **Version**: 0.1.0
- **Python Version**: >=3.12
- **Package Manager**: pip/hatch

## PubMed Configuration

- **Email**: hh65@sussex.ac.uk (required by NCBI)
- **API Key**: Stored in src/literature_search_agent/pubmed.py (should be moved to .env)
- **Rate Limit**: 0.34s sleep between requests (3 requests/second with API key)
- **Default Batch Size**:
  - Search: 1000 PMIDs per batch
  - Fetch XML: 200 PMIDs per batch

## Journal Query

- **Primary Journals**: Nature family, Cell family, Science family, EMBO, cancer journals
- **Full Query**: Defined in `src/literature_search_agent/__init__.py` as `PUBMED_QUERY`
- **Test Query**: Defined as `PUBMED_QUERY_TEST` (Nature and Cell only)

## Output Files

- **Raw Data**: `papers_raw_{date}.json` - Full article metadata
- **Scoring Sheet**: `papers_for_manual_{date}.json` - Minimal data for manual review
- **Default Output Directory**: `data/`

## Development Tools

- **Linter**: Ruff (line-length: 79)
- **Type Checker**: mypy (strict mode, Python 3.12)
- **Test Framework**: pytest
- **Commit Convention**: Conventional Commits (Commitizen)
- **Pre-commit Hooks**: Enabled

### mypy Configuration
- **Pydantic imports**: Ignored (`ignore_missing_imports = true` for `pydantic.*`)
- **Bio.* imports**: Ignored (untyped library)
- **Type ignores**: Used for Bio.Entrez API calls

## Testing

- **Test Directory**: `tests/`
- **Fixtures**: `tests/conftest.py`
- **Test Pattern**: `test_*.py`
- **Coverage Goal**: Comprehensive coverage with mocked external APIs

## Data Models

### PubMedArticle

- pmid (required)
- title (required)
- authors (required)
- journal (required)
- abstract (optional)
- pub_date (optional)
- date_fetched (auto-generated)

### ScoringSheet

- pmid (required)
- title (required)
- score (default: 0)

## File Naming Conventions

- Date sanitization: Replace `/` with `-`, `[` with `_`, `]` with empty string
- Example: `2025/01/24[dp]` -> `2025-01-24_dp`
