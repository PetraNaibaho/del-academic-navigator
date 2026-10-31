"""Semantic and Hybrid Retriever module for Del-Academic Navigator Knowledge Base."""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from src.kb.embedder import SentenceTransformerEmbedder
from src.kb.vector_store import ChromaVectorStore

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Structured search result ready for citation grounding in Agentic Copilot."""

    chunk_id: str
    doc_id: str
    title: str
    category: str
    chunk_index: int
    text: str
    score: float  # Cosine similarity [0.0, 1.0]
    distance: float  # Cosine distance
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_citation_dict(self) -> Dict[str, Any]:
        """Format chunk into citation payload for UI/Agent grounding."""
        return {
            "source": self.title,
            "doc_id": self.doc_id,
            "chunk_index": self.chunk_index,
            "confidence": round(self.score, 4),
            "snippet": self.text[:200] + ("..." if len(self.text) > 200 else ""),
            "metadata": self.metadata,
        }


class SemanticRetriever:
    """High-level semantic and hybrid retriever supporting vector search, metadata filtering, and BM25 RRF."""

    def __init__(
        self,
        vector_store: ChromaVectorStore,
        embedder: Any,
    ):
        self.vector_store = vector_store
        self.embedder = embedder

    @staticmethod
    def distance_to_similarity(distance: float) -> float:
        """Convert ChromaDB cosine distance to Cosine Similarity score.

        In ChromaDB with HNSW cosine metric:
            distance = 1.0 - cos_similarity
        Therefore:
            cos_similarity = 1.0 - distance
        Clamped to [0.0, 1.0].
        """
        similarity = 1.0 - distance
        return max(0.0, min(1.0, float(similarity)))

    def search(
        self,
        query: str,
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Perform dense vector semantic retrieval on query string."""
        if not query.strip() or self.vector_store.count() == 0:
            return []

        # 1. Encode query
        query_embedding = self.embedder.encode_query(query)

        # 2. Query vector store
        raw_results = self.vector_store.query_similarity(
            query_embedding=query_embedding,
            top_k=top_k,
            where_filter=where_filter,
        )

        ids = raw_results.get("ids", [[]])[0]
        distances = raw_results.get("distances", [[]])[0]
        documents = raw_results.get("documents", [[]])[0]
        metadatas = raw_results.get("metadatas", [[]])[0]

        search_results: List[SearchResult] = []
        for i in range(len(ids)):
            dist = float(distances[i]) if distances else 0.0
            sim_score = self.distance_to_similarity(dist)
            meta = metadatas[i] if metadatas and i < len(metadatas) else {}
            doc_text = documents[i] if documents and i < len(documents) else ""

            result = SearchResult(
                chunk_id=ids[i],
                doc_id=str(meta.get("doc_id", "UNKNOWN")),
                title=str(meta.get("title", "Untitled Document")),
                category=str(meta.get("category", "GENERAL")),
                chunk_index=int(meta.get("chunk_index", 0)),
                text=doc_text,
                score=sim_score,
                distance=dist,
                metadata=meta,
            )
            search_results.append(result)

        # Sort descending by score
        search_results.sort(key=lambda x: x.score, reverse=True)
        return search_results

    def hybrid_search(
        self,
        query: str,
        all_chunks: List[Any],
        top_k: int = 5,
        rrf_k: int = 60,
    ) -> List[SearchResult]:
        """Perform Hybrid Search combining Dense Semantic Search and Lexical BM25/keyword matching using RRF.

        Reciprocal Rank Fusion (RRF):
            Score(d) = 1 / (k + rank_semantic(d)) + 1 / (k + rank_lexical(d))
        """
        # 1. Dense Semantic Ranking
        dense_results = self.search(query, top_k=min(20, self.vector_store.count()))
        dense_ranks = {res.chunk_id: rank + 1 for rank, res in enumerate(dense_results)}

        # 2. Lexical / Keyword Token Matching Ranking
        query_tokens = set(query.lower().split())
        lexical_scores = []
        for chunk in all_chunks:
            chunk_tokens = chunk.text.lower().split()
            overlap = sum(1 for t in chunk_tokens if t in query_tokens)
            score = overlap / (len(chunk_tokens) + 1e-5)
            lexical_scores.append((chunk.chunk_id, score, chunk))

        lexical_scores.sort(key=lambda x: x[1], reverse=True)
        lexical_ranks = {item[0]: rank + 1 for rank, item in enumerate(lexical_scores[:20])}

        # 3. Compute RRF Scores
        all_candidate_ids = set(dense_ranks.keys()).union(set(lexical_ranks.keys()))
        chunk_map = {c.chunk_id: c for c in all_chunks}
        dense_res_map = {res.chunk_id: res for res in dense_results}

        fused_scores = []
        for cid in all_candidate_ids:
            dense_rank = dense_ranks.get(cid, 1000)
            lex_rank = lexical_ranks.get(cid, 1000)
            rrf_score = (1.0 / (rrf_k + dense_rank)) + (1.0 / (rrf_k + lex_rank))
            
            if cid in dense_res_map:
                res = dense_res_map[cid]
            else:
                chunk = chunk_map[cid]
                res = SearchResult(
                    chunk_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    title=str(chunk.metadata.get("title", "")),
                    category=str(chunk.metadata.get("category", "")),
                    chunk_index=chunk.chunk_index,
                    text=chunk.text,
                    score=0.0,
                    distance=1.0,
                    metadata=chunk.metadata,
                )
            fused_scores.append((rrf_score, res))

        fused_scores.sort(key=lambda x: x[0], reverse=True)
        top_results = [item[1] for item in fused_scores[:top_k]]
        return top_results
