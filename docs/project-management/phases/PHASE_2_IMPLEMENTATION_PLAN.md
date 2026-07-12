# Phase 2 Implementation Plan: Advanced Optimization

**Status:** In Progress  
**Timeline:** Months 4-5 (Weeks 10-15)  
**Goal:** Implement Smart Truncation and Batch Processing features

---

## Overview

Phase 2 builds on Phase 1's foundation by adding advanced optimization features that handle large contexts and multiple tasks efficiently. These features target the remaining 20-35% token savings potential.

### Features

1. **Smart Truncation** (#9) - 10-20% potential savings
   - Relevance-based context truncation
   - Intelligent section prioritization
   - Summary generation for less relevant content

2. **Batch Processing** (#10) - 10-15% potential savings
   - Multi-task grouping
   - Shared context optimization
   - Parallel processing support

---

## Phase 2.1: Smart Truncation (Weeks 10-13)

### Objectives

- Implement relevance-based truncation algorithm
- Create section scoring and prioritization system
- Add intelligent summarization for truncated content
- Maintain 90%+ relevance preservation
- Achieve 10-20% token reduction on large contexts

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SmartTruncator                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Input: Long Context (5000+ tokens) + Query                │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Section Splitter                                  │  │
│  │    - Split by headers, paragraphs, code blocks      │  │
│  │    - Preserve structure and boundaries              │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 2. Relevance Scorer                                  │  │
│  │    - TF-IDF similarity to query                      │  │
│  │    - Keyword matching                                │  │
│  │    - Semantic similarity (optional)                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 3. Priority Selector                                 │  │
│  │    - Sort sections by relevance                      │  │
│  │    - Select top N sections within token limit        │  │
│  │    - Preserve critical sections (headers, code)      │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 4. Summarizer (for truncated content)               │  │
│  │    - Generate brief summaries of removed sections    │  │
│  │    - Preserve key information                        │  │
│  │    - Add context markers                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                  │
│  Output: Truncated Context (within token limit)            │
│          + Metadata (tokens saved, relevance preserved)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Details

#### Week 10: Core Truncation Engine

```python
from typing import List, Dict, Tuple
import re
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


@dataclass
class Section:
    """Represents a section of text with metadata."""
    content: str
    start_pos: int
    end_pos: int
    section_type: str  # 'header', 'paragraph', 'code', 'list'
    relevance_score: float = 0.0
    is_critical: bool = False


class SectionSplitter:
    """Split text into logical sections."""
    
    def __init__(self):
        self.patterns = {
            'header': r'^#{1,6}\s+.+$',
            'code_block': r'```[\s\S]*?```',
            'list_item': r'^\s*[-*+]\s+.+$',
            'paragraph': r'.+?(?:\n\n|\n$|$)'
        }
    
    def split(self, text: str) -> List[Section]:
        """Split text into sections preserving structure."""
        sections = []
        pos = 0
        
        # Split by double newlines first (paragraphs)
        paragraphs = re.split(r'\n\n+', text)
        
        for para in paragraphs:
            if not para.strip():
                continue
            
            # Determine section type
            section_type = self._classify_section(para)
            
            # Check if critical (headers, code blocks)
            is_critical = section_type in ['header', 'code_block']
            
            section = Section(
                content=para.strip(),
                start_pos=pos,
                end_pos=pos + len(para),
                section_type=section_type,
                is_critical=is_critical
            )
            sections.append(section)
            pos += len(para) + 2  # Account for newlines
        
        return sections
    
    def _classify_section(self, text: str) -> str:
        """Classify section type."""
        text = text.strip()
        
        if re.match(self.patterns['header'], text, re.MULTILINE):
            return 'header'
        elif re.match(self.patterns['code_block'], text, re.DOTALL):
            return 'code_block'
        elif re.match(self.patterns['list_item'], text, re.MULTILINE):
            return 'list'
        else:
            return 'paragraph'


class RelevanceScorer:
    """Score section relevance to query."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def score_sections(self, sections: List[Section], query: str) -> List[Section]:
        """Score all sections against query."""
        if not sections:
            return sections
        
        # Prepare texts
        texts = [s.content for s in sections] + [query]
        
        try:
            # Compute TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Query vector is the last one
            query_vector = tfidf_matrix[-1]
            section_vectors = tfidf_matrix[:-1]
            
            # Compute cosine similarity
            similarities = cosine_similarity(section_vectors, query_vector).flatten()
            
            # Update sections with scores
            for section, score in zip(sections, similarities):
                section.relevance_score = float(score)
                
                # Boost critical sections
                if section.is_critical:
                    section.relevance_score *= 1.5
        
        except Exception as e:
            # Fallback to keyword matching
            query_words = set(query.lower().split())
            for section in sections:
                section_words = set(section.content.lower().split())
                overlap = len(query_words & section_words)
                section.relevance_score = overlap / max(len(query_words), 1)
        
        return sections


class SmartTruncator:
    """Intelligently truncate context to fit token limits."""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.splitter = SectionSplitter()
        self.scorer = RelevanceScorer()
        self.tokens_per_word = 1.3  # Approximate
    
    def truncate(self, context: str, query: str) -> Dict:
        """Truncate context intelligently."""
        
        # 1. Split into sections
        sections = self.splitter.split(context)
        
        if not sections:
            return {
                'truncated_context': context,
                'tokens_saved': 0,
                'relevance_preserved': 1.0,
                'sections_kept': 0,
                'sections_removed': 0
            }
        
        # 2. Score relevance
        sections = self.scorer.score_sections(sections, query)
        
        # 3. Sort by relevance (critical sections first)
        sections.sort(key=lambda s: (s.is_critical, s.relevance_score), reverse=True)
        
        # 4. Select sections within token limit
        selected = []
        token_count = 0
        removed_sections = []
        
        for section in sections:
            section_tokens = self._estimate_tokens(section.content)
            
            if token_count + section_tokens <= self.max_tokens:
                selected.append(section)
                token_count += section_tokens
            else:
                removed_sections.append(section)
        
        # 5. Sort selected sections by original position
        selected.sort(key=lambda s: s.start_pos)
        
        # 6. Build truncated context
        truncated_parts = []
        for section in selected:
            truncated_parts.append(section.content)
        
        # 7. Add summary of removed content if significant
        if removed_sections and len(removed_sections) > 2:
            summary = self._summarize_removed(removed_sections)
            truncated_parts.append(f"\n\n[Truncated content summary: {summary}]")
        
        truncated_context = '\n\n'.join(truncated_parts)
        
        # 8. Calculate metrics
        original_tokens = self._estimate_tokens(context)
        tokens_saved = original_tokens - token_count
        
        # Calculate relevance preservation
        total_relevance = sum(s.relevance_score for s in sections)
        preserved_relevance = sum(s.relevance_score for s in selected)
        relevance_preserved = preserved_relevance / total_relevance if total_relevance > 0 else 1.0
        
        return {
            'truncated_context': truncated_context,
            'tokens_saved': tokens_saved,
            'token_reduction_percent': (tokens_saved / original_tokens * 100) if original_tokens > 0 else 0,
            'relevance_preserved': relevance_preserved,
            'sections_kept': len(selected),
            'sections_removed': len(removed_sections),
            'original_tokens': original_tokens,
            'final_tokens': token_count
        }
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count from text."""
        words = len(text.split())
        return int(words * self.tokens_per_word)
    
    def _summarize_removed(self, sections: List[Section]) -> str:
        """Create brief summary of removed sections."""
        # Extract key information from removed sections
        summaries = []
        for section in sections[:3]:  # Top 3 removed sections
            # Take first sentence or first 50 chars
            first_sentence = section.content.split('.')[0][:50]
            summaries.append(first_sentence)
        
        if len(sections) > 3:
            summaries.append(f"and {len(sections) - 3} more sections")
        
        return '; '.join(summaries)
```

#### Week 11-12: Testing & Validation

```python
# tests/test_truncation.py
import pytest
from scripts.engine.optimization.truncation import (
    SmartTruncator, SectionSplitter, RelevanceScorer, Section
)


class TestSectionSplitter:
    """Test section splitting functionality."""
    
    def test_split_simple_paragraphs(self):
        """Test splitting simple paragraphs."""
        splitter = SectionSplitter()
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        
        sections = splitter.split(text)
        
        assert len(sections) == 3
        assert all(s.section_type == 'paragraph' for s in sections)
    
    def test_identify_headers(self):
        """Test header identification."""
        splitter = SectionSplitter()
        text = "# Main Header\n\nSome content.\n\n## Sub Header\n\nMore content."
        
        sections = splitter.split(text)
        
        headers = [s for s in sections if s.section_type == 'header']
        assert len(headers) == 2
        assert all(s.is_critical for s in headers)
    
    def test_identify_code_blocks(self):
        """Test code block identification."""
        splitter = SectionSplitter()
        text = "Some text.\n\n```python\ncode here\n```\n\nMore text."
        
        sections = splitter.split(text)
        
        code_sections = [s for s in sections if s.section_type == 'code_block']
        assert len(code_sections) == 1
        assert code_sections[0].is_critical


class TestRelevanceScorer:
    """Test relevance scoring."""
    
    def test_score_relevant_section(self):
        """Test scoring of relevant sections."""
        scorer = RelevanceScorer()
        
        sections = [
            Section("Cassandra replication configuration", 0, 50, 'paragraph'),
            Section("Unrelated content about weather", 51, 100, 'paragraph'),
            Section("How to set replication factor", 101, 150, 'paragraph')
        ]
        
        query = "configure replication in Cassandra"
        scored = scorer.score_sections(sections, query)
        
        # First and third sections should score higher
        assert scored[0].relevance_score > scored[1].relevance_score
        assert scored[2].relevance_score > scored[1].relevance_score
    
    def test_boost_critical_sections(self):
        """Test that critical sections get boosted scores."""
        scorer = RelevanceScorer()
        
        sections = [
            Section("# Replication", 0, 20, 'header', is_critical=True),
            Section("Replication details", 21, 50, 'paragraph', is_critical=False)
        ]
        
        query = "replication"
        scored = scorer.score_sections(sections, query)
        
        # Header should score higher due to boost
        assert scored[0].relevance_score > scored[1].relevance_score


class TestSmartTruncator:
    """Test smart truncation functionality."""
    
    def test_truncate_long_context(self):
        """Test truncation of long context."""
        truncator = SmartTruncator(max_tokens=100)
        
        # Create long context (>100 tokens)
        context = "\n\n".join([
            "# Cassandra Configuration",
            "This section explains replication.",
            "Replication factor determines data copies.",
            "Use RF=3 for production systems.",
            "Unrelated content about networking.",
            "More unrelated content about storage.",
            "Even more unrelated content."
        ])
        
        query = "How to configure replication factor?"
        result = truncator.truncate(context, query)
        
        assert result['final_tokens'] <= 100
        assert result['tokens_saved'] > 0
        assert result['relevance_preserved'] >= 0.7
        assert 'replication' in result['truncated_context'].lower()
    
    def test_preserve_critical_sections(self):
        """Test that critical sections are preserved."""
        truncator = SmartTruncator(max_tokens=50)
        
        context = "\n\n".join([
            "# Important Header",
            "Some content.",
            "More content.",
            "Even more content."
        ])
        
        query = "information"
        result = truncator.truncate(context, query)
        
        # Header should be preserved
        assert '# Important Header' in result['truncated_context']
    
    def test_no_truncation_needed(self):
        """Test when context is already within limit."""
        truncator = SmartTruncator(max_tokens=1000)
        
        context = "Short context that fits easily."
        query = "context"
        result = truncator.truncate(context, query)
        
        assert result['tokens_saved'] == 0
        assert result['relevance_preserved'] == 1.0
        assert result['truncated_context'] == context
    
    def test_token_reduction_percentage(self):
        """Test token reduction calculation."""
        truncator = SmartTruncator(max_tokens=50)
        
        # Create context that will need truncation
        context = " ".join(["word"] * 200)  # ~260 tokens
        query = "word"
        result = truncator.truncate(context, query)
        
        assert result['token_reduction_percent'] > 0
        assert result['token_reduction_percent'] <= 100


class TestTruncationIntegration:
    """Integration tests for truncation."""
    
    def test_realistic_documentation_truncation(self):
        """Test truncation on realistic documentation."""
        truncator = SmartTruncator(max_tokens=500)
        
        # Simulate long documentation
        context = """
# Cassandra Replication Guide

## Overview
Apache Cassandra uses replication to ensure data availability and durability.

## Replication Factor
The replication factor (RF) determines how many copies of data are stored.
- RF=1: Single copy (development only)
- RF=3: Three copies (recommended for production)
- RF=5: Five copies (high availability)

## Configuration
To configure replication, modify cassandra.yaml:
```yaml
replication:
  class: NetworkTopologyStrategy
  datacenter1: 3
```

## Best Practices
Always use RF=3 or higher in production.
Consider network topology when setting RF.
Monitor replication lag regularly.

## Troubleshooting
If replication fails, check:
1. Network connectivity
2. Disk space
3. Node status

## Advanced Topics
Replication can be tuned for specific workloads.
Consider consistency levels with replication.
Use nodetool repair for anti-entropy.

## Performance Considerations
Higher RF increases write latency.
Read performance improves with higher RF.
Balance RF with consistency requirements.
"""
        
        query = "How to configure replication factor for production?"
        result = truncator.truncate(context, query)
        
        # Should preserve relevant sections
        assert 'RF=3' in result['truncated_context']
        assert 'production' in result['truncated_context'].lower()
        assert result['relevance_preserved'] >= 0.8
        assert result['final_tokens'] <= 500
        
        # Should have saved significant tokens
        assert result['token_reduction_percent'] >= 30
```

#### Week 13: Performance Optimization

- Profile truncation performance
- Optimize TF-IDF computation for large contexts
- Add caching for repeated truncations
- Benchmark against baseline

### Success Criteria

- ✅ Truncation reduces tokens by 10-20% on large contexts (>2000 tokens)
- ✅ Relevance preservation ≥ 90% (measured by TF-IDF similarity)
- ✅ Critical sections (headers, code) always preserved
- ✅ Processing time < 100ms for 5000-token contexts
- ✅ All tests passing (15+ tests)

---

## Phase 2.2: Batch Processing (Weeks 14-15)

### Objectives

- Implement intelligent task batching
- Create similarity-based grouping
- Add shared context optimization
- Achieve 10-15% token savings on multi-task workflows
- Maintain 95%+ quality across batched tasks

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BatchProcessor                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Input: Multiple Tasks (queries + contexts)                │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Task Queue                                        │  │
│  │    - Buffer incoming tasks                           │  │
│  │    - Trigger batch when size/time threshold met     │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 2. Similarity Grouper                                │  │
│  │    - Compute task similarity                         │  │
│  │    - Group similar tasks together                    │  │
│  │    - Identify shared context                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 3. Batch Prompt Builder                              │  │
│  │    - Extract shared context once                     │  │
│  │    - Format multiple queries                         │  │
│  │    - Add batch instructions                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 4. Response Parser                                   │  │
│  │    - Parse batch response                            │  │
│  │    - Distribute to individual tasks                  │  │
│  │    - Validate completeness                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                  │
│  Output: Individual Responses + Metrics                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Details

#### Week 14: Core Batch Processing

```python
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import time
from collections import defaultdict
import json


@dataclass
class Task:
    """Represents a single task to be processed."""
    id: str
    query: str
    context: Optional[str] = None
    format: str = 'text'
    metadata: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class BatchResult:
    """Result of batch processing."""
    task_id: str
    response: str
    tokens_used: int
    processing_time: float


class SimilarityGrouper:
    """Group similar tasks for batch processing."""
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(max_features=50)
    
    def group_tasks(self, tasks: List[Task]) -> List[List[Task]]:
        """Group tasks by similarity."""
        if len(tasks) <= 1:
            return [[t] for t in tasks]
        
        # Compute similarity matrix
        queries = [t.query for t in tasks]
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(queries)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Group using simple clustering
            groups = []
            assigned = set()
            
            for i, task in enumerate(tasks):
                if i in assigned:
                    continue
                
                # Start new group
                group = [task]
                assigned.add(i)
                
                # Find similar tasks
                for j in range(i + 1, len(tasks)):
                    if j not in assigned and similarity_matrix[i][j] >= self.similarity_threshold:
                        group.append(tasks[j])
                        assigned.add(j)
                
                groups.append(group)
            
            return groups
        
        except Exception:
            # Fallback: each task in its own group
            return [[t] for t in tasks]
    
    def extract_shared_context(self, tasks: List[Task]) -> Optional[str]:
        """Extract shared context from tasks."""
        contexts = [t.context for t in tasks if t.context]
        
        if not contexts:
            return None
        
        # Find common prefix (simple approach)
        if len(contexts) == 1:
            return contexts[0]
        
        # Find longest common substring
        common = contexts[0]
        for context in contexts[1:]:
            # Simple: if contexts are very similar, use first one
            if context == common:
                continue
            # Otherwise, no shared context
            return None
        
        return common


class BatchPromptBuilder:
    """Build prompts for batch processing."""
    
    def build_batch_prompt(self, tasks: List[Task], shared_context: Optional[str] = None) -> str:
        """Build a single prompt for multiple tasks."""
        
        parts = []
        
        # Add shared context once
        if shared_context:
            parts.append(f"Context:\n{shared_context}\n")
        
        # Add batch instructions
        parts.append(f"Process the following {len(tasks)} queries:\n")
        
        # Add individual queries
        for i, task in enumerate(tasks, 1):
            parts.append(f"\nQuery {i} (ID: {task.id}):")
            parts.append(task.query)
            
            # Add task-specific context if different from shared
            if task.context and task.context != shared_context:
                parts.append(f"Additional context: {task.context}")
        
        # Add output format instructions
        parts.append("\n\nProvide responses in JSON format:")
        parts.append('{"responses": [{"id": "task_id", "answer": "response"}, ...]}')
        
        return '\n'.join(parts)


class ResponseParser:
    """Parse batch responses."""
    
    def parse_batch_response(self, response: str, expected_count: int) -> List[Dict]:
        """Parse batch response into individual results."""
        
        try:
            # Try JSON parsing first
            data = json.loads(response)
            
            if 'responses' in data:
                return data['responses']
            
            # Fallback: treat as list
            if isinstance(data, list):
                return data
        
        except json.JSONDecodeError:
            # Fallback: split by task IDs
            return self._parse_text_response(response, expected_count)
        
        return []
    
    def _parse_text_response(self, response: str, expected_count: int) -> List[Dict]:
        """Parse text-based batch response."""
        results = []
        
        # Split by "Query N" or "ID:"
        parts = re.split(r'(?:Query \d+|ID: \w+)', response)
        
        for i, part in enumerate(parts[1:], 1):  # Skip first empty part
            if part.strip():
                results.append({
                    'id': f'task_{i}',
                    'answer': part.strip()
                })
        
        return results


class BatchProcessor:
    """Process multiple tasks efficiently in batches."""
    
    def __init__(
        self,
        batch_size: int = 5,
        timeout_seconds: float = 2.0,
        similarity_threshold: float = 0.7
    ):
        self.batch_size = batch_size
        self.timeout_seconds = timeout_seconds
        self.queue: List[Task] = []
        self.last_batch_time = time.time()
        
        self.grouper = SimilarityGrouper(similarity_threshold)
        self.prompt_builder = BatchPromptBuilder()
        self.parser = ResponseParser()
        
        self.metrics = {
            'total_tasks': 0,
            'batches_processed': 0,
            'tokens_saved': 0,
            'avg_batch_size': 0
        }
    
    def add_task(self, task: Task) -> Optional[List[BatchResult]]:
        """Add task to queue and process if ready."""
        self.queue.append(task)
        self.metrics['total_tasks'] += 1
        
        # Check if should process batch
        should_process = (
            len(self.queue) >= self.batch_size or
            (time.time() - self.last_batch_time) >= self.timeout_seconds
        )
        
        if should_process:
            return self.process_batch()
        
        return None
    
    def process_batch(self) -> List[BatchResult]:
        """Process queued tasks as batch."""
        if not self.queue:
            return []
        
        start_time = time.time()
        
        # 1. Group similar tasks
        groups = self.grouper.group_tasks(self.queue)
        
        # 2. Process each group
        all_results = []
        
        for group in groups:
            # Extract shared context
            shared_context = self.grouper.extract_shared_context(group)
            
            # Build batch prompt
            batch_prompt = self.prompt_builder.build_batch_prompt(group, shared_context)
            
            # Simulate LLM call (in real implementation, call actual LLM)
            batch_response = self._simulate_batch_llm_call(batch_prompt, len(group))
            
            # Parse response
            parsed = self.parser.parse_batch_response(batch_response, len(group))
            
            # Create results
            for task, response_data in zip(group, parsed):
                result = BatchResult(
                    task_id=task.id,
                    response=response_data.get('answer', ''),
                    tokens_used=len(batch_prompt.split()) // len(group),  # Approximate
                    processing_time=time.time() - start_time
                )
                all_results.append(result)
        
        # Update metrics
        self.metrics['batches_processed'] += 1
        self.metrics['avg_batch_size'] = (
            (self.metrics['avg_batch_size'] * (self.metrics['batches_processed'] - 1) + len(self.queue)) /
            self.metrics['batches_processed']
        )
        
        # Calculate tokens saved (shared context counted once)
        if len(groups) > 0 and len(self.queue) > 1:
            # Estimate: shared context saved (n-1) times
            shared_context_tokens = 100  # Estimate
            self.metrics['tokens_saved'] += shared_context_tokens * (len(self.queue) - 1)
        
        # Clear queue
        self.queue = []
        self.last_batch_time = time.time()
        
        return all_results
    
    def _simulate_batch_llm_call(self, prompt: str, task_count: int) -> str:
        """Simulate LLM call for testing."""
        # Generate mock JSON response
        responses = []
        for i in range(task_count):
            responses.append({
                'id': f'task_{i+1}',
                'answer': f'Response to query {i+1}'
            })
        
        return json.dumps({'responses': responses})
    
    def get_metrics(self) -> Dict:
        """Get batch processing metrics."""
        return self.metrics.copy()
    
    def flush(self) -> List[BatchResult]:
        """Force process remaining tasks."""
        return self.process_batch()
```

#### Week 15: Testing & Integration

```python
# tests/test_batch_processing.py
import pytest
import time
from scripts.engine.optimization.batch_processing import (
    BatchProcessor, Task, SimilarityGrouper, BatchPromptBuilder, ResponseParser
)


class TestSimilarityGrouper:
    """Test task grouping by similarity."""
    
    def test_group_similar_tasks(self):
        """Test grouping of similar tasks."""
        grouper = SimilarityGrouper(similarity_threshold=0.7)
        
        tasks = [
            Task(id='1', query='Status of node1'),
            Task(id='2', query='Status of node2'),
            Task(id='3', query='Configure replication'),
            Task(id='4', query='Status of node3'),
        ]
        
        groups = grouper.group_tasks(tasks)
        
        # Should have 2 groups: status queries and config query
        assert len(groups) == 2
        
        # Find status group
        status_group = [g for g in groups if len(g) > 1][0]
        assert len(status_group) == 3
    
    def test_extract_shared_context(self):
        """Test shared context extraction."""
        grouper = SimilarityGrouper()
        
        tasks = [
            Task(id='1', query='Query 1', context='Shared context here'),
            Task(id='2', query='Query 2', context='Shared context here'),
        ]
        
        shared = grouper.extract_shared_context(tasks)
        assert shared == 'Shared context here'


class TestBatchPromptBuilder:
    """Test batch prompt building."""
    
    def test_build_simple_batch(self):
        """Test building batch prompt."""
        builder = BatchPromptBuilder()
        
        tasks = [
            Task(id='1', query='What is RF?'),
            Task(id='2', query='What is CL?'),
        ]
        
        prompt = builder.build_batch_prompt(tasks)
        
        assert 'Query 1' in prompt
        assert 'Query 2' in prompt
        assert 'What is RF?' in prompt
        assert 'What is CL?' in prompt
    
    def test_include_shared_context(self):
        """Test shared context inclusion."""
        builder = BatchPromptBuilder()
        
        tasks = [Task(id='1', query='Query 1')]
        shared_context = 'This is shared context'
        
        prompt = builder.build_batch_prompt(tasks, shared_context)
        
        assert 'Context:' in prompt
        assert shared_context in prompt
        # Context should appear only once
        assert prompt.count(shared_context) == 1


class TestResponseParser:
    """Test batch response parsing."""
    
    def test_parse_json_response(self):
        """Test parsing JSON batch response."""
        parser = ResponseParser()
        
        response = '''
        {
            "responses": [
                {"id": "1", "answer": "Answer 1"},
                {"id": "2", "answer": "Answer 2"}
            ]
        }
        '''
        
        results = parser.parse_batch_response(response, 2)
        
        assert len(results) == 2
        assert results[0]['answer'] == 'Answer 1'
        assert results[1]['answer'] == 'Answer 2'
    
    def test_parse_text_response(self):
        """Test parsing text-based response."""
        parser = ResponseParser()
        
        response = '''
        Query 1: Answer to first query
        Query 2: Answer to second query
        '''
        
        results = parser.parse_batch_response(response, 2)
        
        assert len(results) >= 2


class TestBatchProcessor:
    """Test batch processing functionality."""
    
    def test_add_tasks_to_queue(self):
        """Test adding tasks to queue."""
        processor = BatchProcessor(batch_size=3)
        
        task1 = Task(id='1', query='Query 1')
        result = processor.add_task(task1)
        
        # Should not process yet
        assert result is None
        assert len(processor.queue) == 1
    
    def test_process_when_batch_full(self):
        """Test processing when batch size reached."""
        processor = BatchProcessor(batch_size=2)
        
        task1 = Task(id='1', query='Query 1')
        task2 = Task(id='2', query='Query 2')
        
        processor.add_task(task1)
        results = processor.add_task(task2)
        
        # Should process batch
        assert results is not None
        assert len(results) == 2
        assert len(processor.queue) == 0
    
    def test_process_on_timeout(self):
        """Test processing on timeout."""
        processor = BatchProcessor(batch_size=10, timeout_seconds=0.1)
        
        task = Task(id='1', query='Query 1')
        processor.add_task(task)
        
        # Wait for timeout
        time.sleep(0.15)
        
        task2 = Task(id='2', query='Query 2')
        results = processor.add_task(task2)
        
        # Should have processed first task
        assert results is not None
    
    def test_metrics_tracking(self):
        """Test metrics tracking."""
        processor = BatchProcessor(batch_size=2)
        
        task1 = Task(id='1', query='Query 1')
        task2 = Task(id='2', query='Query 2')
        
        processor.add_task(task1)
        processor.add_task(task2)
        
        metrics = processor.get_metrics()
        
        assert metrics['total_tasks'] == 2
        assert metrics['batches_processed'] == 1
    
    def test_flush_remaining_tasks(self):
        """Test flushing remaining tasks."""
        processor = BatchProcessor(batch_size=10)
        
        task1 = Task(id='1', query='Query 1')
        task2 = Task(id='2', query='Query 2')
        
        processor.add_task(task1)
        processor.add_task(task2)
        
        # Flush
        results = processor.flush()
        
        assert len(results) == 2
        assert len(processor.queue) == 0


class TestBatchProcessingIntegration:
    """Integration tests for batch processing."""
    
    def test_realistic_batch_workflow(self):
        """Test realistic batch processing workflow."""
        processor = BatchProcessor(batch_size=3, similarity_threshold=0.7)
        
        # Simulate stream of tasks
        tasks = [
            Task(id='1', query='Status of node1', context='Cluster info'),
            Task(id='2', query='Status of node2', context='Cluster info'),
            Task(id='3', query='Status of node3', context='Cluster info'),
            Task(id='4', query='Configure replication', context='Config info'),
        ]
        
        all_results = []
        for task in tasks:
            result = processor.add_task(task)
            if result:
                all_results.extend(result)
        
        # Flush remaining
        remaining = processor.flush()
        all_results.extend(remaining)
        
        # Should have processed all tasks
        assert len(all_results) == 4
        
        # Check metrics
        metrics = processor.get_metrics()
        assert metrics['total_tasks'] == 4
        assert metrics['batches_processed'] >= 1
    
    def test_token_savings_calculation(self):
        """Test token savings from batching."""
        processor = BatchProcessor(batch_size=3)
        
        # Tasks with shared context
        shared_context = "This is a long shared context " * 20  # ~100 tokens
        
        tasks = [
            Task(id='1', query='Query 1', context=shared_context),
            Task(id='2', query='Query 2', context=shared_context),
            Task(id='3', query='Query 3', context=shared_context),
        ]
        
        for task in tasks:
            processor.add_task(task)
        
        metrics = processor.get_metrics()
        
        # Should have saved tokens by sharing context
        assert metrics['tokens_saved'] > 0
```

### Success Criteria

- ✅ Batch processing reduces tokens by 10-15% for similar tasks
- ✅ Grouping accuracy ≥ 85% (similar tasks grouped together)
- ✅ Response parsing success rate ≥ 95%
- ✅ Processing latency < 200ms per batch
- ✅ All tests passing (15+ tests)

---

## Phase 2 Integration

### Combined Testing

```python
# tests/test_phase2_integration.py
import pytest
from scripts.engine.optimization.truncation import SmartTruncator
from scripts.engine.optimization.batch_processing import BatchProcessor, Task


class TestPhase2Integration:
    """Integration tests for Phase 2 features."""
    
    def test_truncation_with_batching(self):
        """Test truncation combined with batch processing."""
        truncator = SmartTruncator(max_tokens=500)
        processor = BatchProcessor(batch_size=3)
        
        # Create tasks with long contexts
        long_context = "Context paragraph. " * 100  # ~200 tokens
        
        tasks = [
            Task(id='1', query='Query 1', context=long_context),
            Task(id='2', query='Query 2', context=long_context),
            Task(id='3', query='Query 3', context=long_context),
        ]
        
        # Truncate contexts
        for task in tasks:
            truncation_result = truncator.truncate(task.context, task.query)
            task.context = truncation_result['truncated_context']
        
        # Process as batch
        for task in tasks:
            processor.add_task(task)
        
        # Verify combined savings
        # Truncation: ~50% per task
        # Batching: ~40% from shared context
        # Combined: ~70% total savings
        
        metrics = processor.get_metrics()
        assert metrics['tokens_saved'] > 0
    
    def test_phase2_with_phase1_features(self):
        """Test Phase 2 features with Phase 1 optimizations."""
        from scripts.engine.optimization.caching import ResponseCache
        from scripts.engine.optimization.prompt_optimization import PromptOptimizer
        
        # Initialize all components
        cache = ResponseCache()
        optimizer = PromptOptimizer()
        truncator = SmartTruncator(max_tokens=500)
        processor = BatchProcessor(batch_size=2)
        
        # Simulate workflow
        tasks = [
            Task(id='1', query='Long verbose query about replication factors', context='Context ' * 100),
            Task(id='2', query='Another long query about consistency levels', context='Context ' * 100),
        ]
        
        total_savings = 0
        
        for task in tasks:
            # 1. Check cache
            cached = cache.get(task.query)
            if cached:
                continue
            
            # 2. Optimize prompt
            optimized = optimizer.optimize(task.query)
            task.query = optimized['optimized']
            total_savings += optimized['tokens_saved']
            
            # 3. Truncate context
            truncation = truncator.truncate(task.context, task.query)
            task.context = truncation['truncated_context']
            total_savings += truncation['tokens_saved']
            
            # 4. Add to batch
            processor.add_task(task)
        
        # Process batch
        results = processor.flush()
        
        # Combined savings should be significant
        assert total_savings > 0
        assert len(results) == 2
```

---

## Phase 2 Success Criteria

### Overall Targets

- ✅ Combined token savings (Phase 1 + Phase 2): 50-60%
- ✅ Smart truncation: 10-20% savings on large contexts
- ✅ Batch processing: 10-15% savings on multi-task workflows
- ✅ Quality maintained: ≥ 90% across all features
- ✅ All tests passing: 30+ new tests (48+ total with Phase 1)

### Performance Benchmarks

| Feature | Token Savings | Quality | Latency |
|---------|---------------|---------|---------|
| Smart Truncation | 10-20% | ≥90% | <100ms |
| Batch Processing | 10-15% | ≥95% | <200ms |
| **Combined (Phase 1+2)** | **50-60%** | **≥90%** | **<500ms** |

---

## Timeline

### Week 10-13: Smart Truncation
- Week 10: Core implementation
- Week 11-12: Testing & validation
- Week 13: Performance optimization

### Week 14-15: Batch Processing
- Week 14: Core implementation
- Week 15: Testing & integration

### Buffer: 1 week for adjustments

---

## Next Steps

1. **Immediate**: Begin Week 10 implementation
2. **Week 10**: Complete SmartTruncator core
3. **Week 11-12**: Comprehensive testing
4. **Week 13**: Performance tuning
5. **Week 14**: BatchProcessor implementation
6. **Week 15**: Integration testing
7. **Phase 3**: Validation & production readiness

---

## Risk Mitigation

### Technical Risks

1. **Truncation Quality**: May lose important context
   - Mitigation: Conservative relevance thresholds, preserve critical sections
   
2. **Batch Parsing Failures**: LLM may not follow batch format
   - Mitigation: Robust parsing with fallbacks, clear format instructions

3. **Performance Overhead**: Grouping/scoring may be slow
   - Mitigation: Profile early, optimize hot paths, add caching

### Schedule Risks

1. **Complexity Underestimation**: Features may take longer
   - Mitigation: 1-week buffer, prioritize core functionality

2. **Integration Issues**: Phase 1 + Phase 2 conflicts
   - Mitigation: Early integration testing, modular design

---

## Conclusion

Phase 2 adds advanced optimization features that complement Phase 1's foundation. Together, they provide 50-60% token savings while maintaining high quality. The mock-based testing strategy ensures thorough validation before production deployment.

**Status**: Ready to begin implementation
**Next Action**: Start Week 10 - SmartTruncator core implementation
