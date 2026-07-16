---
title: "Best Practices Implementation Plan (Historical)"
date: 2026-07-12
status: aspirational
category: planning
note: "Proposed plan from 2026-07-12. Actual implementation status tracked in docs/knowledge-base/research/audit-2026-07-14-signoff.md."
---

# Best Practices Implementation Plan (#7-11)

> ⚠️ **Frozen historical snapshot — retracted metrics.** This is a point-in-time planning/audit-trail document, preserved unedited below for the record. Any token-savings/quality figures it cites — e.g. "68.96%", "89.3%", "91.80%" — were **fabricated** (a simulation that never invoked the optimizer) and are **retracted**; the measured figure is ~20% optimizer compression (manifest-backed: `evaluation/results/validation-2026-07-14/`). See `STATUS.md` and `CHANGELOG.md` for current, provenance-backed numbers.


## Overview

This document outlines the implementation plan for the **missing 30-40%** of Bob Shell token-saving best practices in the Knowledge Manager. These practices represent significant optimization opportunities beyond the current 60-70% coverage.

## Current Implementation Status

### ✅ Implemented (60-70% Coverage)
1. Context Reuse (30-50% savings)
2. Structured Knowledge Storage (20-30% savings)
3. Incremental Updates (15-25% savings)
4. Template Reuse (10-20% savings)
5. Semantic Search (10-15% savings)
6. Quality Metrics (5-10% improvement)

### ❌ Missing (30-40% Additional Potential)
7. Prompt Optimization (20-30% potential)
8. Caching Strategies (15-25% potential)
9. Smart Truncation (10-20% potential)
10. Batch Processing (10-15% potential)
11. Output Format Control (5-10% potential)
12. Model Selection (5-10% cost reduction) - *Likely handled by Bob Shell automatically*

---

## Implementation Plan

### #7: Prompt Optimization (20-30% Potential Savings)

**Goal**: Compress prompts, remove redundancy, use system messages efficiently, batch related queries.

#### Architecture

```python
class PromptOptimizer:
    """Optimize prompts before sending to LLM."""
    
    def __init__(self):
        self.compression_rules = self._load_compression_rules()
        self.system_message_cache = {}
        
    def optimize_prompt(self, prompt: str, context: dict) -> dict:
        """
        Optimize a prompt for token efficiency.
        
        Returns:
            {
                'optimized_prompt': str,
                'system_message': str,
                'tokens_saved': int
            }
        """
        # 1. Remove redundant phrases
        compressed = self._compress_redundancy(prompt)
        
        # 2. Extract reusable context to system message
        system_msg, user_msg = self._extract_system_context(compressed, context)
        
        # 3. Use abbreviations for common terms
        abbreviated = self._apply_abbreviations(user_msg)
        
        # 4. Remove unnecessary formatting
        cleaned = self._remove_formatting_overhead(abbreviated)
        
        return {
            'optimized_prompt': cleaned,
            'system_message': system_msg,
            'tokens_saved': len(prompt) - len(cleaned)
        }
    
    def _compress_redundancy(self, text: str) -> str:
        """Remove redundant phrases and repetition."""
        # Remove phrases like "please", "could you", "I would like"
        # Compress "in order to" → "to"
        # Remove filler words
        pass
    
    def _extract_system_context(self, prompt: str, context: dict) -> tuple:
        """Move reusable context to system message."""
        # Extract project context, coding standards, etc.
        # Put in system message (sent once, not repeated)
        pass
    
    def batch_related_queries(self, queries: list) -> str:
        """Combine related queries into single prompt."""
        # Group similar questions
        # Amortize setup costs
        pass
```

#### Integration Points

1. **Knowledge Manager Mode**: Intercept prompts before sending
2. **Metrics Collection**: Track tokens saved by optimization
3. **A/B Testing**: Compare optimized vs non-optimized results

#### Implementation Steps

1. Create `PromptOptimizer` class in `knowledge_manager/optimizer.py`
2. Add compression rules database (common redundancies)
3. Integrate with Bob Shell prompt pipeline
4. Add metrics tracking for optimization effectiveness
5. Test with real queries to validate quality maintained

#### Expected Impact

- **Token Reduction**: 20-30% on top of existing savings
- **Quality Impact**: Minimal (preserve meaning)
- **Implementation Effort**: 2-3 weeks

---

### #8: Caching Strategies (15-25% Potential Savings)

**Goal**: Cache common responses, reuse embeddings, store intermediate results.

#### Architecture

```python
class ResponseCache:
    """Cache LLM responses and embeddings."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.response_cache = {}  # In-memory cache
        self.embedding_cache = {}  # Vector cache
        self.ttl = 3600  # 1 hour TTL
        
    def get_cached_response(self, prompt_hash: str) -> Optional[str]:
        """Get cached response if available and fresh."""
        if prompt_hash in self.response_cache:
            entry = self.response_cache[prompt_hash]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['response']
        return None
    
    def cache_response(self, prompt: str, response: str):
        """Cache a response with hash key."""
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        self.response_cache[prompt_hash] = {
            'response': response,
            'timestamp': time.time()
        }
        # Persist to disk
        self._save_to_disk(prompt_hash, response)
    
    def get_cached_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get cached embedding vector."""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        if text_hash in self.embedding_cache:
            return self.embedding_cache[text_hash]
        return None
    
    def cache_embedding(self, text: str, embedding: np.ndarray):
        """Cache an embedding vector."""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        self.embedding_cache[text_hash] = embedding
```

#### Cache Strategies

1. **Response Cache**: Exact match on prompt hash
2. **Semantic Cache**: Similar prompts (cosine similarity > 0.95)
3. **Embedding Cache**: Reuse vector representations
4. **Intermediate Results**: Cache partial computations

#### Implementation Steps

1. Create `ResponseCache` class with disk persistence
2. Add semantic similarity matching (fuzzy cache)
3. Integrate with knowledge manager search
4. Add cache invalidation logic (TTL, manual)
5. Monitor cache hit rates and effectiveness

#### Expected Impact

- **Token Reduction**: 15-25% for repeated queries
- **Latency Improvement**: 90% faster for cache hits
- **Implementation Effort**: 2-3 weeks

---

### #9: Smart Truncation (10-20% Potential Savings)

**Goal**: Summarize long contexts, extract key information only, progressive detail loading.

#### Architecture

```python
class SmartTruncator:
    """Intelligently truncate context to essential information."""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.summarizer = self._init_summarizer()
        
    def truncate_context(self, context: str, query: str) -> dict:
        """
        Truncate context intelligently based on query relevance.
        
        Returns:
            {
                'truncated_context': str,
                'tokens_saved': int,
                'relevance_score': float
            }
        """
        # 1. Extract query-relevant sections
        relevant_sections = self._extract_relevant_sections(context, query)
        
        # 2. Summarize less relevant parts
        summarized = self._summarize_background(context, relevant_sections)
        
        # 3. Progressive detail loading
        essential, optional = self._split_by_importance(summarized)
        
        # 4. Fit within token budget
        final_context = self._fit_token_budget(essential, optional)
        
        return {
            'truncated_context': final_context,
            'tokens_saved': len(context) - len(final_context),
            'relevance_score': self._calculate_relevance(final_context, query)
        }
    
    def _extract_relevant_sections(self, context: str, query: str) -> list:
        """Extract sections most relevant to query."""
        # Use semantic similarity
        # Rank sections by relevance
        pass
    
    def _summarize_background(self, context: str, keep_sections: list) -> str:
        """Summarize less relevant background information."""
        # Use extractive summarization
        # Keep key facts, remove details
        pass
```

#### Truncation Strategies

1. **Relevance-Based**: Keep query-relevant sections
2. **Extractive Summarization**: Key sentences only
3. **Progressive Loading**: Essential first, details on demand
4. **Hierarchical**: Summaries at multiple levels

#### Implementation Steps

1. Create `SmartTruncator` class
2. Integrate semantic similarity for relevance scoring
3. Add extractive summarization (TextRank, BERT)
4. Implement progressive detail loading
5. Test on long documents to validate quality

#### Expected Impact

- **Token Reduction**: 10-20% for long contexts
- **Quality Impact**: Minimal (preserve key information)
- **Implementation Effort**: 3-4 weeks

---

### #10: Batch Processing (10-15% Potential Savings)

**Goal**: Group similar tasks, amortize setup costs, parallel processing.

#### Architecture

```python
class BatchProcessor:
    """Process multiple related tasks efficiently."""
    
    def __init__(self):
        self.batch_queue = []
        self.batch_size = 5
        self.batch_timeout = 30  # seconds
        
    def add_task(self, task: dict):
        """Add task to batch queue."""
        self.batch_queue.append(task)
        
        if len(self.batch_queue) >= self.batch_size:
            self._process_batch()
    
    def _process_batch(self):
        """Process queued tasks as a batch."""
        # 1. Group by similarity
        groups = self._group_similar_tasks(self.batch_queue)
        
        # 2. Create combined prompt
        for group in groups:
            combined_prompt = self._create_batch_prompt(group)
            
            # 3. Single LLM call for all tasks
            response = self._call_llm(combined_prompt)
            
            # 4. Parse and distribute results
            results = self._parse_batch_response(response, group)
            self._distribute_results(results)
        
        self.batch_queue = []
    
    def _group_similar_tasks(self, tasks: list) -> list:
        """Group tasks by similarity."""
        # Cluster by task type, scenario, context
        pass
    
    def _create_batch_prompt(self, tasks: list) -> str:
        """Create single prompt for multiple tasks."""
        # Shared context once
        # Individual questions numbered
        pass
```

#### Batch Strategies

1. **Time-Based**: Batch tasks within time window
2. **Size-Based**: Batch when queue reaches threshold
3. **Similarity-Based**: Group related tasks
4. **Parallel Execution**: Process independent batches concurrently

#### Implementation Steps

1. Create `BatchProcessor` class with queue management
2. Add task similarity clustering
3. Implement batch prompt generation
4. Add response parsing and distribution
5. Test with various task types

#### Expected Impact

- **Token Reduction**: 10-15% by amortizing setup
- **Throughput**: 2-3x for batchable tasks
- **Implementation Effort**: 2 weeks

---

### #11: Output Format Control (5-10% Potential Savings)

**Goal**: Request concise formats, limit verbosity, use structured outputs (JSON).

#### Architecture

```python
class OutputFormatter:
    """Control LLM output format for efficiency."""
    
    def __init__(self):
        self.format_templates = self._load_templates()
        
    def request_structured_output(self, prompt: str, format_type: str) -> str:
        """Request specific output format."""
        format_instructions = self.format_templates[format_type]
        
        enhanced_prompt = f"""
{prompt}

OUTPUT FORMAT:
{format_instructions}

IMPORTANT: Respond ONLY in the specified format. No additional explanation.
"""
        return enhanced_prompt
    
    def get_json_format(self, schema: dict) -> str:
        """Request JSON output with schema."""
        return f"""
Respond in JSON format matching this schema:
{json.dumps(schema, indent=2)}

No markdown, no explanation, just valid JSON.
"""
    
    def get_concise_format(self) -> str:
        """Request concise output."""
        return """
Be extremely concise:
- Use bullet points
- No introductions or conclusions
- Facts only, no elaboration
- Maximum 3 sentences per point
"""
```

#### Format Strategies

1. **JSON Output**: Structured data, no prose
2. **Bullet Points**: Concise lists
3. **Tables**: Compact representation
4. **Code Only**: No explanations for code tasks
5. **Yes/No**: Binary responses when appropriate

#### Implementation Steps

1. Create `OutputFormatter` class with templates
2. Add format instructions to prompts
3. Validate output format compliance
4. Add format-specific parsers
5. Test across different task types

#### Expected Impact

- **Token Reduction**: 5-10% by reducing verbosity
- **Parsing**: Easier with structured formats
- **Implementation Effort**: 1-2 weeks

---

## Implementation Priority

### Phase 1 (Highest Impact, 3 months)
1. **Caching Strategies** (#8) - 15-25% savings, quick wins
2. **Prompt Optimization** (#7) - 20-30% savings, broad impact
3. **Output Format Control** (#11) - 5-10% savings, easy to implement

### Phase 2 (Medium Impact, 2 months)
4. **Smart Truncation** (#9) - 10-20% savings, complex but valuable
5. **Batch Processing** (#10) - 10-15% savings, workflow dependent

### Phase 3 (Validation & Optimization, 1 month)
6. A/B testing and metrics collection
7. Fine-tuning based on real usage
8. Documentation and training

---

## Success Metrics

### Token Efficiency
- **Target**: Additional 30-40% reduction beyond current 60%
- **Measurement**: Tokens per task (control vs optimized)
- **Goal**: Achieve 80-90% total optimization coverage

### Quality Maintenance
- **Target**: No degradation in output quality
- **Measurement**: Quality scores (completeness, accuracy, consistency, usability)
- **Goal**: Maintain or improve current 90+ scores

### Performance
- **Target**: Faster response times with caching
- **Measurement**: Latency (p50, p95, p99)
- **Goal**: 50% reduction for cached queries

### Cost Savings
- **Target**: Proportional to token reduction
- **Measurement**: Bobcoin cost per task
- **Goal**: 30-40% additional cost reduction

---

## Risk Mitigation

### Quality Risks
- **Risk**: Aggressive optimization degrades output quality
- **Mitigation**: A/B testing, gradual rollout, quality monitoring

### Complexity Risks
- **Risk**: Implementation complexity delays delivery
- **Mitigation**: Phased approach, MVP first, iterate

### Adoption Risks
- **Risk**: Users don't adopt new features
- **Mitigation**: Transparent benefits, easy opt-in, clear documentation

---

## Conclusion

Implementing best practices #7-11 represents a **30-40% additional optimization opportunity** beyond the current 60-70% coverage. The phased implementation plan prioritizes high-impact, lower-complexity features first (caching, prompt optimization) before tackling more complex features (smart truncation, batch processing).

**Total Expected Impact:**
- Current: 60-70% optimization coverage
- After Implementation: 80-90% optimization coverage
- Additional Token Savings: 30-40%
- Total Token Savings: 70-80% vs baseline

This would position the Knowledge Manager as a **best-in-class** token optimization solution for Bob Shell users.
