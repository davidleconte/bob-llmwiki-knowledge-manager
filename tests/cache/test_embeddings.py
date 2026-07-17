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


class TestMiniLMBackend:
    """Verify that EmbeddingGenerator(backend='minilm') activates correctly
    via sentence-transformers when mlx-embeddings is not installed (ADR-017
    follow-up; P4 Sub-Task 2).
    """

    def test_minilm_st_fallback_activates(self, monkeypatch):
        """When mlx-embeddings is absent, sentence-transformers provides MiniLM."""
        import src.cache.embeddings as emb_mod

        # Reset cached resolution state so _try_load_minilm() re-runs.
        monkeypatch.setattr(emb_mod, "_minilm_available", None)
        monkeypatch.setattr(emb_mod, "_minilm_backend", "")
        monkeypatch.setattr(emb_mod, "_minilm_model", None)

        # Simulate mlx-embeddings being absent while keeping sentence-transformers.
        import builtins

        real_import = builtins.__import__

        def _block_mlx(name, *args, **kwargs):
            if name in ("mlx_embeddings", "mlx"):
                raise ImportError("mlx-embeddings not installed (simulated)")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _block_mlx)

        result = emb_mod._try_load_minilm()

        # sentence-transformers is installed in this environment → should succeed.
        assert result is True, "sentence-transformers fallback must activate"
        assert emb_mod._minilm_backend == "st"
        assert emb_mod._minilm_model is not None

    def test_minilm_st_vector_shape_and_norm(self, monkeypatch):
        """MiniLM via sentence-transformers produces 384-dim unit-norm vectors."""
        import src.cache.embeddings as emb_mod

        monkeypatch.setattr(emb_mod, "_minilm_available", None)
        monkeypatch.setattr(emb_mod, "_minilm_backend", "")
        monkeypatch.setattr(emb_mod, "_minilm_model", None)

        import builtins

        real_import = builtins.__import__

        def _block_mlx(name, *args, **kwargs):
            if name in ("mlx_embeddings", "mlx"):
                raise ImportError("mlx-embeddings not installed (simulated)")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _block_mlx)

        if not emb_mod._try_load_minilm():
            import pytest

            pytest.skip("sentence-transformers not installed")

        import numpy as np

        vec = emb_mod._embed_minilm("caching strategy for LLM token optimisation")
        assert vec.shape == (384,), f"Expected (384,), got {vec.shape}"
        norm = float(np.linalg.norm(vec))
        assert abs(norm - 1.0) < 1e-5, f"Vector not unit-norm: {norm}"

    def test_minilm_generator_backend_property(self, monkeypatch):
        """EmbeddingGenerator(backend='minilm') reports correct backend and dim.

        Calls _try_load_minilm() first so the model is already resident when the
        constructor runs — avoids re-downloading the model (which times out).
        """
        import src.cache.embeddings as emb_mod

        monkeypatch.setattr(emb_mod, "_minilm_available", None)
        monkeypatch.setattr(emb_mod, "_minilm_backend", "")
        monkeypatch.setattr(emb_mod, "_minilm_model", None)

        import builtins

        real_import = builtins.__import__

        def _block_mlx(name, *args, **kwargs):
            if name in ("mlx_embeddings", "mlx"):
                raise ImportError("mlx-embeddings not installed (simulated)")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _block_mlx)

        # Pre-load the model so the EmbeddingGenerator ctor finds it resident.
        loaded = emb_mod._try_load_minilm()
        if not loaded:
            import pytest

            pytest.skip("sentence-transformers not installed")

        gen = emb_mod.EmbeddingGenerator(backend="minilm")
        assert gen._backend == "minilm"
        assert gen.embedding_dim == 384
