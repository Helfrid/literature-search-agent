# Work Log

Track completed work, tickets, and project milestones.

## Format

```markdown
### YYYY-MM-DD - TICKET-ID: Brief Description
- **Status**: Completed / In Progress / Blocked
- **Description**: 1-2 line summary
- **URL**: Link to ticket/PR/issue
- **Notes**: Any important context
```

## Work Items

### 2026-01-25 - Test Suite for pubmed.py Module
- **Status**: Completed
- **Description**: Created comprehensive test suite with 30 tests covering all functions and Pydantic models in pubmed.py. Implemented fixtures in conftest.py to mock PubMed API responses.
- **Tests**: All 30 tests passing
- **Coverage**:
  - PubMedArticle model (6 tests)
  - ScoringSheet model (4 tests)
  - _pubmed_search function (5 tests)
  - _fetch_pubmed_xml function (6 tests)
  - _save_pubmed_data function (4 tests)
  - _save_scoring_sheet function (4 tests)
  - pubmed_search integration (1 test)
- **Notes**: Used unittest.mock to avoid hitting real PubMed API

### 2026-01-25 - Project Memory System Setup
- **Status**: Completed
- **Description**: Initialized .project_notes directory with bugs.md, decisions.md, key_facts.md, and issues.md. Added memory-aware protocols to CLAUDE.md.
- **Notes**: Following project-memory skill guidelines

### 2026-02 - Evaluation System Development (eval-work branch)
- **Status**: In Progress
- **Description**: Building paper scoring pipeline with multiple LLM models. Added prompts.py (system/user prompt templates), model_test.py (pydantic-ai + Ollama), model_test_instructor.py (Instructor + OpenAI-compatible API), model_eval.py (async scoring pipeline), model_config.py (model configuration), gt_data.py (ground truth stub).
- **Key Commits**:
  - `abc0722` - model work on rtx5090 server
  - `2237423` - add scoring app, evaluation data, and ground truth module
  - `c4bb51a` - merge: integrate upstream origin/main into eval-work
- **Notes**: Core PubMed fetching is solid; evaluation pipeline still being developed. prompts.py and model_test.py have uncommitted changes.

### 2026-02-13 - Project Memory Refresh
- **Status**: Completed
- **Description**: Updated .project_notes with current project state: added ADR-004 (Instructor library) and ADR-005 (local Ollama models), fixed package manager reference in key_facts.md (was pip/hatch, now uv), documented eval-work branch progress.
