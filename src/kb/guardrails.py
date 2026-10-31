"""Relevance Threshold Guardrail module for Out-of-Domain protection and hallucination mitigation."""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from src.kb.config import default_config
from src.kb.retriever import SearchResult, SemanticRetriever

logger = logging.getLogger(__name__)


@dataclass
class GuardrailDecision:
    """Represents the guardrail verdict for an incoming user query."""

    is_accepted: bool
    query: str
    top_score: float
    threshold: float
    results: List[SearchResult] = field(default_factory=list)
    rejection_message: Optional[str] = None
    suggested_topics: List[str] = field(default_factory=list)


class RelevanceGuardrail:
    """Guards the RAG pipeline by filtering out-of-domain queries using calibrated cosine similarity thresholds."""

    DEFAULT_REJECTION_MESSAGE = (
        "Maaf, pertanyaan Anda berada di luar cakupan basis pengetahuan dokumen internal "
        "Institut Teknologi Del (Del-Academic Navigator). Sistem kami difokuskan untuk menjawab "
        "regulasi akademik, SOP perkuliahan, kehidupan asrama MarTuhan Marroha Marbisuk, dan fasilitas kampus IT Del."
    )

    def __init__(
        self,
        retriever: SemanticRetriever,
        threshold: float = default_config.RELEVANCE_THRESHOLD,
        suggested_topics: Optional[List[str]] = None,
    ):
        self.retriever = retriever
        self.threshold = threshold
        self.suggested_topics = suggested_topics or [
            "SOP Penjadwalan Perkuliahan Pengganti (Make-Up Class)",
            "SOP Bimbingan Akademik Dosen Pembimbing Akademik (Dosen PA)",
            "SOP Peminjaman Laboratorium Komputer dan AI (GD911)",
            "Tata Tertib Asrama, Jam Belajar (Study Time), dan Jam Malam",
            "Prosedur Pengajuan Cuti Akademik dan Pengunduran Diri",
            "Evaluasi Keberlanjutan Studi (Tahap I, Tahap II) dan Drop Out",
            "Pedoman Pelaksanaan Tugas Akhir dan Sidang Meja Hijau FITE",
            "Pengajuan Beasiswa Prestasi dan Bantuan Finansial",
            "Kebijakan Penggunaan Jaringan Internet dan Akun SSO Del",
            "Layanan Sirkulasi Buku dan Akses Repositori Perpustakaan",
            "Pelayanan Kesehatan Klinik Kampus dan Surat Dispensasi Sakit",
            "SOP Standar Beban Kerja Dosen (BKD) dan Etika Pengajaran",
            "Pedoman Disiplin Akademik dan Sanksi Kecurangan",
            "Sistem Penilaian, Skala Huruf Mutu, dan Ujian Remedial",
            "Panduan Izin Bermalam (IB) dan Pesiar Akhir Pekan",
        ]

    def verify_query(
        self,
        query: str,
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> GuardrailDecision:
        """Evaluate query relevance against knowledge base.

        If top-1 cosine similarity < threshold, reject politely with topic suggestions
        and return empty results to prevent hallucination in downstream LLM generation.
        """
        results = self.retriever.search(query, top_k=top_k, where_filter=where_filter)
        top_score = results[0].score if results else 0.0

        if top_score < self.threshold or not results:
            logger.info(
                "Guardrail REJECTED query: '%s' (top_score=%.4f < threshold=%.4f)",
                query,
                top_score,
                self.threshold,
            )
            return GuardrailDecision(
                is_accepted=False,
                query=query,
                top_score=top_score,
                threshold=self.threshold,
                results=[],  # Zero chunk leakage!
                rejection_message=self.DEFAULT_REJECTION_MESSAGE,
                suggested_topics=self.suggested_topics,
            )

        logger.info(
            "Guardrail ACCEPTED query: '%s' (top_score=%.4f >= threshold=%.4f)",
            query,
            top_score,
            self.threshold,
        )
        return GuardrailDecision(
            is_accepted=True,
            query=query,
            top_score=top_score,
            threshold=self.threshold,
            results=results,
            rejection_message=None,
            suggested_topics=[],
        )

    @staticmethod
    def evaluate_threshold_performance(
        query_scores: List[Tuple[str, float, bool]],
        threshold: float,
    ) -> Dict[str, float]:
        """Compute In-Domain vs Out-of-Domain classification metrics at a given threshold.

        query_scores: List of (query, top_score, is_in_domain_true)
        """
        tp = 0  # in-domain correctly accepted
        fp = 0  # out-of-domain falsely accepted
        tn = 0  # out-of-domain correctly rejected
        fn = 0  # in-domain falsely rejected

        for _, score, is_in_domain in query_scores:
            predicted_accept = score >= threshold
            if is_in_domain:
                if predicted_accept:
                    tp += 1
                else:
                    fn += 1
            else:
                if predicted_accept:
                    fp += 1
                else:
                    tn += 1

        accuracy = (tp + tn) / max(len(query_scores), 1)
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = (2 * precision * recall) / max(precision + recall, 1e-6)

        rejection_precision = tn / max(tn + fn, 1)
        rejection_recall = tn / max(tn + fp, 1)
        rejection_f1 = (2 * rejection_precision * rejection_recall) / max(rejection_precision + rejection_recall, 1e-6)

        return {
            "threshold": threshold,
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "rejection_precision": round(rejection_precision, 4),
            "rejection_recall": round(rejection_recall, 4),
            "rejection_f1": round(rejection_f1, 4),
        }
