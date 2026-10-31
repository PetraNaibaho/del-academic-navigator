"""ChromaDB persistent vector store manager with cosine metric and idempotent indexing."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import chromadb
from chromadb.config import Settings

from src.kb.chunker import DocumentChunk
from src.kb.embedder import SentenceTransformerEmbedder

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """Persistent vector store implementation backed by ChromaDB with cosine metric."""

    def __init__(
        self,
        persist_dir: Union[str, Path],
        collection_name: str = "itdel_academic_corpus",
    ):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name

        logger.info(
            "Initializing ChromaDB PersistentClient at: %s (Collection: %s)",
            self.persist_dir,
            self.collection_name,
        )
        
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir.resolve()),
            settings=Settings(anonymized_telemetry=False, is_persistent=True),
        )

        # Get or create collection configured with cosine distance
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "Collection '%s' ready. Current document count: %d",
            self.collection_name,
            self.collection.count(),
        )

    def count(self) -> int:
        """Return the number of vectors stored in the collection."""
        return self.collection.count()

    def reset_collection(self) -> None:
        """Delete all vectors in the collection and recreate fresh."""
        logger.warning("Resetting collection '%s'...", self.collection_name)
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Collection '%s' reset successfully.", self.collection_name)

    def index_chunks(
        self,
        chunks: List[DocumentChunk],
        embedder: Any,
        batch_size: int = 32,
        skip_existing: bool = True,
    ) -> int:
        """Idempotently index document chunks into ChromaDB in batches."""
        if not chunks:
            return 0

        # Check existing IDs if skip_existing is enabled
        existing_ids = set()
        if skip_existing and self.count() > 0:
            existing_records = self.collection.get(include=["metadatas"])
            if existing_records and "ids" in existing_records:
                existing_ids = set(existing_records["ids"])

        new_chunks = [c for c in chunks if c.chunk_id not in existing_ids]
        if not new_chunks:
            logger.info("All %d chunks already indexed. Skipping.", len(chunks))
            return 0

        logger.info(
            "Indexing %d new chunks into ChromaDB (out of %d total)...",
            len(new_chunks),
            len(chunks),
        )

        total_indexed = 0
        for i in range(0, len(new_chunks), batch_size):
            batch = new_chunks[i : i + batch_size]
            batch_texts = [c.text for c in batch]
            batch_ids = [c.chunk_id for c in batch]

            # Generate dense embeddings
            batch_embeddings = embedder.encode_documents(batch_texts)

            # Sanitize metadata for ChromaDB (must be str, int, float, bool)
            batch_metadatas: List[Dict[str, Any]] = []
            for c in batch:
                meta = {}
                for k, v in c.metadata.items():
                    if isinstance(v, (str, int, float, bool)):
                        meta[k] = v
                    else:
                        meta[k] = str(v)
                batch_metadatas.append(meta)

            # Idempotent upsert
            self.collection.upsert(
                ids=batch_ids,
                embeddings=batch_embeddings,
                documents=batch_texts,
                metadatas=batch_metadatas,
            )
            total_indexed += len(batch)
            logger.debug("Indexed batch %d-%d (%d chunks)", i, i + len(batch), total_indexed)

        logger.info("Successfully indexed %d chunks into '%s'. Total count: %d", total_indexed, self.collection_name, self.count())
        return total_indexed

    def query_similarity(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Perform semantic similarity search on the cosine collection."""
        if self.count() == 0:
            return {"ids": [[]], "distances": [[]], "documents": [[]], "metadatas": [[]]}

        kwargs: Dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, self.count()),
            "include": ["documents", "metadatas", "distances"],
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = self.collection.query(**kwargs)
        return results
