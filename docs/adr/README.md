# Architecture Decision Records (ADRs)

This directory contains all Architecture Decision Records for the HCD LLM Optimization System.

## What are ADRs?

Architecture Decision Records document important architectural decisions made during the project, including:
- **Context:** Problem statement and background
- **Decision:** What was decided
- **Rationale:** Why this decision was made
- **Alternatives:** Other options considered
- **Consequences:** Trade-offs and implications

## ADR Index

### Technology Choices

**[001: Python Choice](001-python-choice.md)**
- Decision: Use Python 3.11+ as implementation language
- Rationale: Rich ecosystem, rapid development, ML/AI libraries
- Status: ✅ Accepted

### Architecture Patterns

**[002: Caching Strategy](002-caching-strategy.md)**
- Decision: Multi-level caching (L1: exact, L2: semantic)
- Rationale: Balance hit rate and performance
- Status: ✅ Accepted (see implementation note at end of ADR — class names evolved)

**[013: Facade and Factory Pattern](013-facade-factory-pattern.md)**
- Decision: `TokenOptimizer` facade + `src/factory.py` builder functions as the single composition point
- Rationale: Config flows to runtime; single home for config→constructor mapping; shared L1 cache; health checks wired
- Status: ✅ Accepted

**[016: No TruncationConfig — truncation defaults hard-wired in factory](016-truncation-no-config.md)**
- Decision: No `TruncationConfig` section in `ConfigSchema`; `build_truncator()` uses hard-wired defaults
- Rationale: Truncation is lossy with no acceptance gate; misconfiguration risk exceeds benefit; callers control strategy at call-site
- Status: ✅ Accepted

**[006: Cache Strategy](006-cache-strategy.md)**
- Decision: In-memory cache over distributed cache
- Rationale: Lower latency, simpler implementation
- Status: ✅ Accepted

**[007: Sync vs Async](007-sync-vs-async.md)**
- Decision: Synchronous processing with async future support
- Rationale: Simpler implementation, meets current requirements
- Status: ✅ Accepted

### Algorithms & Techniques

**[003: TF-IDF Scoring](003-tfidf-scoring.md)**
- Decision: Use TF-IDF for relevance scoring
- Rationale: Proven effectiveness, computational efficiency
- Status: ✅ Accepted

**[004: Semantic Similarity](004-semantic-similarity.md)**
- Decision: Cosine similarity for semantic matching
- Rationale: Fast computation, good accuracy
- Status: ✅ Accepted

**[005: Batch Processing](005-batch-processing.md)**
- Decision: Batch processing with similarity grouping
- Rationale: Improved throughput, better cache utilization
- Status: ✅ Accepted

**[008: Token Counting](008-token-counting.md)**
- Decision: tiktoken for token counting
- Rationale: Accurate, fast, provider-compatible
- Status: ✅ Accepted

### Quality Attributes

**[009: Error Handling](009-error-handling.md)**
- Decision: Comprehensive error handling with graceful degradation
- Rationale: System reliability and user experience
- Status: ✅ Accepted

**[010: Testing Strategy](010-testing-strategy.md)**
- Decision: Mock-based testing approach
- Rationale: Fast tests, no external dependencies
- Status: ✅ Accepted

**[011: Monitoring & Observability](011-monitoring-observability.md)**
- Decision: Comprehensive metrics and structured logging
- Rationale: Production visibility and debugging
- Status: ✅ Accepted

**[012: Security Model](012-security-model.md)**
- Decision: Defense-in-depth security approach (never implemented)
- Rationale: Comprehensive protection, compliance
- Status: ⛔ Superseded (2026-07-14) — its implementation/validation claims were
  fabricated; retracted in Phase 7. Canonical security docs:
  [STRIDE Threat Model](../security/THREAT_MODEL.md) and
  [SECURITY.md](../../SECURITY.md).

## ADR Statistics

- **Total ADRs:** 13
- **Status:** 12 accepted, 1 superseded (012)
- **Coverage:** Technology, Architecture, Algorithms, Quality, Composition patterns
- **Lines:** ~5,000 total (estimated)

## ADR Guidelines

### When to Create an ADR

Create an ADR when making decisions about:
- Technology choices (languages, frameworks, tools)
- Architecture patterns (caching, processing, integration)
- Algorithms and techniques (scoring, matching, optimization)
- Quality attributes (security, testing, monitoring, error handling)
- Significant design trade-offs

### ADR Template

```markdown
# ADR-XXX: [Decision Title]

**Status:** [Proposed | Accepted | Deprecated | Superseded]
**Date:** YYYY-MM-DD
**Deciders:** [List of decision makers]
**Context:** [Project/Component context]

## Context

[Describe the problem and constraints]

## Decision

[State the decision clearly]

## Rationale

[Explain why this decision was made]

### Alternatives Considered

[List and evaluate alternatives]

## Consequences

### Positive
- [List benefits]

### Negative
- [List drawbacks]

### Neutral
- [List neutral impacts]

## Implementation

[Implementation details and examples]

## Validation

[How to validate this decision]

## References

[Related documents and resources]
```

### Naming Convention

- Format: `XXX-descriptive-name.md`
- XXX: Three-digit sequential number (001, 002, etc.)
- Use kebab-case for descriptive name
- Keep names concise but clear

### Best Practices

1. **Be Specific:** Clearly state what was decided
2. **Explain Why:** Provide rationale and context
3. **Consider Alternatives:** Show what else was evaluated
4. **Document Trade-offs:** Be honest about consequences
5. **Keep Updated:** Mark as deprecated if superseded
6. **Link Related Docs:** Reference architecture and implementation docs

## Related Documentation

- [Architecture Documentation](../architecture/) - System architecture
- [Component Specifications](../architecture/components/) - Component details
- [Project Management](../project-management/) - Implementation planning
- [Root Index](../../INDEX.md) - Complete documentation index

## Questions?

For questions about ADRs or to propose a new ADR, contact the architecture team.
