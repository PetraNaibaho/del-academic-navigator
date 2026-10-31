"""Central configuration module for Del-Academic Navigator Knowledge Base & Vector Store.

Follows enterprise clean code standards, Pydantic/dataclass patterns,
and ensures centralized configuration without hardcoded paths.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class KBConfig:
    """Configuration container for Knowledge Base ingestion, embedding, and vector store."""

    # Base Paths
    PROJECT_ROOT: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    DATA_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data")
    CORPUS_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data" / "corpus")
    PROCESSED_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data" / "processed")
    CHROMA_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data" / "chroma_db")
    REPORTS_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "reports")
    FIGURES_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "reports" / "figures")

    MANIFEST_JSON: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data" / "corpus_manifest.json")
    MANIFEST_CSV: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data" / "corpus_manifest.csv")
    BENCHMARK_QUERIES_JSON: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data" / "benchmark_queries.json")

    # ChromaDB Settings
    COLLECTION_NAME: str = "itdel_academic_corpus"
    DISTANCE_METRIC: str = "cosine"  # HNSW space in ChromaDB: cosine
    
    # Embedding Models
    DEFAULT_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    CANDIDATE_MODELS: Dict[str, str] = field(default_factory=lambda: {
        "primary": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "e5": "intfloat/multilingual-e5-small",
        "english_baseline": "sentence-transformers/all-MiniLM-L6-v2"
    })
    
    # Model token limits
    MODEL_TOKEN_LIMIT: int = 128  # MiniLM max input tokens
    BATCH_SIZE: int = 32

    # Chunking Parameters (Word-aware recursive strategy)
    DEFAULT_CHUNK_SIZE_WORDS: int = 150  # Optimal empirically validated
    DEFAULT_CHUNK_OVERLAP_WORDS: int = 30  # 20% overlap
    MIN_CHUNK_SIZE_WORDS: int = 20

    # Guardrails & Relevance Threshold
    # Empirically calibrated threshold on cosine similarity (1 - distance)
    # Calibrated from empirical sweep: In-Domain min=0.463, Out-of-Domain max=0.385
    RELEVANCE_THRESHOLD: float = 0.44
    
    # Available domain topics for polite fallback suggestion
    AVAILABLE_TOPICS: List[str] = field(default_factory=lambda: [
        "SOP Penjadwalan Kuliah Pengganti (Make-up Class & Ruang GD721/GD722)",
        "SOP Bimbingan Akademik Dosen Pembimbing Akademik (Dosen PA)",
        "SOP Peminjaman & Tata Tertib Laboratorium Komputer & AI (GD911)",
        "SOP Tata Tertib, Jam Belajar (Study Time), dan Jam Malam Asrama",
        "SOP Pengajuan Cuti Akademik dan Pengunduran Diri",
        "SOP Evaluasi Keberlanjutan Studi (Tahap I, Tahap II) dan Drop Out",
        "SOP Tugas Akhir, Seminar Proposal, dan Sidang Meja Hijau FITE",
        "SOP Beasiswa Prestasi dan Bantuan Finansial Mahasiswa",
        "SOP Penggunaan Internet, Akun SSO Del, dan Kebijakan Keamanan Siber",
        "SOP Layanan Sirkulasi Buku dan Repositori Digital Perpustakaan",
        "SOP Klinik Kesehatan Kampus dan Surat Dispensasi Sakit",
        "SOP Beban Kerja Dosen (BKD) dan Etika Pengajaran",
        "Pedoman Sanksi Disiplin Akademik dan Pencegahan Plagiarisme",
        "Pedoman Sistem Penilaian, Skala Huruf Mutu, dan Ujian Remedial",
        "Panduan Izin Bermalam (IB) dan Pesiar Akhir Pekan Mahasiswa"
    ])

    RANDOM_SEED: int = 42


# Default shared instance
default_config = KBConfig()
