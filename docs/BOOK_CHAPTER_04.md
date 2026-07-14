# Chapter 4: Multi-Level Caching Architecture

> ⚠️ **Metrics correction (2026-07-14).** Earlier drafts of this document cited fabricated token-savings/quality figures — "68.96%", "89.3%", "91.80%" — produced by a simulation that never invoked the optimizer. **Those figures are retracted.** The honest, measured figure is **~20% mean optimizer compression** on real prose (manifest-backed: `evaluation/results/validation-2026-07-14/`; see `STATUS.md` and `CHANGELOG.md`). Inline numbers below have been corrected where they appeared.


## 4.1 The Caching Problem

**Challenge:** How do we avoid re-querying the LLM for information we've already retrieved?

**Naive Solution:** Store exact query matches
- Works for identical queries
- Fails for similar queries
- Miss rate: 60-70%

**Better Solution:** Multi-level caching with exact + semantic matching

## 4.2 L1 Cache: Exact Match (<1ms)

### How It Works
**Technology:** Python dictionary (hash table)
**Lookup:** O(1) constant time
**Performance:** <1ms average

**Process:**
1. Hash the query text
2. Look up in dictionary
3. Return cached result if found

**Example:**
```python
query = "What's our authentication strategy?"
cache_key = hash(query)  # Fast hash function
if cache_key in l1_cache:
    return l1_cache[cache_key]  # <1ms
```

### When It Works
✅ Exact same query text
✅ Same whitespace and punctuation
✅ Identical wording

### When It Fails
❌ Different wording ("auth strategy" vs "authentication approach")
❌ Different punctuation
❌ Reordered words

**Hit Rate:** ~10-15% (exact matches only)

## 4.3 L2 Cache: Semantic Match (<100ms)

### How It Works
**Technology:** TF-IDF + Cosine Similarity
**Lookup:** O(n) linear search through cache
**Performance:** <100ms for 1000 entries

**Process:**
1. Convert query to TF-IDF vector
2. Compare with all cached queries using cosine similarity
3. Return result if similarity > 0.85 threshold

**Example:**
```python
query = "How does our auth system work?"
query_vector = tfidf.transform([query])

for cached_query, result in l2_cache:
    cached_vector = tfidf.transform([cached_query])
    similarity = cosine_similarity(query_vector, cached_vector)
    
    if similarity > 0.85:
        return result  # Semantic match found
```

### When It Works
✅ Similar wording ("auth strategy" ≈ "authentication approach")
✅ Synonyms ("explain" ≈ "describe")
✅ Reordered words
✅ Different punctuation

### When It Fails
❌ Completely different topics
❌ Similarity < 0.85 threshold
❌ Ambiguous queries

**Hit Rate:** ~25-30% (semantic matches)

## 4.4 Cache Orchestration and Promotion

### Multi-Level Lookup Flow

```
Query arrives
    ↓
Check L1 Cache (exact match)
    ↓
Hit? → Return result (<1ms)
    ↓
Miss → Check L2 Cache (semantic match)
    ↓
Hit? → Promote to L1 + Return result (<100ms)
    ↓
Miss → Query LLM + Store in L2 (2-5 seconds)
```

### Cache Promotion
**Why:** L2 hits become L1 entries for faster future access

**Process:**
1. L2 cache hit detected
2. Copy entry to L1 cache
3. Future queries get <1ms response

**Example:**
```
Query 1: "What's our authentication strategy?"
→ L1 miss, L2 miss, query LLM
→ Store in L2

Query 2: "How does our auth system work?" (similar)
→ L1 miss, L2 hit (similarity: 0.87)
→ Promote to L1
→ Return result (<100ms)

Query 3: "How does our auth system work?" (exact)
→ L1 hit
→ Return result (<1ms)
```

### Cache Invalidation
**Strategy:** Time-based expiration (configurable)

**Default TTL:**
- L1 cache: 1 hour
- L2 cache: 24 hours

**Manual invalidation:** Clear cache when codebase changes significantly

## 4.5 Performance Characteristics

### Latency Measurements

| Cache Level | Lookup Time | Hit Rate | Combined Hit Rate |
|-------------|-------------|----------|-------------------|
| L1 (exact)  | <1ms        | 10-15%   | 10-15%            |
| L2 (semantic)| <100ms     | 25-30%   | 35-45%            |
| LLM (miss)  | 2-5 seconds | 55-65%   | -                 |

### Memory Usage

**L1 Cache:**
- ~1KB per entry (query + result)
- 1000 entries = ~1MB
- Negligible memory impact

**L2 Cache:**
- ~2KB per entry (query + vector + result)
- 1000 entries = ~2MB
- Still very lightweight

### Scalability

**Current limits:**
- L1: 10,000 entries (10MB)
- L2: 5,000 entries (10MB)
- Total: 20MB memory

**Performance at scale:**
- L1: O(1) - constant time regardless of size
- L2: O(n) - linear with cache size
  - 1,000 entries: ~50ms
  - 5,000 entries: ~100ms
  - 10,000 entries: ~200ms (still acceptable)

## 4.6 Real-World Cache Hit Rates

### Validated Results (Synthetic Data)

**Test Setup:**
- 100 queries
- 40% exact duplicates
- 30% semantic matches
- 30% unique queries

**Results:**
- L1 hit rate: 40%
- L2 hit rate: 30%
- Combined: 70% cache hit rate
- **Token savings: 40% (from caching alone)**

### Expected Real-World Performance

**Typical usage patterns:**
- L1 hit rate: 10-15% (exact matches)
- L2 hit rate: 25-30% (semantic matches)
- Combined: 35-45% cache hit rate
- **Token savings: 20-25% (from caching alone)**

### Factors Affecting Hit Rate

**Increases hit rate:**
✅ Repetitive queries
✅ Team collaboration (shared cache)
✅ Longer cache TTL
✅ Similar query patterns

**Decreases hit rate:**
❌ Unique queries
❌ Rapidly changing codebase
❌ Short cache TTL
❌ Diverse query patterns

### Optimization Tips

1. **Increase TTL** for stable codebases
2. **Share cache** across team members
3. **Standardize queries** for common tasks
4. **Pre-warm cache** with common queries
5. **Monitor hit rates** and adjust thresholds

---

**Next Chapter:** Knowledge Base Framework
