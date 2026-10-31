"""Command-line interface (CLI) for Del-Academic Navigator Knowledge Base & Vector Store."""

import argparse
import logging
import sys
from pathlib import Path
from typing import List

from src.kb.benchmark import BenchmarkSuite
from src.kb.chunker import WordAwareRecursiveChunker
from src.kb.cleaner import TextCleaner
from src.kb.config import default_config
from src.kb.embedder import SentenceTransformerEmbedder
from src.kb.guardrails import RelevanceGuardrail
from src.kb.loader import DocumentLoader
from src.kb.retriever import SemanticRetriever
from src.kb.vector_store import ChromaVectorStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("del-nav.kb")


def cmd_ingest(args):
    """Ingest documents, clean, chunk, and index into ChromaDB."""
    print("=" * 70)
    print("  DEL-ACADEMIC NAVIGATOR: PIPELINE INGESTION & PERSISTENT INDEXING")
    print("=" * 70)

    loader = DocumentLoader(default_config.CORPUS_DIR, default_config.MANIFEST_JSON)
    cleaner = TextCleaner()
    chunker = WordAwareRecursiveChunker(
        chunk_size_words=default_config.DEFAULT_CHUNK_SIZE_WORDS,
        chunk_overlap_words=default_config.DEFAULT_CHUNK_OVERLAP_WORDS,
    )

    print(f"\n[1/4] Loading documents from: {default_config.CORPUS_DIR}")
    raw_docs = loader.load_directory()
    print(f"      Total loaded documents: {len(raw_docs)}")

    print(f"\n[2/4] Preprocessing & Chunking (Size: {chunker.chunk_size_words} words, Overlap: {chunker.chunk_overlap_words} words)")
    all_chunks = []
    cleaning_stats_list = []

    for doc in raw_docs:
        cleaned_text, stats = cleaner.clean_with_stats(doc.raw_text)
        cleaning_stats_list.append((doc.doc_id, stats))
        chunks = chunker.chunk_text(cleaned_text, doc.doc_id, doc.metadata)
        all_chunks.extend(chunks)

    print(f"      Total extracted chunks: {len(all_chunks)}")

    print(f"\n[3/4] Initializing Embedding Model: {default_config.DEFAULT_MODEL_NAME}")
    embedder = SentenceTransformerEmbedder(model_name=default_config.DEFAULT_MODEL_NAME)

    print(f"\n[4/4] Storing into ChromaDB: {default_config.CHROMA_DIR}")
    store = ChromaVectorStore(
        persist_dir=default_config.CHROMA_DIR,
        collection_name=default_config.COLLECTION_NAME,
    )
    if args.reset:
        store.reset_collection()

    indexed_count = store.index_chunks(all_chunks, embedder, batch_size=32, skip_existing=not args.reset)
    print(f"\n[SUCCESS] Ingestion completed!")
    print(f"          New indexed chunks: {indexed_count}")
    print(f"          Total in collection: {store.count()}")


def cmd_search(args):
    """Perform semantic search with relevance guardrail."""
    query = args.query.strip()
    if not query:
        print("[ERROR] Query cannot be empty.")
        sys.exit(1)

    print("=" * 70)
    print(f"  DEL-ACADEMIC NAVIGATOR: SEMANTIC SEARCH")
    print(f"  Query: '{query}'")
    if args.category:
        print(f"  Filter Category: '{args.category}'")
    print("=" * 70)

    embedder = SentenceTransformerEmbedder(model_name=default_config.DEFAULT_MODEL_NAME)
    store = ChromaVectorStore(
        persist_dir=default_config.CHROMA_DIR,
        collection_name=default_config.COLLECTION_NAME,
    )
    retriever = SemanticRetriever(store, embedder)
    guardrail = RelevanceGuardrail(retriever, threshold=default_config.RELEVANCE_THRESHOLD)

    where_filter = {"category": args.category} if args.category else None
    decision = guardrail.verify_query(query, top_k=args.top_k, where_filter=where_filter)

    if not decision.is_accepted:
        print(f"\n[STATUS: REJECTED (Out-of-Domain Guardrail)]")
        print(f"Top Score: {decision.top_score:.4f} < Threshold: {decision.threshold:.4f}\n")
        print(f"Pesan Sistem:")
        print(f"  {decision.rejection_message}\n")
        print(f"Topik yang Tersedia dalam Basis Pengetahuan IT Del:")
        for topic in decision.suggested_topics[:8]:
            print(f"  * {topic}")
    else:
        print(f"\n[STATUS: ACCEPTED (In-Domain)]")
        print(f"Top Score: {decision.top_score:.4f} >= Threshold: {decision.threshold:.4f}\n")
        print(f"Ditemukan {len(decision.results)} chunk relevan:\n")
        for rank, res in enumerate(decision.results, start=1):
            print(f"--- [Peringkat #{rank}] Doc ID: {res.doc_id} | Skor Cosine: {res.score:.4f} ---")
            print(f"Judul Dokumen: {res.title}")
            print(f"Kategori: {res.category} | Chunk Index: #{res.chunk_index}")
            print(f"Kutipan:\n{res.text}\n")


def cmd_benchmark(args):
    """Run retrieval benchmark and print metrics."""
    print("=" * 70)
    print("  DEL-ACADEMIC NAVIGATOR: RETRIEVAL BENCHMARK EVALUATION")
    print("=" * 70)

    suite = BenchmarkSuite()
    queries = suite.load_benchmark_queries()

    embedder = SentenceTransformerEmbedder(model_name=default_config.DEFAULT_MODEL_NAME)
    store = ChromaVectorStore(
        persist_dir=default_config.CHROMA_DIR,
        collection_name=default_config.COLLECTION_NAME,
    )
    retriever = SemanticRetriever(store, embedder)

    eval_results = suite.evaluate_retriever(retriever, queries, top_k=5)

    print("\n--- HASIL METRIK TEMU BALIK SEMANTIK ---")
    print(f"Total Kueri In-Domain : {eval_results['total_evaluated_queries']}")
    print(f"Hit@1 Accuracy        : {eval_results['hit@1'] * 100:.2f}%")
    print(f"Hit@3 Accuracy        : {eval_results['hit@3'] * 100:.2f}%")
    print(f"Hit@5 Accuracy        : {eval_results['hit@5'] * 100:.2f}%")
    print(f"Mean Reciprocal Rank  : {eval_results['mrr']:.4f}")
    print(f"Mean Top-1 Similarity : {eval_results['mean_top1_similarity']:.4f}")

    print("\n--- RINCIAN PER KATEGORI KUERI ---")
    for cat, data in eval_results["category_breakdown"].items():
        print(f"  [{cat.upper()}] (n={data['count']}):")
        print(f"      Hit@1: {data['hit@1']*100:.1f}% | Hit@3: {data['hit@3']*100:.1f}% | MRR: {data['mrr']:.4f} | Rata-rata Skor: {data['mean_score']:.4f}")


def cmd_report(args):
    """Execute end-to-end benchmark, ablations, threshold sweep, and render report figures."""
    print("=" * 70)
    print("  DEL-ACADEMIC NAVIGATOR: GENERATE COMPREHENSIVE BENCHMARK REPORTS")
    print("=" * 70)

    suite = BenchmarkSuite()
    loader = DocumentLoader(default_config.CORPUS_DIR, default_config.MANIFEST_JSON)
    raw_docs = loader.load_directory()
    queries = suite.load_benchmark_queries()

    embedder = SentenceTransformerEmbedder(model_name=default_config.DEFAULT_MODEL_NAME)
    store = ChromaVectorStore(
        persist_dir=default_config.CHROMA_DIR,
        collection_name=default_config.COLLECTION_NAME,
    )
    retriever = SemanticRetriever(store, embedder)

    # 1. Chunk all documents to provide lexical matching corpus
    chunker = WordAwareRecursiveChunker()
    cleaner = TextCleaner()
    all_chunks = []
    for doc in raw_docs:
        c_text = cleaner.clean(doc.raw_text)
        all_chunks.extend(chunker.chunk_text(c_text, doc.doc_id, doc.metadata))

    print("\n[1/5] Evaluating Dense Semantic Search...")
    semantic_eval = suite.evaluate_retriever(retriever, queries, top_k=5)

    print("\n[2/5] Evaluating Lexical Baseline (BM25 / Keyword Overlap)...")
    lexical_eval = suite.evaluate_lexical_baseline(all_chunks, queries, top_k=5)

    print("\n[3/5] Running Guardrail Threshold Sweep (0.20 to 0.85)...")
    sweep_data = suite.sweep_guardrail_thresholds(retriever, queries, start=0.20, stop=0.85, step=0.02)

    print("\n[4/5] Running Chunking Ablation Study Grid...")
    ablation_data = suite.run_chunking_ablation(raw_docs, embedder, queries)

    # Collect all query scores for histogram
    query_scores_tuples = []
    for q in queries:
        res = retriever.search(q["query"], top_k=1)
        score = res[0].score if res else 0.0
        query_scores_tuples.append((q["query"], score, bool(q.get("is_in_domain", True)), q.get("category", "")))

    print("\n[5/5] Generating Plots and CSV Reports in reports/...")
    suite.generate_all_plots_and_reports(
        semantic_eval=semantic_eval,
        lexical_eval=lexical_eval,
        sweep_data=sweep_data,
        ablation_data=ablation_data,
        all_query_scores=query_scores_tuples,
    )

    print("\n[SUCCESS] All benchmark artifacts and figures generated successfully!")
    print(f"          Check {default_config.REPORTS_DIR} and {default_config.FIGURES_DIR}")


def main():
    parser = argparse.ArgumentParser(
        description="Del-Academic Navigator: Enterprise Knowledge Base & Vector Search CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand to execute")

    # Ingest subcommand
    parser_ingest = subparsers.add_parser("ingest", help="Ingest, clean, chunk, and index corpus")
    parser_ingest.add_argument("--reset", action="store_true", help="Reset collection before indexing")

    # Search subcommand
    parser_search = subparsers.add_parser("search", help="Perform semantic search on knowledge base")
    parser_search.add_argument("query", type=str, help="Search query string")
    parser_search.add_argument("--top-k", type=int, default=3, help="Number of chunks to retrieve")
    parser_search.add_argument("--category", type=str, default=None, help="Optional category filter")

    # Benchmark subcommand
    parser_benchmark = subparsers.add_parser("benchmark", help="Run retrieval benchmark metrics")

    # Report subcommand
    parser_report = subparsers.add_parser("report", help="Run full benchmark suite and generate figures")

    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    if args.subcommand == "ingest":
        cmd_ingest(args)
    elif args.subcommand == "search":
        cmd_search(args)
    elif args.subcommand == "benchmark":
        cmd_benchmark(args)
    elif args.subcommand == "report":
        cmd_report(args)


if __name__ == "__main__":
    main()
