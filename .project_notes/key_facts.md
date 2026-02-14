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

## Evaluation Architecture (Simplified)

### Phase 1: Ground Truth Collection (Complete)

- Fetched 2 weeks of PubMed abstracts via `pubmed.py`
- Built a Streamlit web app (`scoring_app.py`) for manual human scoring
- Human scores saved as ground truth JSON
- Scoring task: include/exclude + highlight + classification per paper

### Phase 2: Model Scoring (Next)

- Generate prompts for each model to replicate the human scoring task
- Run each model (local Ollama + frontier API) against the same papers
- Save per-model results as JSON (one file per model)
- Models: OpenBioLLM-8B, Bio-Mistral, LLaMA 3 8B, Qwen 2.5 7B

### Phase 3: Benchmarking

- Compare each model's JSON output against human ground truth
- Compute metrics: precision, recall, F1, Spearman correlation
- Identify per-model strengths/weaknesses by category
- Use results to select best model and refine prompts


## Security Note

- DO NOT store secrets, passwords, or API keys here
- Use environment variables or secret management tools
- This file is for configuration VALUES, not credentials

## Project Information

- **Project Name**: literature-search-agent
- **Version**: 0.1.0
- **Python Version**: >=3.12
- **Package Manager**: uv (with hatchling build backend)

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

### PubMedArticle (pubmed.py)

- pmid (required)
- title (required)
- authors (required)
- journal (required)
- abstract (optional)
- pub_date (optional)
- date_fetched (auto-generated)
- doi (optional)

### ScoringSheet (pubmed.py)

- pmid (required)
- title (required)
- abstract (optional, excluded from serialization)
- journal (required)
- score (default: 0)

### ArticleAnalysis (model_eval.py)

- include: bool (include in literature review?)
- highlight: bool (particularly important?)
- classification: Literal (10 categories)
- reasoning: str (2-3 sentence explanation)

## Evaluation Modules (Current State)

- **prompts.py** - System and user prompt templates for paper scoring
  - 10 classification categories: Cell cycle, Genome stability, Senescence, Cancer biology, CRISPR, Imaging, AI/Biology, Evolutionary, Other
  - Protein keywords: PP1, PP2A, CDK, Cyclin, Aurora, Polo, etc.
- **model_test.py** - pydantic-ai with Ollama (koesn/llama3-openbiollm-8b)
- **model_test_instructor.py** - Instructor with OpenAI-compatible API (qwen2.5:7b-instruct-q8_0)
- **model_eval.py** - Async scoring pipeline (incomplete - references undefined `client`)
- **model_config.py** - Pydantic Settings for model config (template, not actively used)
- **gt_data.py** - Ground truth data stub (import only)

## Unfinished / Known TODOs

- Move PubMed API key from hardcoded in pubmed.py to .env
- Complete model_eval.py (undefined `client` variable)
- Implement evaluate.py (metrics computation)
- Implement prompt_iterator.py (prompt improvement loop)
- Complete gt_data.py implementation
- Add tests for config.py, model_eval.py
- Update README.md (still has placeholder text)

## File Naming Conventions

- Date sanitization: Replace `/` with `-`, `[` with `_`, `]` with empty string
- Example: `2025/01/24[dp]` -> `2025-01-24_dp`
