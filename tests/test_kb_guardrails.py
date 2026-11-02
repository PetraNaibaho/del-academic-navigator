"""Unit tests for Relevance Threshold Guardrail module (src/kb/guardrails.py).

Tests in-domain acceptance, out-of-domain rejection with polite response,
zero chunk leakage on rejection, topic recommendations,
and threshold performance sweep metrics (TP/FP/TN/FN, precision, recall, F1).
"""

from unittest.mock import MagicMock
import pytest
from src.kb.guardrails import GuardrailDecision, RelevanceGuardrail
from src.kb.retriever import SearchResult, SemanticRetriever


@pytest.fixture
def mock_retriever() -> SemanticRetriever:
    return MagicMock(spec=SemanticRetriever)


def test_guardrail_in_domain_acceptance(mock_retriever: SemanticRetriever):
    # Simulated relevant search result above threshold (score=0.72 >= 0.44)
    fake_result = SearchResult(
        chunk_id="SOP-AKD-01#c000",
        doc_id="SOP-AKD-01",
        title="SOP Penjadwalan",
        category="SOP_AKADEMIK",
        chunk_index=0,
        text="Ketentuan kuliah pengganti minimal H-2.",
        score=0.72,
        distance=0.28,
        metadata={},
    )
    mock_retriever.search.return_value = [fake_result]

    guardrail = RelevanceGuardrail(retriever=mock_retriever, threshold=0.44)
    decision = guardrail.verify_query("Bagaimana cara menjadwalkan kuliah pengganti?")

    assert isinstance(decision, GuardrailDecision)
    assert decision.is_accepted is True
    assert decision.top_score == 0.72
    assert decision.threshold == 0.44
    assert len(decision.results) == 1
    assert decision.rejection_message is None
    assert decision.suggested_topics == []


def test_guardrail_out_of_domain_rejection_zero_leakage(mock_retriever: SemanticRetriever):
    # Simulated out-of-domain result with low score below threshold (score=0.25 < 0.44)
    fake_low_result = SearchResult(
        chunk_id="SOP-AKD-01#c000",
        doc_id="SOP-AKD-01",
        title="SOP Penjadwalan",
        category="SOP_AKADEMIK",
        chunk_index=0,
        text="Ketentuan kuliah pengganti minimal H-2.",
        score=0.25,
        distance=0.75,
        metadata={},
    )
    mock_retriever.search.return_value = [fake_low_result]

    guardrail = RelevanceGuardrail(retriever=mock_retriever, threshold=0.44)
    decision = guardrail.verify_query("Resep saksang babi khas Toba")

    assert decision.is_accepted is False
    assert decision.top_score == 0.25
    assert decision.threshold == 0.44
    # CRITICAL: Zero chunk leakage to prevent downstream RAG hallucination
    assert decision.results == []
    # Polite rejection message
    assert "di luar cakupan" in decision.rejection_message
    assert "Institut Teknologi Del" in decision.rejection_message
    # Useful topic recommendations
    assert len(decision.suggested_topics) >= 5
    assert any("Penjadwalan" in t for t in decision.suggested_topics)


def test_guardrail_empty_retrieval(mock_retriever: SemanticRetriever):
    # Case where retriever returns empty list
    mock_retriever.search.return_value = []

    guardrail = RelevanceGuardrail(retriever=mock_retriever, threshold=0.44)
    decision = guardrail.verify_query("Pertanyaan sembarang")

    assert decision.is_accepted is False
    assert decision.top_score == 0.0
    assert decision.results == []
    assert decision.rejection_message is not None


def test_guardrail_evaluate_threshold_performance():
    # Synthetic query score tuples: (query, top_score, is_in_domain_ground_truth)
    query_scores = [
        ("q_in_1", 0.75, True),   # TP
        ("q_in_2", 0.65, True),   # TP
        ("q_in_3", 0.35, True),   # FN (below 0.40)
        ("q_out_1", 0.20, False), # TN
        ("q_out_2", 0.45, False), # FP (above 0.40)
    ]

    metrics = RelevanceGuardrail.evaluate_threshold_performance(query_scores, threshold=0.40)

    assert metrics["threshold"] == 0.40
    assert metrics["tp"] == 2
    assert metrics["fp"] == 1
    assert metrics["tn"] == 1
    assert metrics["fn"] == 1
    assert metrics["accuracy"] == 0.60
    assert metrics["precision"] == pytest.approx(2 / 3, 1e-4)
    assert metrics["recall"] == pytest.approx(2 / 3, 1e-4)
    assert metrics["rejection_precision"] == 0.50
    assert metrics["rejection_recall"] == 0.50
