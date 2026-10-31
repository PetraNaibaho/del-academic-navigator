"""Compare the 3 candidate embedding models on the enterprise corpus and benchmark queries."""

import json
import os
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from src.kb.chunker import WordAwareRecursiveChunker
from src.kb.cleaner import TextCleaner
from src.kb.config import default_config
from src.kb.embedder import SentenceTransformerEmbedder
from src.kb.loader import DocumentLoader
from src.kb.retriever import SemanticRetriever
from src.kb.vector_store import ChromaVectorStore

MODELS = [
    ("paraphrase-multilingual-MiniLM-L12-v2", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
    ("multilingual-e5-small", "intfloat/multilingual-e5-small"),
    ("all-MiniLM-L6-v2", "sentence-transformers/all-MiniLM-L6-v2"),
]


def main():
    loader = DocumentLoader(default_config.CORPUS_DIR, default_config.MANIFEST_JSON)
    cleaner = TextCleaner()
    chunker = WordAwareRecursiveChunker(chunk_size_words=150, chunk_overlap_words=30)
    raw_docs = loader.load_directory()

    all_chunks = []
    for doc in raw_docs:
        c_text = cleaner.clean(doc.raw_text)
        all_chunks.extend(chunker.chunk_text(c_text, doc.doc_id, doc.metadata))

    queries = json.load(open(default_config.BENCHMARK_QUERIES_JSON, encoding="utf-8"))
    in_domain_queries = [q for q in queries if q["is_in_domain"]]
    out_domain_queries = [q for q in queries if not q["is_in_domain"]]

    comparison_results = []

    print("=" * 80)
    print("  EVALUASI KOMPARATIF MODEL EMBEDDING PADA KORPUS IT DEL")
    print("=" * 80)

    for alias, model_path in MODELS:
        print(f"\nEvaluating candidate model: {alias}...")
        start_init = time.perf_counter()
        embedder = SentenceTransformerEmbedder(model_name=model_path)
        init_time = time.perf_counter() - start_init

        temp_dir = default_config.PROJECT_ROOT / "data" / f"chroma_comp_{alias}"
        store = ChromaVectorStore(persist_dir=temp_dir, collection_name=f"comp_{alias.replace('-', '_')}")
        store.reset_collection()

        start_index = time.perf_counter()
        store.index_chunks(all_chunks, embedder, batch_size=32, skip_existing=False)
        index_time = time.perf_counter() - start_index

        retriever = SemanticRetriever(store, embedder)

        # In-domain evaluation
        hit1, hit3, hit5 = 0, 0, 0
        rrs = []
        in_scores = []
        latencies = []

        for q in in_domain_queries:
            t0 = time.perf_counter()
            res = retriever.search(q["query"], top_k=5)
            latencies.append((time.perf_counter() - t0) * 1000)

            retrieved_ids = [r.doc_id for r in res]
            target = q["target_doc_id"]
            top_score = res[0].score if res else 0.0
            in_scores.append(top_score)

            h1 = 1 if retrieved_ids and retrieved_ids[0] == target else 0
            h3 = 1 if target in retrieved_ids[:3] else 0
            h5 = 1 if target in retrieved_ids[:5] else 0

            hit1 += h1
            hit3 += h3
            hit5 += h5

            rr = 0.0
            for rank, did in enumerate(retrieved_ids, start=1):
                if did == target:
                    rr = 1.0 / rank
                    break
            rrs.append(rr)

        # Out-of-domain evaluation
        out_scores = []
        for q in out_domain_queries:
            res = retriever.search(q["query"], top_k=1)
            out_scores.append(res[0].score if res else 0.0)

        n_in = len(in_domain_queries)
        rec = {
            "model_alias": alias,
            "dimension": embedder.dimension,
            "hit@1": round(hit1 / n_in, 4),
            "hit@3": round(hit3 / n_in, 4),
            "hit@5": round(hit5 / n_in, 4),
            "mrr": round(float(np.mean(rrs)), 4),
            "mean_in_score": round(float(np.mean(in_scores)), 4),
            "mean_out_score": round(float(np.mean(out_scores)), 4),
            "max_out_score": round(float(np.max(out_scores)), 4),
            "score_separation": round(float(np.mean(in_scores) - np.mean(out_scores)), 4),
            "avg_latency_ms": round(float(np.mean(latencies)), 2),
            "indexing_time_s": round(index_time, 2),
        }
        comparison_results.append(rec)

        # Cleanup temp store
        try:
            store.reset_collection()
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

    print("\n" + "=" * 80)
    print(f"{'Model':<36} | {'Dim':<4} | {'Hit@1':<6} | {'Hit@3':<6} | {'MRR':<6} | {'In-Score':<8} | {'Out-Score':<9} | {'Sep':<6} | {'Lat(ms)':<7}")
    print("-" * 105)
    for r in comparison_results:
        print(f"{r['model_alias']:<36} | {r['dimension']:<4} | {r['hit@1']*100:>5.1f}% | {r['hit@3']*100:>5.1f}% | {r['mrr']:>6.4f} | {r['mean_in_score']:>8.4f} | {r['mean_out_score']:>9.4f} | {r['score_separation']:>6.4f} | {r['avg_latency_ms']:>7.2f}")
    print("=" * 105)

    # Save to reports
    out_csv = default_config.REPORTS_DIR / "model_comparison_benchmark.csv"
    import pandas as pd
    pd.DataFrame(comparison_results).to_csv(out_csv, index=False)
    print(f"\n[OK] Saved model comparison results to: {out_csv}")


if __name__ == "__main__":
    main()
