"""Word-aware recursive document chunker with overlap and deterministic hashing."""

import hashlib
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents an atomic, word-aware document chunk carrying rich metadata."""

    chunk_id: str
    doc_id: str
    text: str
    chunk_index: int
    total_chunks: int
    start_word: int
    end_word: int
    word_count: int
    content_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class WordAwareRecursiveChunker:
    """Recursive chunker that respects semantic boundaries (paragraphs, sentences, words)."""

    def __init__(
        self,
        chunk_size_words: int = 150,
        chunk_overlap_words: int = 30,
        min_chunk_words: int = 20,
    ):
        if chunk_size_words <= 0:
            raise ValueError(f"chunk_size_words must be > 0, got {chunk_size_words}")
        if chunk_overlap_words < 0:
            raise ValueError(f"chunk_overlap_words must be >= 0, got {chunk_overlap_words}")
        if chunk_overlap_words >= chunk_size_words:
            raise ValueError(
                f"chunk_overlap_words ({chunk_overlap_words}) must be strictly less than chunk_size_words ({chunk_size_words})"
            )

        self.chunk_size_words = chunk_size_words
        self.chunk_overlap_words = chunk_overlap_words
        self.min_chunk_words = min_chunk_words

        # Regex for splitting sentences while preserving terminal punctuation
        self.sentence_splitter = re.compile(r"(?<=[.!?])\s+")

    @staticmethod
    def compute_sha256(text: str) -> str:
        """Compute SHA-256 hash of text content."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _split_into_atomic_units(self, text: str) -> List[str]:
        """Split text into sentences/paragraphs without breaking words."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        units = []
        for para in paragraphs:
            sentences = self.sentence_splitter.split(para)
            for s in sentences:
                s_clean = s.strip()
                if s_clean:
                    units.append(s_clean)
        return units

    def chunk_text(
        self,
        text: str,
        doc_id: str,
        base_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        """Split text into word-aware chunks with overlap and inject metadata."""
        cleaned_text = text.strip()
        if not cleaned_text:
            return []

        base_meta = dict(base_metadata or {})
        units = self._split_into_atomic_units(cleaned_text)
        
        # If no punctuation units were found, treat whole text as a single unit or split by words
        if not units:
            units = [cleaned_text]

        # Group atomic units into chunks bounded by word count
        raw_chunks_data: List[Dict[str, Any]] = []
        current_words: List[str] = []
        global_word_offset = 0

        for unit in units:
            unit_words = unit.split()
            if not unit_words:
                continue

            # If adding this unit exceeds chunk_size, flush current chunk
            if len(current_words) + len(unit_words) > self.chunk_size_words and current_words:
                chunk_str = " ".join(current_words)
                start_w = global_word_offset
                end_w = global_word_offset + len(current_words)
                raw_chunks_data.append({
                    "text": chunk_str,
                    "start_word": start_w,
                    "end_word": end_w,
                    "words": current_words,
                })
                # Overlap: keep last `chunk_overlap_words` from current_words
                overlap_len = min(self.chunk_overlap_words, len(current_words))
                if overlap_len > 0:
                    current_words = current_words[-overlap_len:]
                    global_word_offset = end_w - overlap_len
                else:
                    current_words = []
                    global_word_offset = end_w

            # If a single sentence unit is longer than chunk_size_words, split it word by word
            if len(unit_words) > self.chunk_size_words:
                step = self.chunk_size_words - self.chunk_overlap_words
                for i in range(0, len(unit_words), step):
                    slice_words = unit_words[i : i + self.chunk_size_words]
                    chunk_str = " ".join(slice_words)
                    start_w = global_word_offset
                    end_w = global_word_offset + len(slice_words)
                    raw_chunks_data.append({
                        "text": chunk_str,
                        "start_word": start_w,
                        "end_word": end_w,
                        "words": slice_words,
                    })
                    global_word_offset += len(slice_words)
                current_words = []
            else:
                current_words.extend(unit_words)

        # Flush any remaining words
        if current_words:
            chunk_str = " ".join(current_words)
            # If the remaining chunk is smaller than min_chunk_words and we already have chunks,
            # merge it with the last chunk to avoid orphan fragments
            if len(current_words) < self.min_chunk_words and raw_chunks_data:
                last_chunk = raw_chunks_data[-1]
                merged_words = last_chunk["words"] + current_words
                last_chunk["text"] = " ".join(merged_words)
                last_chunk["end_word"] = last_chunk["end_word"] + len(current_words)
                last_chunk["words"] = merged_words
            else:
                start_w = global_word_offset
                end_w = global_word_offset + len(current_words)
                raw_chunks_data.append({
                    "text": chunk_str,
                    "start_word": start_w,
                    "end_word": end_w,
                    "words": current_words,
                })

        total_chunks = len(raw_chunks_data)
        now_iso = datetime.now(timezone.utc).isoformat()
        chunks: List[DocumentChunk] = []

        for idx, item in enumerate(raw_chunks_data):
            chunk_text_str = item["text"].strip()
            word_count = len(chunk_text_str.split())
            content_hash = self.compute_sha256(chunk_text_str)
            chunk_id = f"{doc_id}#c{idx:03d}"

            chunk_meta = dict(base_meta)
            chunk_meta.update({
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "chunk_index": idx,
                "total_chunks": total_chunks,
                "start_word": item["start_word"],
                "end_word": item["end_word"],
                "word_count": word_count,
                "content_hash": content_hash,
                "ingest_date": now_iso,
            })

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    text=chunk_text_str,
                    chunk_index=idx,
                    total_chunks=total_chunks,
                    start_word=item["start_word"],
                    end_word=item["end_word"],
                    word_count=word_count,
                    content_hash=content_hash,
                    metadata=chunk_meta,
                )
            )

        return chunks
