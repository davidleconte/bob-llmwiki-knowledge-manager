---
title: "Token-Efficient Repository Analysis Workflow"
date: 2026-07-12
status: reference
category: guide
related:
  - ../knowledge-base/guides/setup-token-optimization.md
  - ../quick-start.md
  - ../USAGE.md
---

# Token-Efficient Repository Analysis Workflow

**Purpose:** A systematic workflow for auditing, analyzing, correcting, enriching, and adding features to GitHub repositories while minimizing token consumption.

**Version:** 1.0
**Last Updated:** July 12, 2026

---

## Overview

This workflow describes how the **Bob Shell Knowledge Manager** (KB documentation framework) and the **Token Optimization System** (Python prompt optimization) can be used **independently or alongside each other** for token-efficient repository analysis. The two systems are **not integrated** — each operates as a standalone tool. See [README.md `§` dual systems](../README.md#this-repository-contains-two-separate-systems) for details.

### Key Principles

1. **Progressive Depth** - Start broad, go deep incrementally
2. **Cache Everything** - Reuse analysis results across sessions
3. **Document Once** - Store findings in knowledge base, reference later
4. **Batch Operations** - Group similar analyses to maximize cache hits
5. **Incremental Updates** - Update existing docs rather than recreating

---

## Phase 1: Initial Setup (One-Time, ~100 tokens)

### Step 1.1: Initialize Knowledge Base

```bash
cd ~/Projects/target-repository
~/Projects/bob-llmwiki-knowledge-manager/scripts/init-project.sh
```

**Creates:**
```
docs/knowledge-base/
├── INDEX.md
├── concepts/       # Architecture & design patterns
├── guides/         # Improvement & refactoring guides
├── references/     # API & component documentation
└── research/       # Audit findings & analysis
```

### Step 1.2: Create Analysis Structure

```bash
bob --chat-mode=knowledge-manager
```

**Initialize tracking documents:**
```
Create a research document titled "analysis-roadmap-2026-07" with sections:
1. Repository Overview
2. Analysis Phases
3. Findings Summary
4. Improvement Priorities
5. Progress Tracking
```

**Token Cost:** ~50 tokens (cached for reuse)

---

## Phase 2: Broad Analysis (Token-Efficient Scanning)

### Step 2.1: Repository Structure Analysis

**Goal:** Understand high-level organization without reading all files

```bash
bob --chat-mode=knowledge-manager
```

**Commands (in order):**

1. **List directory structure:**
```
List the top-level directory structure and create a concept document 
describing the repository organization
```

2. **Identify key files:**
```
Identify and list the 10 most important files based on:
- README, CONTRIBUTING, package.json/requirements.txt
- Main entry points (main.py, index.js, etc.)
- Configuration files
- Test directories

Create a reference document listing these key files with brief descriptions.
```

**Token Optimization:**
- Uses `list_files` tool (low token cost)
- Caches directory structure (L1 cache hit on subsequent queries)
- Documents findings once, references later

**Token Cost:** ~200 tokens (first run), ~20 tokens (cached subsequent runs)

### Step 2.2: Technology Stack Identification

```
Analyze package.json, requirements.txt, go.mod, or similar files and 
create a concept document describing:
- Programming languages used
- Major frameworks and libraries
- Build tools and dependencies
- Testing frameworks
```

**Token Optimization:**
- Reads only dependency files (small, focused)
- Caches dependency analysis (L2 semantic cache for similar queries)

**Token Cost:** ~150 tokens (first run), ~30 tokens (cached)

### Step 2.3: Architecture Overview

```
Based on the directory structure and key files, create a concept 
document describing the high-level architecture:
- Application layers (frontend, backend, database)
- Design patterns observed
- Module organization
- Entry points and flow
```

**Token Optimization:**
- Uses previously cached structure analysis
- No need to re-read files
- Semantic cache hits for architecture queries

**Token Cost:** ~100 tokens (leverages cache)

---

## Phase 3: Targeted Deep Dives (Progressive Analysis)

### Step 3.1: Prioritize Analysis Areas

**Create priority matrix:**
```
Create a research document titled "analysis-priorities" categorizing 
components by:
- Criticality (High/Medium/Low)
- Complexity (High/Medium/Low)
- Risk (Security/Performance/Maintainability)

Focus deep analysis on High-Criticality + High-Risk areas first.
```

**Token Cost:** ~80 tokens

### Step 3.2: Component-by-Component Analysis

**For each priority component:**

```
Analyze [component-name] in [directory] and create:
1. A concept document describing its purpose and design
2. A research document with findings on:
   - Code quality issues
   - Security concerns
   - Performance bottlenecks
   - Improvement opportunities
```

**Token Optimization Strategy:**

1. **Read Once, Document Thoroughly:**
   - Read component files once
   - Create comprehensive documentation
   - Reference documentation in future queries

2. **Use Truncation for Large Files:**
   - For files >1000 lines, use truncation strategies
   - Focus on critical sections (imports, class definitions, main functions)
   - Read full file only if needed

3. **Batch Similar Analyses:**
   - Analyze all authentication components together
   - Analyze all database components together
   - Maximize semantic cache hits

**Token Cost per Component:**
- First component: ~500 tokens (no cache)
- Similar components: ~150 tokens (semantic cache hits)
- Subsequent reviews: ~50 tokens (exact cache hits)

### Step 3.3: Cross-Component Analysis

**After analyzing individual components:**

```
Review all component documentation and create a research document 
analyzing:
- Integration patterns between components
- Shared dependencies and coupling
- Architectural inconsistencies
- System-wide concerns (error handling, logging, security)
```

**Token Optimization:**
- References existing component docs (no re-reading)
- Uses cached component analyses
- Semantic similarity for pattern detection

**Token Cost:** ~200 tokens (leverages all previous cache)

---

## Phase 4: Issue Identification & Categorization

### Step 4.1: Security Audit

```
Review all authentication, authorization, and data handling code 
documented in the knowledge base and create a research document 
titled "security-audit-findings" with:
- Critical vulnerabilities (OWASP Top 10)
- Security best practices violations
- Recommended fixes with priority
```

**Token Optimization:**
- References existing component docs
- No need to re-read code
- Caches security patterns for similar repos

**Token Cost:** ~150 tokens

### Step 4.2: Code Quality Assessment

```
Based on documented components, create a research document 
"code-quality-assessment" analyzing:
- Code duplication
- Complexity metrics (inferred from structure)
- Naming conventions
- Documentation coverage
- Test coverage
```

**Token Cost:** ~120 tokens

### Step 4.3: Performance Analysis

```
Review database queries, API endpoints, and algorithms documented 
in the knowledge base and create a research document 
"performance-analysis" with:
- Identified bottlenecks
- N+1 query problems
- Inefficient algorithms
- Caching opportunities
```

**Token Cost:** ~130 tokens

### Step 4.4: Architecture Assessment

```
Create a research document "architecture-assessment" comparing:
- Current architecture (from concept docs)
- Industry best practices
- Recommended improvements
- Migration path
```

**Token Cost:** ~100 tokens

---

## Phase 5: Improvement Planning

### Step 5.1: Prioritize Improvements

```
Create a research document "improvement-roadmap" that consolidates 
all findings and prioritizes improvements by:
- Impact (High/Medium/Low)
- Effort (High/Medium/Low)
- Dependencies
- Risk

Create a priority matrix: Quick Wins, Major Projects, Fill-ins, Thankless Tasks
```

**Token Cost:** ~150 tokens

### Step 5.2: Create Implementation Guides

**For each high-priority improvement:**

```
Create a guide titled "[improvement-name]-implementation-guide" with:
- Current state (reference concept docs)
- Target state
- Step-by-step implementation plan
- Testing strategy
- Rollback plan
```

**Token Optimization:**
- References existing documentation
- Templates for similar improvements
- Cached implementation patterns

**Token Cost per Guide:** ~100 tokens (first), ~40 tokens (similar guides)

---

## Phase 6: Incremental Implementation

### Step 6.1: Implement & Document

**For each improvement:**

1. **Switch to code mode:**
```bash
bob --chat-mode=code
```

2. **Implement changes:**
```
Implement [improvement] following the guide in 
docs/knowledge-base/guides/[improvement]-implementation-guide.md
```

3. **Switch back to knowledge-manager mode:**
```bash
bob --chat-mode=knowledge-manager
```

4. **Update documentation:**
```
Update the [component] concept document to reflect the changes made.
Update the improvement-roadmap to mark [improvement] as complete.
```

**Token Optimization:**
- Implementation uses code mode (different context)
- Documentation updates reference existing docs
- Progress tracking prevents duplicate work

**Token Cost per Improvement:**
- Implementation: Variable (depends on complexity)
- Documentation update: ~50 tokens

### Step 6.2: Validation & Testing

```
Create a guide for testing [improvement] with:
- Test cases
- Expected results
- Validation checklist
```

**Token Cost:** ~80 tokens

---

## Phase 7: Continuous Maintenance

### Step 7.1: Regular Reviews

**Weekly:**
```
Review changes made this week and update:
- Component concept documents
- Architecture overview
- Improvement roadmap progress
```

**Token Cost:** ~100 tokens/week

**Monthly:**
```
Conduct mini-audit:
- Review new code for quality issues
- Check for security concerns
- Update performance analysis
- Identify new improvement opportunities
```

**Token Cost:** ~300 tokens/month

### Step 7.2: Knowledge Base Maintenance

```
Validate knowledge base structure and cross-references:
~/Projects/bob-llmwiki-knowledge-manager/scripts/validate-kb.sh

Update INDEX.md with new documents and findings.
```

**Token Cost:** ~50 tokens

---

## Token Consumption Summary

### Initial Analysis (Complete Repository)

| Phase | First Run | Cached Runs | Savings |
|-------|-----------|-------------|---------|
| Setup | 100 | 10 | 90% |
| Broad Analysis | 450 | 80 | 82% |
| Deep Dives (10 components) | 3,500 | 800 | 77% |
| Issue Identification | 500 | 150 | 70% |
| Improvement Planning | 400 | 120 | 70% |
| **Total** | **4,950** | **1,160** | **77%** |

### Ongoing Maintenance

| Activity | Frequency | Tokens/Instance | Monthly Total |
|----------|-----------|-----------------|---------------|
| Weekly Review | 4x/month | 100 | 400 |
| Monthly Audit | 1x/month | 300 | 300 |
| Implementation Updates | Variable | 50 | ~200 |
| **Total** | - | - | **~900/month** |

### Key Savings Mechanisms

The **measured** optimizer-compression magnitude is manifest-backed in `evaluation/results/validation-2026-07-14/`; the per-mechanism items below are illustrative of *how* tokens are saved, not measured figures:

1. **L1 Cache (Exact Match):** repeated queries served from cache (recompute avoided)
2. **L2 Cache (Semantic):** similar queries served from cache
3. **Documentation References:** cite digested reports instead of re-reading source
4. **Batch Processing:** group related analyses into one pass
5. **Incremental Updates:** update the KB, don't re-analyze from scratch

---

## Best Practices

### 1. Document Everything Immediately

**Why:** Prevents re-reading code in future sessions

**How:**
```
After analyzing [component], immediately create:
- Concept document (what it is)
- Research document (findings)
- Reference document (API/interface)
```

### 2. Use Semantic Queries

**Why:** Maximizes L2 cache hits

**How:**
```
Instead of: "Analyze the authentication system"
Use: "Review authentication patterns and security practices"
(Similar phrasing = cache hit)
```

### 3. Batch Similar Analyses

**Why:** Semantic cache learns patterns

**How:**
```
Analyze all database-related components in one session:
- models/
- repositories/
- migrations/
```

### 4. Reference, Don't Re-Read

**Why:** Massive token savings

**How:**
```
Instead of: "Read src/auth/login.py and analyze security"
Use: "Based on the authentication concept document, analyze security"
```

### 5. Incremental Updates

**Why:** Avoids full re-analysis

**How:**
```
Update the [component] concept document with [new information]
(vs. "Re-analyze [component] and create new documentation")
```

### 6. Use Truncation Strategically

**Why:** Reduces tokens for large files

**How:**
```
For files >1000 lines:
- Read structure first (imports, classes, functions)
- Deep dive only on critical sections
- Use search_file_content for specific patterns
```

### 7. Export for Offline Reference

**Why:** Zero tokens for human review

**How:**
```bash
~/Projects/bob-llmwiki-knowledge-manager/scripts/export-kb.sh html
# Review findings in browser, no Bob Shell needed
```

---

## Example: Complete Workflow

### Day 1: Initial Analysis (4,950 tokens)

```bash
# Setup
cd ~/Projects/target-repo
~/Projects/bob-llmwiki-knowledge-manager/scripts/init-project.sh
bob --chat-mode=knowledge-manager

# Broad analysis
"List directory structure and create organization concept document"
"Analyze dependencies and create technology stack concept document"
"Create high-level architecture concept document"

# Prioritize
"Create analysis-priorities research document"

# Deep dive (top 5 components)
"Analyze authentication system and create documentation"
"Analyze database layer and create documentation"
"Analyze API endpoints and create documentation"
"Analyze frontend components and create documentation"
"Analyze configuration system and create documentation"

# Identify issues
"Create security-audit-findings research document"
"Create code-quality-assessment research document"
"Create performance-analysis research document"

# Plan improvements
"Create improvement-roadmap research document"
"Create implementation guides for top 3 improvements"
```

### Day 2: Implementation (Variable tokens)

```bash
bob --chat-mode=code

# Implement improvements
"Implement security fix for authentication following the guide"
"Implement performance optimization for database queries"
"Implement error handling improvements"

bob --chat-mode=knowledge-manager

# Update documentation
"Update authentication concept document with security fixes"
"Update database concept document with optimizations"
"Update improvement-roadmap marking items complete"
```

### Week 2: Review (100 tokens)

```bash
bob --chat-mode=knowledge-manager

"Review changes made this week and update relevant documentation"
```

### Month 2: Maintenance (300 tokens)

```bash
bob --chat-mode=knowledge-manager

"Conduct monthly audit and update findings"
```

---

## Integration with Token Optimization System

### Using the Python Token Optimization System

**For programmatic analysis:**

```python
from src.cache import MultiLevelCache
from src.optimizer import PromptOptimizer
from src.monitoring import get_logger, get_metrics_collector

# Initialize
cache = MultiLevelCache()
optimizer = PromptOptimizer()
logger = get_logger("repo_analysis")
metrics = get_metrics_collector()

# Analyze with caching
def analyze_component(component_path, query):
    # Check cache first
    cached = cache.get(query)
    if cached:
        logger.info("cache_hit", component=component_path)
        return cached
    
    # Perform analysis
    result = perform_analysis(component_path, query)
    
    # Cache result
    cache.set(query, result)
    metrics.record_cache_miss("L1", 0.5)
    
    return result

# Batch analysis
components = ["auth/", "db/", "api/"]
for component in components:
    result = analyze_component(
        component,
        f"Analyze {component} for security issues"
    )
    # Results cached for future queries
```

---

## Troubleshooting

### High Token Consumption

**Symptom:** Using more tokens than expected

**Solutions:**
1. Check cache hit rate: `metrics.get_metrics()`
2. Ensure semantic similarity in queries
3. Reference existing docs instead of re-reading
4. Use truncation for large files
5. Batch similar analyses

### Cache Misses

**Symptom:** Low cache hit rate

**Solutions:**
1. Use consistent query phrasing
2. Group similar analyses together
3. Avoid overly specific queries
4. Review L2 cache similarity threshold

### Documentation Drift

**Symptom:** Docs don't match current code

**Solutions:**
1. Update docs immediately after changes
2. Run weekly validation
3. Use incremental updates, not rewrites
4. Cross-reference between docs

---

## Conclusion

This workflow provides a **systematic, token-efficient approach** to repository analysis by:

1. **Progressive depth** - Start broad, go deep incrementally
2. **Aggressive caching** - Reuse analysis across sessions
3. **Documentation-first** - Store findings, reference later
4. **Batch processing** - Group similar analyses
5. **Incremental updates** - Update, don't recreate

**Token savings are workload-dependent; the measured optimizer-compression figure is manifest-backed in `evaluation/results/validation-2026-07-14/`.**

**Key insight:** The knowledge base becomes your cached analysis layer, dramatically reducing tokens for ongoing work.
