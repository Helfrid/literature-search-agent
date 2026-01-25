# Architectural Decision Records

Track important architectural decisions, their context, and trade-offs.

## Format

```markdown
### ADR-XXX: Decision Title (YYYY-MM-DD)

**Context:**
- Why the decision was needed
- What problem it solves

**Decision:**
- What was chosen

**Alternatives Considered:**
- Option 1 -> Why rejected
- Option 2 -> Why rejected

**Consequences:**
- Benefits
- Trade-offs
```

## Decisions

### ADR-001: Use BioPython Entrez for PubMed API Access (Unknown Date)

**Context:**
- Need to access PubMed/NCBI databases for literature searches
- Must respect NCBI API rate limits and authentication
- Need reliable XML parsing for PubMed article data

**Decision:**
- Use BioPython's Entrez module for all PubMed interactions
- Implement rate limiting (0.34s sleep between requests)
- Use batch processing for large result sets

**Alternatives Considered:**
- Direct HTTP requests to NCBI API -> More error-prone, requires manual XML parsing
- Other PubMed libraries -> BioPython is well-maintained and widely used

**Consequences:**
- Benefits: Reliable API access, automatic XML parsing, good documentation
- Trade-offs: Dependency on BioPython package

### ADR-002: Use Pydantic for Data Validation (Unknown Date)

**Context:**
- Need to validate PubMed article data structure
- Want type safety and serialization capabilities
- Must handle optional fields gracefully

**Decision:**
- Use Pydantic BaseModel for PubMedArticle and ScoringSheet
- Leverage automatic validation and JSON serialization
- Use Field defaults for auto-generated fields (date_fetched)

**Alternatives Considered:**
- Dataclasses -> Less validation, no automatic parsing
- Plain dictionaries -> No type safety, error-prone

**Consequences:**
- Benefits: Strong validation, excellent error messages, JSON serialization built-in
- Trade-offs: Additional dependency, learning curve for Pydantic syntax

### ADR-003: Mock PubMed API in Tests (2026-01-25)

**Context:**
- Need comprehensive test coverage for pubmed.py
- Cannot rely on actual PubMed API for tests (unreliable, slow, rate limits)
- Must test error handling and edge cases

**Decision:**
- Use unittest.mock to mock Entrez API calls
- Create fixtures in conftest.py with realistic XML responses
- Test all functions in isolation with mocked dependencies

**Alternatives Considered:**
- Integration tests against real API -> Too slow, unreliable, rate limit issues
- Record/replay library (VCR.py) -> Adds complexity, harder to test edge cases

**Consequences:**
- Benefits: Fast tests, reliable, can test error conditions
- Trade-offs: Mocks may diverge from real API over time
