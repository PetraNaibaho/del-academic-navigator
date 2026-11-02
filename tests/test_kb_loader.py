"""Unit tests for Document Loader module (src/kb/loader.py).

Tests file format support (.txt, .md, .pdf), manifest metadata enrichment,
directory loading, and robust error handling (missing files, unsupported extensions).
"""

from pathlib import Path
import pytest
from src.kb.config import default_config
from src.kb.loader import DocumentLoader, RawDocument


@pytest.fixture
def loader() -> DocumentLoader:
    return DocumentLoader(
        corpus_dir=default_config.CORPUS_DIR,
        manifest_path=default_config.MANIFEST_JSON,
    )


def test_loader_manifest_loaded(loader: DocumentLoader):
    assert len(loader._manifest_cache) > 0
    assert "SOP-AKD-01" in loader._manifest_cache


def test_loader_load_markdown_document(loader: DocumentLoader):
    md_file = default_config.CORPUS_DIR / "SOP-AKD-01_Penjadwalan_Kuliah_Pengganti.md"
    assert md_file.exists()

    doc = loader.load_document(md_file)
    assert isinstance(doc, RawDocument)
    assert doc.doc_id == "SOP-AKD-01"
    assert doc.format == "md"
    assert doc.category == "SOP_AKADEMIK"
    assert "Make-Up Class" in doc.title
    assert doc.char_count > 100
    assert doc.word_count > 20
    assert "UU PDP No. 27/2022" in doc.metadata.get("compliance", "")


def test_loader_load_text_document(loader: DocumentLoader):
    txt_file = default_config.CORPUS_DIR / "SOP-SDM-01_Beban_Kinerja_Dosen_dan_Kode_Etik_Pengajaran.txt"
    assert txt_file.exists()

    doc = loader.load_document(txt_file)
    assert isinstance(doc, RawDocument)
    assert doc.doc_id == "SOP-SDM-01"
    assert doc.format == "txt"
    assert doc.category == "SOP_SDM"
    assert doc.word_count > 20


def test_loader_load_pdf_document(loader: DocumentLoader):
    pdf_file = default_config.CORPUS_DIR / "REG-AKD-01_Pedoman_Pelanggaran_Akademik_dan_Sanksi_Disiplin.pdf"
    assert pdf_file.exists()

    doc = loader.load_document(pdf_file)
    assert isinstance(doc, RawDocument)
    assert doc.doc_id == "REG-AKD-01"
    assert doc.format == "pdf"
    assert doc.category == "REGULASI"
    assert "PELANGGARAN AKADEMIK" in doc.raw_text.upper()


def test_loader_load_directory(loader: DocumentLoader):
    docs = loader.load_directory()
    assert len(docs) >= 10
    doc_ids = {d.doc_id for d in docs}
    assert "SOP-AKD-01" in doc_ids
    assert "REG-AKD-01" in doc_ids
    assert "PANDUAN-KMS-01" in doc_ids


def test_loader_file_not_found(loader: DocumentLoader):
    with pytest.raises(FileNotFoundError):
        loader.load_document(Path("data/corpus/non_existent_document.md"))


def test_loader_unsupported_format(tmp_path: Path):
    invalid_file = tmp_path / "test.docx"
    invalid_file.write_text("sample content")

    loader = DocumentLoader()
    with pytest.raises(ValueError, match="Unsupported document format"):
        loader.load_document(invalid_file)
