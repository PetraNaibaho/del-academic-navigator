"""Unit tests for Semantic and Hybrid Retriever module (src/kb/retriever.py).

Tests score sorting order (descending), distance to similarity conversion,
metadata filtering (Chroma where clause), citation dictionary generation,
and hybrid search RRF integration.
Uses MockEmbedder for fast, deterministic unit test execution.
"""

from pathlib import Path
import pytest
from src.kb.chunker import DocumentChunk
from src.kb.embedder import MockEmbedder
from src.kb.retriever import SearchResult, SemanticRetriever
from src.kb.vector_store import ChromaVectorStore


@pytest.fixture
def mock_embedder() -> MockEmbedder:
    return MockEmbedder(dimension=384)


@pytest.fixture
def test_chunks() -> list[DocumentChunk]:
    return [
        DocumentChunk(
            chunk_id="SOP-AKD-01#c000",
            doc_id="SOP-AKD-01",
            text="Dosen wajib mengajukan kuliah pengganti paling lambat H-2.",
            chunk_index=0,
            total_chunks=2,
            start_word=0,
            end_word=8,
            word_count=8,
            content_hash="h1",
            metadata={"doc_id": "SOP-AKD-01", "category": "SOP_AKADEMIK", "title": "SOP Penjadwalan"},
        ),
        DocumentChunk(
            chunk_id="SOP-AKD-01#c001",
            doc_id="SOP-AKD-01",
            text="Kelas rombongan lebih dari 40 mahasiswa wajib di ruangan GD721 atau GD722.",
            chunk_index=1,
            total_chunks=2,
            start_word=9,
            end_word=19,
            word_count=11,
            content_hash="h2",
            metadata={"doc_id": "SOP-AKD-01", "category": "SOP_AKADEMIK", "title": "SOP Penjadwalan"},
        ),
        DocumentChunk(
            chunk_id="SOP-KMS-01#c000",
            doc_id="SOP-KMS-01",
            text="Waktu belajar mandiri wajib asrama compulsory study time dimulai pukul 19:30 hingga 22:00.",
            chunk_index=0,
            total_chunks=1,
            start_word=0,
            end_word=12,
            word_count=12,
            content_hash="h3",
            metadata={"doc_id": "SOP-KMS-01", "category": "SOP_KEMAHASISWAAN", "title": "SOP Asrama"},
        ),
    ]


@pytest.fixture
def populated_retriever(
    tmp_path: Path,
    mock_embedder: MockEmbedder,
    test_chunks: list[DocumentChunk],
) -> SemanticRetriever:
    store = ChromaVectorStore(persist_dir=tmp_path / "retriever_test", collection_name="col_retriever")
    store.index_chunks(test_chunks, mock_embedder)
    return SemanticRetriever(vector_store=store, embedder=mock_embedder)


def test_distance_to_similarity_conversion():
    # In ChromaDB cosine space: distance = 1 - cos_sim, so cos_sim = 1 - distance
    assert SemanticRetriever.distance_to_similarity(0.0) == 1.0
    assert pytest.approx(SemanticRetriever.distance_to_similarity(0.25), 1e-4) == 0.75
    assert SemanticRetriever.distance_to_similarity(1.0) == 0.0
    # Clamping tests
    assert SemanticRetriever.distance_to_similarity(1.5) == 0.0
    assert SemanticRetriever.distance_to_similarity(-0.2) == 1.0


def test_retriever_search_sorting_order(populated_retriever: SemanticRetriever):
    results = populated_retriever.search("kuliah pengganti", top_k=3)
    assert len(results) == 3
    # Results must be sorted in descending order of similarity score
    for i in range(len(results) - 1):
        assert results[i].score >= results[i + 1].score
        assert isinstance(results[i], SearchResult)


def test_retriever_metadata_filtering(populated_retriever: SemanticRetriever):
    # Search specifically filtered by category SOP_KEMAHASISWAAN
    results = populated_retriever.search(
        "kuliah mahasiswa asrama",
        top_k=5,
        where_filter={"category": "SOP_KEMAHASISWAAN"},
    )
    assert len(results) == 1
    assert results[0].doc_id == "SOP-KMS-01"
    assert results[0].category == "SOP_KEMAHASISWAAN"

    # Search filtered by doc_id
    results_akd = populated_retriever.search(
        "asrama",
        top_k=5,
        where_filter={"doc_id": "SOP-AKD-01"},
    )
    assert len(results_akd) == 2
    for r in results_akd:
        assert r.doc_id == "SOP-AKD-01"


def test_retriever_empty_query(populated_retriever: SemanticRetriever):
    assert populated_retriever.search("") == []
    assert populated_retriever.search("   ") == []


def test_search_result_citation_dict():
    res = SearchResult(
        chunk_id="SOP-AKD-01#c000",
        doc_id="SOP-AKD-01",
        title="SOP Penjadwalan Kuliah Pengganti",
        category="SOP_AKADEMIK",
        chunk_index=0,
        text="Teks isi ketentuan perkuliahan pengganti kampus Del.",
        score=0.8842,
        distance=0.1158,
        metadata={"unit": "BAAK"},
    )
    citation = res.to_citation_dict()
    assert citation["source"] == "SOP Penjadwalan Kuliah Pengganti"
    assert citation["doc_id"] == "SOP-AKD-01"
    assert citation["chunk_index"] == 0
    assert citation["confidence"] == 0.8842
    assert "Teks isi ketentuan" in citation["snippet"]
    assert citation["metadata"] == {"unit": "BAAK"}


def test_retriever_hybrid_search(
    populated_retriever: SemanticRetriever,
    test_chunks: list[DocumentChunk],
):
    # Query with exact keyword overlap for 'asrama'
    results = populated_retriever.hybrid_search(
        query="aturan asrama compulsory study time",
        all_chunks=test_chunks,
        top_k=2,
    )
    assert len(results) == 2
    # The chunk containing 'compulsory study time asrama' should be ranked top
    assert results[0].doc_id == "SOP-KMS-01"
