"""Del-Academic Navigator Knowledge Base & Vector Store Package.

Provides modular tools for document ingestion, text cleaning,
word-aware chunking, dense embeddings, persistent ChromaDB indexing,
semantic retrieval, and relevance guardrails.
"""

from src.kb.chunker import DocumentChunk, WordAwareRecursiveChunker
from src.kb.cleaner import CleaningStats, TextCleaner
from src.kb.config import KBConfig, default_config
from src.kb.embedder import MockEmbedder, SentenceTransformerEmbedder
from src.kb.guardrails import GuardrailDecision, RelevanceGuardrail
from src.kb.loader import DocumentLoader, RawDocument
from src.kb.retriever import SearchResult, SemanticRetriever
from src.kb.vector_store import ChromaVectorStore

__all__ = [
    "KBConfig",
    "default_config",
    "RawDocument",
    "DocumentLoader",
    "CleaningStats",
    "TextCleaner",
    "DocumentChunk",
    "WordAwareRecursiveChunker",
    "SentenceTransformerEmbedder",
    "MockEmbedder",
    "ChromaVectorStore",
    "SearchResult",
    "SemanticRetriever",
    "GuardrailDecision",
    "RelevanceGuardrail",
]
