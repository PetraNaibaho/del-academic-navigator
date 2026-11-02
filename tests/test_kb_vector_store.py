"""Unit tests for ChromaDB persistent vector store module (src/kb/vector_store.py).

Tests persistent storage creation, cosine distance space configuration,
idempotent indexing, persistence across client restarts, and collection resets.
Uses MockEmbedder for fast, deterministic unit test execution.
"""

from pathlib import Path
import pytest
from src.kb.chunker import DocumentChunk
from src.kb.embedder import MockEmbedder
from src.kb.vector_store import ChromaVectorStore


@pytest.fixture
def mock_embedder() -> MockEmbedder:
    return MockEmbedder(dimension=384)


@pytest.fixture
def sample_chunks() -> list[DocumentChunk]:
    return [
        DocumentChunk(
            chunk_id="DOC-01#c000",
            doc_id="DOC-01",
            text="Pengajuan kuliah pengganti wajib H-2.",
            chunk_index=0,
            total_chunks=2,
            start_word=0,
            end_word=5,
            word_count=5,
            content_hash="hash01",
            metadata={"doc_id": "DOC-01", "category": "SOP_AKADEMIK", "title": "SOP 01"},
        ),
        DocumentChunk(
            chunk_id="DOC-01#c001",
            doc_id="DOC-01",
            text="Kelas rombel di atas 40 mahasiswa wajib di GD721.",
            chunk_index=1,
            total_chunks=2,
            start_word=6,
            end_word=14,
            word_count=9,
            content_hash="hash02",
            metadata={"doc_id": "DOC-01", "category": "SOP_AKADEMIK", "title": "SOP 01"},
        ),
        DocumentChunk(
            chunk_id="DOC-02#c000",
            doc_id="DOC-02",
            text="Kuota bimbingan akademik dosen PA maksimal 5 mahasiswa.",
            chunk_index=0,
            total_chunks=1,
            start_word=0,
            end_word=8,
            word_count=8,
            content_hash="hash03",
            metadata={"doc_id": "DOC-02", "category": "SOP_KEMAHASISWAAN", "title": "SOP 02"},
        ),
    ]


def test_vector_store_initialization(tmp_path: Path):
    store = ChromaVectorStore(persist_dir=tmp_path / "chroma_test", collection_name="test_col")
    assert store.count() == 0
    assert store.collection.metadata.get("hnsw:space") == "cosine"


def test_vector_store_idempotent_indexing(
    tmp_path: Path,
    mock_embedder: MockEmbedder,
    sample_chunks: list[DocumentChunk],
):
    store = ChromaVectorStore(persist_dir=tmp_path / "chroma_test", collection_name="test_col")

    # Initial indexing of 3 chunks
    indexed_first = store.index_chunks(sample_chunks, mock_embedder, skip_existing=True)
    assert indexed_first == 3
    assert store.count() == 3

    # Second indexing of same chunks with skip_existing=True should skip all 3
    indexed_second = store.index_chunks(sample_chunks, mock_embedder, skip_existing=True)
    assert indexed_second == 0
    assert store.count() == 3

    # Indexing empty chunks
    assert store.index_chunks([], mock_embedder) == 0


def test_vector_store_persistence_across_reconnect(
    tmp_path: Path,
    mock_embedder: MockEmbedder,
    sample_chunks: list[DocumentChunk],
):
    persist_dir = tmp_path / "chroma_persistence"

    # Step 1: Open store, index chunks, then close/del reference
    store1 = ChromaVectorStore(persist_dir=persist_dir, collection_name="persistent_col")
    store1.index_chunks(sample_chunks, mock_embedder)
    assert store1.count() == 3
    del store1

    # Step 2: Reopen a new ChromaVectorStore on the exact same directory
    store2 = ChromaVectorStore(persist_dir=persist_dir, collection_name="persistent_col")
    assert store2.count() == 3

    # Verify existing document texts and metadatas remain intact
    res = store2.collection.get(ids=["DOC-01#c000"])
    assert len(res["ids"]) == 1
    assert res["documents"][0] == "Pengajuan kuliah pengganti wajib H-2."
    assert res["metadatas"][0]["category"] == "SOP_AKADEMIK"


def test_vector_store_reset_collection(
    tmp_path: Path,
    mock_embedder: MockEmbedder,
    sample_chunks: list[DocumentChunk],
):
    store = ChromaVectorStore(persist_dir=tmp_path / "chroma_reset", collection_name="reset_col")
    store.index_chunks(sample_chunks, mock_embedder)
    assert store.count() == 3

    store.reset_collection()
    assert store.count() == 0
    assert store.collection.metadata.get("hnsw:space") == "cosine"
