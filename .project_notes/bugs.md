# Bug Log

Track recurring bugs, their solutions, and prevention strategies.

## Format

```markdown
### YYYY-MM-DD - Brief Bug Description
- **Issue**: What went wrong
- **Root Cause**: Why it happened
- **Solution**: How it was fixed
- **Prevention**: How to avoid it in the future
```

## Bugs

### 2026-01-25 - Test Suite Created
- **Issue**: No test coverage for pubmed.py module
- **Root Cause**: Tests were not written during initial development
- **Solution**: Created comprehensive test suite with 30 tests using pytest and mocked PubMed API
- **Prevention**: Maintain test-driven development practices; add tests for new features

### 2026-01-25 - mypy Type Errors with Pydantic and Bio.Entrez
- **Issue**: mypy strict mode failed with "Class cannot subclass BaseModel (has type Any)" and "Error importing plugin pydantic.mypy: No module named 'pydantic'"
- **Root Cause**: Pydantic wasn't being recognized by mypy due to missing type stubs configuration; BioPython lacks type stubs
- **Solution**: Added `ignore_missing_imports = true` for both `pydantic.*` and `Bio.*` in pyproject.toml; added `# type: ignore` comments for Entrez API calls; added None checks for required Pydantic fields; cleared mypy cache
- **Prevention**: For Pydantic v2, if mypy plugin doesn't work, use `ignore_missing_imports = true` for pydantic.*; always use type: ignore for untyped external APIs
