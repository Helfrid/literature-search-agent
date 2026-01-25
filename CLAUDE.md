# Claude Code Instructions

This document provides context and guidelines for AI assistants working on the literature-search-agent project.

## Project Overview

A Python tool for searching PubMed literature databases and managing research articles. The project focuses on high-quality journals in cell biology, cancer research, and related fields.

## Project Memory System

This project maintains institutional knowledge in `.project_notes/` for consistency across sessions.

### Memory Files

- **bugs.md** - Bug log with dates, solutions, and prevention notes
- **decisions.md** - Architectural Decision Records (ADRs) with context and trade-offs
- **key_facts.md** - Project configuration, credentials, ports, important URLs
- **issues.md** - Work log with ticket IDs, descriptions, and URLs

### Memory-Aware Protocols

**Before proposing architectural changes:**
- Check `.project_notes/decisions.md` for existing decisions
- Verify the proposed approach doesn't conflict with past choices
- If it does conflict, acknowledge the existing decision and explain why a change is warranted

**When encountering errors or bugs:**
- Search `.project_notes/bugs.md` for similar issues
- Apply known solutions if found
- Document new bugs and solutions when resolved

**When looking up project configuration:**
- Check `.project_notes/key_facts.md` for credentials, ports, URLs, service accounts
- Prefer documented facts over assumptions

**When completing work on tickets:**
- Log completed work in `.project_notes/issues.md`
- Include ticket ID, date, brief description, and URL

**When user requests memory updates:**
- Update the appropriate memory file (bugs, decisions, key_facts, or issues)
- Follow the established format and style (bullet lists, dates, concise entries)

### Style Guidelines for Memory Files

- **Prefer bullet lists over tables** for simplicity and ease of editing
- **Keep entries concise** (1-3 lines for descriptions)
- **Always include dates** for temporal context
- **Include URLs** for tickets, documentation, monitoring dashboards
- **Manual cleanup** of old entries is expected (not automated)

## Code Style and Standards

### Python Standards
- **Python Version**: >=3.12
- **Line Length**: 79 characters (Ruff configuration)
- **Type Checking**: mypy in strict mode
- **Linting**: Ruff with comprehensive rule set
- **Testing**: pytest with fixtures in conftest.py

### Commit Conventions
- Use Conventional Commits format
- Managed by Commitizen
- Version bumps update `__init__.py`, `pyproject.toml`, and `README.md`

### Pre-commit Hooks
- Ruff linting and formatting
- mypy type checking
- Automatically fixes issues where possible

## Testing Practices

### Test Structure
- All tests in `tests/` directory
- Fixtures in `tests/conftest.py` for reusability
- Mock external APIs (PubMed/NCBI) - never use real API in tests
- Test file pattern: `test_*.py`

### Test Coverage Goals
- Unit tests for all functions
- Pydantic model validation tests
- Edge case and error handling tests
- Integration tests with mocked dependencies

### Running Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_pubmed.py
```

## Module Structure

### Core Modules
- **pubmed.py** - PubMed API interaction and data fetching
- **config.py** - Environment configuration and logging
- **__init__.py** - Package initialization and query definitions

### Data Models (Pydantic)
- **PubMedArticle** - Full article metadata with validation
- **ScoringSheet** - Minimal article info for manual review

### Key Functions
- `_pubmed_search()` - Search PubMed for article IDs
- `_fetch_pubmed_xml()` - Fetch and parse article metadata
- `_save_pubmed_data()` - Save raw article data to JSON
- `_save_scoring_sheet()` - Save scoring sheet for manual review
- `pubmed_search()` - Main orchestrator function

## Development Workflow

1. Check `.project_notes/decisions.md` before major changes
2. Write tests first (TDD approach when possible)
3. Run linting: `ruff check .`
4. Run type checking: `mypy .`
5. Run tests: `pytest`
6. Commit with conventional commit messages
7. Update `.project_notes/` as needed

## Common Tasks

### Adding a New Feature
1. Check existing decisions in `.project_notes/decisions.md`
2. Write tests in `tests/`
3. Implement feature
4. Update documentation
5. Log work in `.project_notes/issues.md`

### Fixing a Bug
1. Search `.project_notes/bugs.md` for similar issues
2. Write failing test that reproduces the bug
3. Fix the bug
4. Verify test passes
5. Document in `.project_notes/bugs.md`

### Updating Configuration
1. Update the configuration
2. Update `.project_notes/key_facts.md` with new values
3. Update any affected documentation

## Important Notes

- **API Key Security**: The PubMed API key is currently hardcoded in `pubmed.py` - should be moved to environment variables
- **Rate Limiting**: Always respect NCBI rate limits (0.34s between requests)
- **Batch Processing**: Use appropriate batch sizes (1000 for search, 200 for fetch)
- **Date Sanitization**: File naming requires sanitization of dates (replace `/` with `-`, `[` with `_`, `]` with empty)
