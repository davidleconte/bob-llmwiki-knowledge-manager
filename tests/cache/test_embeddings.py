"""Tests for embedding generation determinism (C-5 regression).

Previously EmbeddingGenerator.generate() refit a TfidfVectorizer on the whole
accumulated corpus whenever it saw a new text -- a read-triggered refit. Because
TF-IDF dimensionality and idf weights are corpus-dependent, the embedding for a
FIXED text changed (shape and values) as the corpus grew, so:
  - a cached embedding silently drifted as new prompts were read/written, and
  - cosine similarity for a fixed pair was not stable across time / insertion
    order, breaking reproducibility (a Phase 4 integration prerequisite).

The fix makes the vectorizer stateless and fixed-dimension (HashingVectorizer),
so generate(text) is a pure transform: identical input -> identical output,
regardless of corpus history or instance.
"""

import numpy as np
import pytest

from src.cache.embeddings import EmbeddingGenerator


class TestEmbeddingDeterminism:
    def test_embedding_deterministic_across_corpus_growth(self):
        gen = EmbeddingGenerator()
        emb_first = gen.generate("what is python", use_cache=False)

        # Grow the corpus with unrelated texts, exactly what used to trigger a
        # refit that changed the dimensionality/values of earlier embeddings.
        for t in [
            "java is a great language",
            "rust guarantees memory safety",
            "go has a concurrency model",
            "javascript runs in browsers",
        ]:
            gen.generate(t, use_cache=False)

        emb_again = gen.generate("what is python", use_cache=False)

        assert emb_first.shape == emb_again.shape
        assert np.array_equal(emb_first, emb_again)

    def test_embedding_reproducible_across_instances(self):
        # Reproducibility: the same text embeds identically regardless of which
        # instance produced it or what corpus history that instance carries.
        g1 = EmbeddingGenerator()
        g2 = EmbeddingGenerator()

        # Give g1 a different corpus history than g2.
        g1.generate("seed one about databases")
        g1.generate("seed two about networking")

        a = g1.generate("a reproducible query", use_cache=False)
        b = g2.generate("a reproducible query", use_cache=False)

        assert a.shape == b.shape
        assert np.array_equal(a, b)

    def test_fixed_dimensionality(self):
        # Dimension is a constant (max_features), never a growing vocab size.
        gen = EmbeddingGenerator(max_features=512)
        emb = gen.generate("dimensionality should be fixed", use_cache=False)
        assert emb.shape == (512,)

    def test_identical_text_has_similarity_one(self):
        # The property SemanticCache relies on for exact-text hits.
        gen = EmbeddingGenerator()
        assert gen.similarity("cache me if you can", "cache me if you can") == pytest.approx(1.0)
