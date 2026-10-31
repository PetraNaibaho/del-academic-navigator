"""Embedding extraction module wrapping Sentence-Transformers with prefix and batching support."""

import logging
import os
from typing import List, Optional, Union

import numpy as np

# Prevent huggingface_hub from attempting online requests when running in sandboxed environment
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

logger = logging.getLogger(__name__)


class SentenceTransformerEmbedder:
    """Enterprise embedding generator using Sentence-Transformers models.

    Handles model caching, batch encoding, L2 normalization,
    and automatic query/passage prefixing (e.g., for E5 models).
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        device: Optional[str] = None,
        batch_size: int = 32,
        normalize_embeddings: bool = True,
    ):
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self.normalize_embeddings = normalize_embeddings
        self._is_e5 = "e5" in model_name.lower()

        logger.info("Initializing SentenceTransformer with model: %s (device=%s)", self.model_name, self.device)
        from sentence_transformers import SentenceTransformer
        try:
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device,
                model_kwargs={"local_files_only": True},
            )
        except Exception:
            # Fallback if local_files_only kwargs isn't supported by specific wrapper
            self.model = SentenceTransformer(self.model_name, device=self.device)

        self._dimension = self.model.get_sentence_embedding_dimension()
        logger.info("Model loaded successfully. Embedding dimension: %d", self._dimension)

    @property
    def dimension(self) -> int:
        """Return embedding vector dimension."""
        return self._dimension

    def _prepare_text(self, text: str, is_query: bool = False) -> str:
        """Apply model-specific prefixing (e.g., 'query: ' or 'passage: ' for E5 models)."""
        clean_text = text.strip()
        if self._is_e5:
            prefix = "query: " if is_query else "passage: "
            if not clean_text.startswith(prefix):
                return f"{prefix}{clean_text}"
        return clean_text

    def encode_documents(self, documents: List[str], show_progress_bar: bool = False) -> List[List[float]]:
        """Encode a list of document chunk texts into dense vectors."""
        if not documents:
            return []

        prefixed_docs = [self._prepare_text(doc, is_query=False) for doc in documents]
        embeddings = self.model.encode(
            prefixed_docs,
            batch_size=self.batch_size,
            show_progress_bar=show_progress_bar,
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True,
        )
        return embeddings.tolist()

    def encode_query(self, query: str) -> List[float]:
        """Encode a single query string into a dense vector."""
        prefixed_query = self._prepare_text(query, is_query=True)
        embedding = self.model.encode(
            prefixed_query,
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True,
        )
        return embedding.tolist()


class MockEmbedder:
    """Fast deterministic mock embedder for rapid unit tests without GPU/weights overhead."""

    def __init__(self, dimension: int = 384, model_name: str = "mock-embedder"):
        self.model_name = model_name
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def _hash_to_vector(self, text: str) -> List[float]:
        import hashlib
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # Seed pseudo-random generator with text hash
        seed = int.from_bytes(h[:4], "little")
        rng = np.random.RandomState(seed)
        vec = rng.randn(self._dimension)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def encode_documents(self, documents: List[str], show_progress_bar: bool = False) -> List[List[float]]:
        return [self._hash_to_vector(d) for d in documents]

    def encode_query(self, query: str) -> List[float]:
        return self._hash_to_vector(query)
