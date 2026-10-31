"""Comprehensive benchmarking, ablation study, and guardrail calibration suite."""

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

mpl_dir = Path(__file__).resolve().parent.parent.parent / "reports" / ".mpl"
mpl_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(mpl_dir))

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for automated environments
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.kb.chunker import WordAwareRecursiveChunker
from src.kb.cleaner import TextCleaner
from src.kb.config import default_config
from src.kb.embedder import SentenceTransformerEmbedder
from src.kb.guardrails import RelevanceGuardrail
from src.kb.loader import DocumentLoader
from src.kb.retriever import SearchResult, SemanticRetriever
from src.kb.vector_store import ChromaVectorStore

logger = logging.getLogger(__name__)


class BenchmarkSuite:
    """Enterprise evaluation engine for semantic search, ablation experiments, and guardrails."""

    def __init__(self, config=default_config):
        self.config = config
        self.loader = DocumentLoader(self.config.CORPUS_DIR, self.config.MANIFEST_JSON)
        self.cleaner = TextCleaner()

    def load_benchmark_queries(self) -> List[Dict[str, Any]]:
        """Load benchmark queries from JSON file."""
        if not self.config.BENCHMARK_QUERIES_JSON.exists():
            raise FileNotFoundError(f"Queries file not found: {self.config.BENCHMARK_QUERIES_JSON}")
        with open(self.config.BENCHMARK_QUERIES_JSON, "r", encoding="utf-8") as f:
            return json.load(f)

    def evaluate_retriever(
        self,
        retriever: SemanticRetriever,
        queries: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Run evaluation metrics on in-domain queries: Hit@1, Hit@3, Hit@5, MRR, Mean Similarity."""
        in_domain_queries = [q for q in queries if q.get("is_in_domain", True)]
        results_by_query = []

        hit1_count = 0
        hit3_count = 0
        hit5_count = 0
        reciprocal_ranks = []
        top1_scores = []

        # Category breakdowns
        cat_metrics: Dict[str, Dict[str, Any]] = {}

        for q in in_domain_queries:
            query_text = q["query"]
            target_doc_id = q["target_doc_id"]
            cat = q.get("category", "general")

            start_t = time.perf_counter()
            retrieved = retriever.search(query_text, top_k=top_k)
            latency_ms = (time.perf_counter() - start_t) * 1000.0

            retrieved_doc_ids = [r.doc_id for r in retrieved]
            top_score = retrieved[0].score if retrieved else 0.0
            top1_scores.append(top_score)

            # Hit checks
            h1 = 1 if retrieved_doc_ids and retrieved_doc_ids[0] == target_doc_id else 0
            h3 = 1 if target_doc_id in retrieved_doc_ids[:3] else 0
            h5 = 1 if target_doc_id in retrieved_doc_ids[:5] else 0

            hit1_count += h1
            hit3_count += h3
            hit5_count += h5

            # MRR
            rr = 0.0
            for rank, did in enumerate(retrieved_doc_ids, start=1):
                if did == target_doc_id:
                    rr = 1.0 / rank
                    break
            reciprocal_ranks.append(rr)

            # Record per-query details
            results_by_query.append({
                "query_id": q.get("query_id", ""),
                "category": cat,
                "query": query_text,
                "target_doc_id": target_doc_id,
                "retrieved_top1": retrieved_doc_ids[0] if retrieved_doc_ids else "NONE",
                "top1_score": round(top_score, 4),
                "hit@1": h1,
                "hit@3": h3,
                "hit@5": h5,
                "reciprocal_rank": round(rr, 4),
                "latency_ms": round(latency_ms, 2),
            })

            # Update category accumulators
            if cat not in cat_metrics:
                cat_metrics[cat] = {"count": 0, "hit1": 0, "hit3": 0, "mrr": 0.0, "scores": []}
            cat_metrics[cat]["count"] += 1
            cat_metrics[cat]["hit1"] += h1
            cat_metrics[cat]["hit3"] += h3
            cat_metrics[cat]["mrr"] += rr
            cat_metrics[cat]["scores"].append(top_score)

        n_queries = max(len(in_domain_queries), 1)
        summary = {
            "total_evaluated_queries": n_queries,
            "hit@1": round(hit1_count / n_queries, 4),
            "hit@3": round(hit3_count / n_queries, 4),
            "hit@5": round(hit5_count / n_queries, 4),
            "mrr": round(float(np.mean(reciprocal_ranks)), 4),
            "mean_top1_similarity": round(float(np.mean(top1_scores)), 4),
            "min_top1_similarity": round(float(np.min(top1_scores)), 4) if top1_scores else 0.0,
            "max_top1_similarity": round(float(np.max(top1_scores)), 4) if top1_scores else 0.0,
            "category_breakdown": {
                c: {
                    "count": v["count"],
                    "hit@1": round(v["hit1"] / v["count"], 4),
                    "hit@3": round(v["hit3"] / v["count"], 4),
                    "mrr": round(v["mrr"] / v["count"], 4),
                    "mean_score": round(float(np.mean(v["scores"])), 4),
                }
                for c, v in cat_metrics.items()
            },
            "query_details": results_by_query,
        }
        return summary

    def evaluate_lexical_baseline(
        self,
        all_chunks: List[Any],
        queries: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Compute keyword / lexical matching baseline (TF-IDF style token overlap)."""
        in_domain_queries = [q for q in queries if q.get("is_in_domain", True)]
        hit1_count = 0
        hit3_count = 0
        reciprocal_ranks = []
        cat_metrics: Dict[str, Dict[str, Any]] = {}

        for q in in_domain_queries:
            query_tokens = set(q["query"].lower().split())
            target_doc_id = q["target_doc_id"]
            cat = q.get("category", "general")

            scores = []
            for chunk in all_chunks:
                chunk_tokens = chunk.text.lower().split()
                overlap = sum(1 for t in chunk_tokens if t in query_tokens)
                scores.append((chunk.doc_id, overlap / (len(chunk_tokens) + 1e-5)))

            scores.sort(key=lambda x: x[1], reverse=True)
            retrieved_doc_ids = [s[0] for s in scores[:top_k]]

            h1 = 1 if retrieved_doc_ids and retrieved_doc_ids[0] == target_doc_id else 0
            h3 = 1 if target_doc_id in retrieved_doc_ids[:3] else 0
            rr = 0.0
            for rank, did in enumerate(retrieved_doc_ids, start=1):
                if did == target_doc_id:
                    rr = 1.0 / rank
                    break

            hit1_count += h1
            hit3_count += h3
            reciprocal_ranks.append(rr)

            if cat not in cat_metrics:
                cat_metrics[cat] = {"count": 0, "hit1": 0, "hit3": 0, "mrr": 0.0}
            cat_metrics[cat]["count"] += 1
            cat_metrics[cat]["hit1"] += h1
            cat_metrics[cat]["hit3"] += h3
            cat_metrics[cat]["mrr"] += rr

        n_queries = max(len(in_domain_queries), 1)
        return {
            "hit@1": round(hit1_count / n_queries, 4),
            "hit@3": round(hit3_count / n_queries, 4),
            "mrr": round(float(np.mean(reciprocal_ranks)), 4),
            "category_breakdown": {
                c: {
                    "hit@1": round(v["hit1"] / v["count"], 4),
                    "hit@3": round(v["hit3"] / v["count"], 4),
                    "mrr": round(v["mrr"] / v["count"], 4),
                }
                for c, v in cat_metrics.items()
            },
        }

    def sweep_guardrail_thresholds(
        self,
        retriever: SemanticRetriever,
        queries: List[Dict[str, Any]],
        start: float = 0.20,
        stop: float = 0.85,
        step: float = 0.02,
    ) -> List[Dict[str, float]]:
        """Evaluate precision, recall, F1, and rejection metrics across a range of thresholds."""
        # 1. Collect top-1 scores for all queries
        query_score_tuples = []
        for q in queries:
            results = retriever.search(q["query"], top_k=1)
            score = results[0].score if results else 0.0
            is_in_domain = bool(q.get("is_in_domain", True))
            query_score_tuples.append((q["query"], score, is_in_domain))

        # 2. Evaluate performance across threshold grid
        thresholds = np.arange(start, stop + step / 2, step)
        sweep_results = []
        for t in thresholds:
            t_round = round(float(t), 4)
            metrics = RelevanceGuardrail.evaluate_threshold_performance(query_score_tuples, t_round)
            sweep_results.append(metrics)

        return sweep_results

    def run_chunking_ablation(
        self,
        raw_docs: List[Any],
        embedder: Any,
        queries: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Empirical ablation study on chunk sizes (100, 150, 200, 300 words) and overlaps (0%, 10%, 20%)."""
        configs = [
            {"size": 100, "overlap": 0},
            {"size": 100, "overlap": 10},
            {"size": 150, "overlap": 0},
            {"size": 150, "overlap": 15},
            {"size": 150, "overlap": 30},  # Config default (20%)
            {"size": 200, "overlap": 20},
            {"size": 200, "overlap": 40},
            {"size": 300, "overlap": 30},
            {"size": 300, "overlap": 60},
        ]

        ablation_results = []
        in_domain_queries = [q for q in queries if q.get("is_in_domain", True)]

        for cfg in configs:
            c_size = cfg["size"]
            c_overlap = cfg["overlap"]
            chunker = WordAwareRecursiveChunker(chunk_size_words=c_size, chunk_overlap_words=c_overlap)

            # Chunk documents
            all_chunks = []
            for doc in raw_docs:
                cleaned_text = self.cleaner.clean(doc.raw_text)
                chunks = chunker.chunk_text(cleaned_text, doc.doc_id, doc.metadata)
                all_chunks.extend(chunks)

            # Create ephemeral in-memory / temp Chroma collection for ablation test
            temp_dir = self.config.PROJECT_ROOT / "data" / f"temp_ablation_s{c_size}_o{c_overlap}"
            temp_store = ChromaVectorStore(persist_dir=temp_dir, collection_name=f"ablation_{c_size}_{c_overlap}")
            temp_store.reset_collection()
            temp_store.index_chunks(all_chunks, embedder, batch_size=32, skip_existing=False)

            temp_retriever = SemanticRetriever(temp_store, embedder)
            eval_metrics = self.evaluate_retriever(temp_retriever, in_domain_queries, top_k=3)

            # Clean up temp store collection
            try:
                temp_store.reset_collection()
                import shutil
                if temp_dir.exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

            chunk_lengths = [c.word_count for c in all_chunks]
            ablation_results.append({
                "chunk_size_words": c_size,
                "chunk_overlap_words": c_overlap,
                "overlap_pct": round((c_overlap / c_size) * 100, 1),
                "total_chunks": len(all_chunks),
                "mean_chunk_words": round(float(np.mean(chunk_lengths)), 1),
                "max_chunk_words": int(np.max(chunk_lengths)) if chunk_lengths else 0,
                "hit@1": eval_metrics["hit@1"],
                "hit@3": eval_metrics["hit@3"],
                "mrr": eval_metrics["mrr"],
                "mean_top1_score": eval_metrics["mean_top1_similarity"],
            })

        return ablation_results

    def generate_all_plots_and_reports(
        self,
        semantic_eval: Dict[str, Any],
        lexical_eval: Dict[str, Any],
        sweep_data: List[Dict[str, float]],
        ablation_data: List[Dict[str, Any]],
        all_query_scores: List[Tuple[str, float, bool, str]],
    ) -> None:
        """Render high-resolution figures and markdown/CSV report summaries in reports/."""
        self.config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        self.config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

        # -------------------------------------------------------------
        # Figure 1: Semantic Search vs Lexical Baseline by Category
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
        categories = ["synonym_non_literal", "literal_baseline", "mixed_typo"]
        cat_labels = ["Sinonim Non-Literal", "Literal Baseline", "Mixed / Typo"]

        sem_hits = [semantic_eval["category_breakdown"].get(c, {}).get("hit@1", 0.0) for c in categories]
        lex_hits = [lexical_eval["category_breakdown"].get(c, {}).get("hit@1", 0.0) for c in categories]

        x = np.arange(len(categories))
        width = 0.35

        rects1 = ax.bar(x - width / 2, sem_hits, width, label="Sentence-Transformers (Dense Semantic)", color="#004B87")
        rects2 = ax.bar(x + width / 2, lex_hits, width, label="Keyword Baseline (Lexical / BM25)", color="#DC2626")

        ax.set_ylabel("Hit@1 Accuracy", fontsize=11, fontweight="bold")
        ax.set_title("Perbandingan Temu Balik: Semantic Search vs Lexical Baseline", fontsize=12, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(cat_labels, fontsize=10)
        ax.set_ylim(0, 1.15)
        ax.legend(frameon=True)

        for rect in rects1:
            h = rect.get_height()
            ax.annotate(f"{h:.2f}", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")
        for rect in rects2:
            h = rect.get_height()
            ax.annotate(f"{h:.2f}", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom", fontsize=9)

        plt.tight_layout()
        fig1_path = self.config.FIGURES_DIR / "semantic_vs_lexical_comparison.png"
        fig.savefig(fig1_path)
        plt.close(fig)

        # -------------------------------------------------------------
        # Figure 2: Guardrail Threshold Sweep (Precision, Recall, F1)
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
        t_vals = [s["threshold"] for s in sweep_data]
        f1_vals = [s["f1"] for s in sweep_data]
        prec_vals = [s["precision"] for s in sweep_data]
        rec_vals = [s["recall"] for s in sweep_data]
        rej_prec = [s["rejection_precision"] for s in sweep_data]

        ax.plot(t_vals, prec_vals, label="In-Domain Precision", color="#2563EB", lw=2, linestyle="--")
        ax.plot(t_vals, rec_vals, label="In-Domain Recall", color="#10B981", lw=2, linestyle=":")
        ax.plot(t_vals, f1_vals, label="In-Domain F1-Score", color="#1E3A8A", lw=2.5)
        ax.plot(t_vals, rej_prec, label="Rejection Precision (OOD)", color="#EF4444", lw=2)

        # Highlight calibrated threshold
        best_t = self.config.RELEVANCE_THRESHOLD
        ax.axvline(x=best_t, color="#DC2626", linestyle="-.", lw=1.5, label=f"Ambang Terpilih (τ = {best_t:.2f})")

        ax.set_xlabel("Cosine Similarity Threshold (τ)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Nilai Metrik", fontsize=11, fontweight="bold")
        ax.set_title("Kalibrasi Guardrail: Kurva Precision-Recall & F1 vs Ambang Relevansi", fontsize=12, fontweight="bold")
        ax.set_ylim(-0.05, 1.1)
        ax.set_xlim(min(t_vals), max(t_vals))
        ax.legend(frameon=True, loc="lower left")

        plt.tight_layout()
        fig2_path = self.config.FIGURES_DIR / "guardrail_threshold_sweep.png"
        fig.savefig(fig2_path)
        plt.close(fig)

        # -------------------------------------------------------------
        # Figure 3: Score Distribution (In-Domain vs Out-of-Domain)
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
        in_scores = [item[1] for item in all_query_scores if item[2] is True]
        out_scores = [item[1] for item in all_query_scores if item[2] is False]

        bins = np.linspace(0.1, 0.9, 17)
        ax.hist(in_scores, bins=bins, alpha=0.75, label=f"In-Domain ({len(in_scores)} kueri)", color="#004B87", edgecolor="white")
        ax.hist(out_scores, bins=bins, alpha=0.75, label=f"Out-of-Domain ({len(out_scores)} kueri)", color="#EF4444", edgecolor="white")
        ax.axvline(x=self.config.RELEVANCE_THRESHOLD, color="#B91C1C", linestyle="--", lw=2, label=f"Threshold = {self.config.RELEVANCE_THRESHOLD}")

        ax.set_xlabel("Top-1 Cosine Similarity Score", fontsize=11, fontweight="bold")
        ax.set_ylabel("Jumlah Kueri", fontsize=11, fontweight="bold")
        ax.set_title("Distribusi Skor Cosine Similarity: In-Domain vs Out-of-Domain", fontsize=12, fontweight="bold")
        ax.legend(frameon=True)

        plt.tight_layout()
        fig3_path = self.config.FIGURES_DIR / "score_distribution_in_vs_out_domain.png"
        fig.savefig(fig3_path)
        plt.close(fig)

        # -------------------------------------------------------------
        # Figure 4: Chunking Ablation Study
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
        cfg_labels = [f"s{d['chunk_size_words']}_o{d['chunk_overlap_words']}" for d in ablation_data]
        mrr_vals = [d["mrr"] for d in ablation_data]
        hit1_vals = [d["hit@1"] for d in ablation_data]

        x = np.arange(len(cfg_labels))
        ax.plot(x, hit1_vals, marker="o", lw=2, color="#004B87", label="Hit@1")
        ax.plot(x, mrr_vals, marker="s", lw=2, color="#10B981", linestyle="--", label="MRR")
        ax.set_xticks(x)
        ax.set_xticklabels(cfg_labels, rotation=45, ha="right", fontsize=9)
        ax.set_ylabel("Nilai Metrik Temu Balik", fontsize=11, fontweight="bold")
        ax.set_title("Eksperimen Ablasi Parameter Chunking (Ukuran Kata & Overlap)", fontsize=12, fontweight="bold")
        ax.set_ylim(0.5, 1.05)
        ax.legend(frameon=True)

        plt.tight_layout()
        fig4_path = self.config.FIGURES_DIR / "chunking_ablation_grid.png"
        fig.savefig(fig4_path)
        plt.close(fig)

        # Save Markdown and CSV reports
        df_ablation = pd.DataFrame(ablation_data)
        df_ablation.to_csv(self.config.REPORTS_DIR / "chunking_ablation_results.csv", index=False)

        df_sweep = pd.DataFrame(sweep_data)
        df_sweep.to_csv(self.config.REPORTS_DIR / "guardrail_sweep_results.csv", index=False)

        logger.info("All figures and reports successfully generated in %s", self.config.REPORTS_DIR)
