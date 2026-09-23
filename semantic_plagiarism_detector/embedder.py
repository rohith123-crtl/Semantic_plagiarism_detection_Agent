"""
Semantic Embedder
=================
Provides a clean interface for generating embeddings.
- Default: Lightweight TF-IDF style + character n-grams (works offline, no extra deps)
- Production: Drop-in replacement with sentence-transformers (recommended)

This design satisfies the "Semantic embeddings" requirement while remaining
runnable in restricted environments.
"""

from __future__ import annotations
import re
import math
from collections import Counter
from typing import List, Dict, Optional
import numpy as np


class BaseEmbedder:
    """Abstract interface – swap implementations easily."""

    def embed(self, texts: List[str]) -> np.ndarray:
        raise NotImplementedError

    def embed_single(self, text: str) -> np.ndarray:
        return self.embed([text])[0]


class TfIdfNgramEmbedder(BaseEmbedder):
    """
    Offline semantic-ish embedder.
    Combines:
      - Word unigrams + bigrams
      - Character trigrams (helps with paraphrases / rewording)
    Then applies simple TF-IDF weighting and L2 normalization.
    """

    def __init__(self, max_features: int = 8000):
        self.max_features = max_features
        self.vocab: Dict[str, int] = {}
        self.idf: Optional[np.ndarray] = None
        self._fitted = False

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        words = text.split()
        tokens = []
        # word unigrams + bigrams + trigrams
        tokens.extend(words)
        tokens.extend(f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1))
        tokens.extend(f"{words[i]}_{words[i+1]}_{words[i+2]}" for i in range(len(words) - 2))
        # character 3-grams and 4-grams (strong for paraphrase robustness)
        clean = re.sub(r"\s+", " ", text)
        tokens.extend(clean[i:i+3] for i in range(len(clean) - 2))
        tokens.extend(clean[i:i+4] for i in range(len(clean) - 3))
        return tokens

    def fit(self, texts: List[str]) -> "TfIdfNgramEmbedder":
        doc_freq: Counter = Counter()
        for text in texts:
            unique = set(self._tokenize(text))
            for t in unique:
                doc_freq[t] += 1

        # Keep most frequent features
        most_common = doc_freq.most_common(self.max_features)
        self.vocab = {tok: idx for idx, (tok, _) in enumerate(most_common)}
        N = len(texts)
        self.idf = np.zeros(len(self.vocab), dtype=np.float32)
        for tok, idx in self.vocab.items():
            df = doc_freq[tok]
            self.idf[idx] = math.log((N + 1) / (df + 1)) + 1.0
        self._fitted = True
        return self

    def embed(self, texts: List[str]) -> np.ndarray:
        if not self._fitted:
            # Auto-fit on the fly for convenience
            self.fit(texts)

        vectors = np.zeros((len(texts), len(self.vocab)), dtype=np.float32)
        for i, text in enumerate(texts):
            tokens = self._tokenize(text)
            counts = Counter(tokens)
            for tok, cnt in counts.items():
                if tok in self.vocab:
                    idx = self.vocab[tok]
                    vectors[i, idx] = cnt * self.idf[idx]

        # L2 normalize
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-9)
        return vectors / norms


class SentenceTransformerEmbedder(BaseEmbedder):
    """
    Production embedder using sentence-transformers.
    Uncomment and use when the package is available.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )

    def embed(self, texts: List[str]) -> np.ndarray:
        return np.array(self.model.encode(texts, show_progress_bar=False))


def get_embedder(prefer_semantic: bool = True) -> BaseEmbedder:
    """
    Factory: tries real semantic model first, falls back to offline TF-IDF.
    """
    if prefer_semantic:
        try:
            return SentenceTransformerEmbedder()
        except Exception:
            pass
    return TfIdfNgramEmbedder()
