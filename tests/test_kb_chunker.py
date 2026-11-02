"""Unit tests for Word-Aware Recursive Chunker module (src/kb/chunker.py).

Tests word boundary integrity (never cuts words mid-word),
overlap consistency, metadata richness, hashing determinism,
parameter validation, and edge cases (empty text, short text, very long sentences).
"""

import hashlib
import pytest
from src.kb.chunker import DocumentChunk, WordAwareRecursiveChunker


def test_chunker_parameter_validation():
    with pytest.raises(ValueError, match="chunk_size_words must be > 0"):
        WordAwareRecursiveChunker(chunk_size_words=0)

    with pytest.raises(ValueError, match="chunk_overlap_words must be >= 0"):
        WordAwareRecursiveChunker(chunk_size_words=100, chunk_overlap_words=-5)

    with pytest.raises(ValueError, match="strictly less than chunk_size_words"):
        WordAwareRecursiveChunker(chunk_size_words=100, chunk_overlap_words=100)

    with pytest.raises(ValueError, match="strictly less than chunk_size_words"):
        WordAwareRecursiveChunker(chunk_size_words=100, chunk_overlap_words=120)


def test_chunker_empty_string():
    chunker = WordAwareRecursiveChunker(chunk_size_words=100, chunk_overlap_words=20)
    chunks = chunker.chunk_text("", doc_id="DOC-01")
    assert chunks == []

    chunks_ws = chunker.chunk_text("   \n\t  ", doc_id="DOC-01")
    assert chunks_ws == []


def test_chunker_short_text():
    chunker = WordAwareRecursiveChunker(chunk_size_words=100, chunk_overlap_words=20, min_chunk_words=10)
    text = "Institut Teknologi Del menyelenggarakan pendidikan tinggi berbasis asrama."
    chunks = chunker.chunk_text(text, doc_id="DOC-SHORT")
    assert len(chunks) == 1
    assert chunks[0].doc_id == "DOC-SHORT"
    assert chunks[0].chunk_index == 0
    assert chunks[0].total_chunks == 1
    assert chunks[0].word_count == len(text.split())
    assert chunks[0].text == text


def test_chunker_word_boundary_integrity():
    # Chunker must NEVER cut words in the middle (e.g., 'akademik' -> 'aka' + 'demik')
    chunker = WordAwareRecursiveChunker(chunk_size_words=20, chunk_overlap_words=5, min_chunk_words=5)
    sample_words = [
        "pertanggungjawaban", "ketidakhadiran", "pemberdayaan", "perkuliahan",
        "keberlanjutan", "laboratorium", "kemahasiswaan", "penjadwalan",
        "internasional", "kedisiplinan", "pelanggaran", "pengembangan",
        "pembimbingan", "kewirausahaan", "transformasi", "infrastruktur",
        "penyelenggaraan", "pengorganisasian", "rekomendasi", "pembelajaran",
        "komprehensif", "kolektivitas", "kesejahteraan", "kemasyarakatan"
    ]
    text = ". ".join([" ".join(sample_words[i:i+4]) for i in range(0, len(sample_words), 4)]) + "."
    chunks = chunker.chunk_text(text, doc_id="DOC-WORDS")

    assert len(chunks) > 1
    for chunk in chunks:
        chunk_words = chunk.text.replace(".", "").split()
        for w in chunk_words:
            assert w in sample_words, f"Word '{w}' appears corrupted or cut across word boundary!"


def test_chunker_overlap_consistency():
    chunker = WordAwareRecursiveChunker(chunk_size_words=30, chunk_overlap_words=10, min_chunk_words=5)
    # Generate 70 distinct numbered words
    words = [f"word_{i:03d}" for i in range(70)]
    text = " ".join(words) + "."
    chunks = chunker.chunk_text(text, doc_id="DOC-OVERLAP")

    assert len(chunks) >= 2
    for i in range(len(chunks) - 1):
        c1_words = chunks[i].text.replace(".", "").split()
        c2_words = chunks[i+1].text.replace(".", "").split()
        
        # Check overlap: trailing words of c1 must match leading words of c2
        overlap_slice = c1_words[-10:]
        assert c2_words[:10] == overlap_slice, f"Overlap mismatch between chunk {i} and {i+1}"


def test_chunker_very_long_sentence():
    # Test text containing a single run-on sentence with > 120 words without any period
    chunker = WordAwareRecursiveChunker(chunk_size_words=25, chunk_overlap_words=5, min_chunk_words=5)
    words = [f"token_{i}" for i in range(120)]
    long_sentence = " ".join(words)
    chunks = chunker.chunk_text(long_sentence, doc_id="DOC-LONG")

    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.word_count <= 25
        assert chunk.chunk_id.startswith("DOC-LONG#c")


def test_chunker_metadata_richness():
    chunker = WordAwareRecursiveChunker(chunk_size_words=40, chunk_overlap_words=10)
    text = "Kalimat pertama satu dua tiga. Kalimat kedua empat lima enam. Kalimat ketiga tujuh delapan sembilan."
    base_meta = {
        "title": "SOP Penjadwalan IT Del",
        "category": "SOP_AKADEMIK",
        "source_file": "data/corpus/sop_01.md",
        "organization": "Institut Teknologi Del"
    }
    chunks = chunker.chunk_text(text, doc_id="SOP-AKD-01", base_metadata=base_meta)

    assert len(chunks) == 1
    c = chunks[0]
    assert c.chunk_id == "SOP-AKD-01#c000"
    assert c.doc_id == "SOP-AKD-01"
    assert c.chunk_index == 0
    assert c.total_chunks == 1
    assert c.start_word == 0
    assert c.end_word == c.word_count
    assert c.content_hash == hashlib.sha256(c.text.encode("utf-8")).hexdigest()

    # Rich metadata verification
    meta = c.metadata
    assert meta["title"] == "SOP Penjadwalan IT Del"
    assert meta["category"] == "SOP_AKADEMIK"
    assert meta["source_file"] == "data/corpus/sop_01.md"
    assert meta["organization"] == "Institut Teknologi Del"
    assert "ingest_date" in meta
    assert meta["chunk_id"] == c.chunk_id
    assert meta["content_hash"] == c.content_hash
