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

### ADR-004: Use Instructor Library for Structured LLM Output (2026-02)

**Context:**
- Need to get structured, validated output from LLMs for paper scoring
- Must work with local Ollama models via OpenAI-compatible API
- Output must conform to Pydantic models (ArticleAnalysis)

**Decision:**
- Use Instructor library with OpenAI client pointing to Ollama
- Define output schemas as Pydantic models
- Use async scoring pipeline (model_eval.py) for parallel processing

**Alternatives Considered:**
- pydantic-ai -> Also explored (model_test.py), but Instructor more mature for structured output
- Raw OpenAI function calling -> More boilerplate, less validation
- LangChain -> Too heavy for this use case

**Consequences:**
- Benefits: Clean structured output, automatic validation, retry on parse failures
- Trade-offs: Additional dependency, tied to OpenAI-compatible API format

### ADR-005: Use Local Ollama Models for Paper Evaluation (2026-02)

**Context:**
- Need to evaluate ~50-100 papers daily for relevance to cell cycle/cancer biology
- Want to compare multiple models against human expert judgment
- Cost sensitivity for daily automated pipeline

**Decision:**
- Use Ollama for local model inference (qwen2.5:7b, OpenBioLLM-8B, BioMistral, llama3:8b)
- Compare local models against frontier model (Claude API) and manual scoring
- Run on RTX 5090 server for adequate performance

**Alternatives Considered:**
- Cloud-only (OpenAI/Anthropic) -> Too expensive for daily batch scoring
- vLLM -> More complex setup, Ollama simpler for development
- HuggingFace Transformers direct -> More code, Ollama handles serving

**Consequences:**
- Benefits: No per-query cost, full control, privacy for research data
- Trade-offs: Hardware dependency, model quality varies, requires GPU server
