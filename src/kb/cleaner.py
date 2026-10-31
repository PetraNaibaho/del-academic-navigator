"""Text preprocessing and cleaning module for enterprise documents.

Implements Unicode NFKC normalization, hyphenation repair,
header/footer removal, whitespace normalization, and document structure preservation.
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union


@dataclass
class CleaningStats:
    """Statistics comparing document text before and after cleaning."""

    original_chars: int
    cleaned_chars: int
    original_words: int
    cleaned_words: int
    char_reduction_pct: float
    word_reduction_pct: float
    hyphens_fixed_count: int
    headers_footers_removed_count: int


class TextCleaner:
    """Enterprise text preprocessing cleaner preserving structural markers."""

    # Regex patterns for headers, footers, and page numbers
    HEADER_FOOTER_PATTERNS = [
        re.compile(r"^\s*INSTITUT TEKNOLOGI DEL\s*[-–]\s*DOKUMEN RESMI\s*$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^\s*Halaman\s+\d+\s+dari\s+\d+\s*$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^\s*Halaman\s+\d+\s*$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^\s*Page\s+\d+\s+of\s+\d+\s*$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^\s*Institut Teknologi Del\s*[-–]\s*Sistem Manajemen Pengetahuan Enterprise\s*$", re.IGNORECASE | re.MULTILINE),
    ]

    # Hyphenation pattern across linebreaks: e.g. "pembe- \n lajaran" -> "pembelajaran"
    HYPHENATION_PATTERN = re.compile(r"(\b[a-zA-Z\u00C0-\u024F]+)-\s*\n\s*([a-zA-Z\u00C0-\u024F]+\b)")

    def __init__(self, preserve_markdown_headers: bool = True):
        self.preserve_markdown_headers = preserve_markdown_headers

    def normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters using NFKC (Compatibility Decomposition + Canonical Composition)."""
        return unicodedata.normalize("NFKC", text)

    def fix_hyphenation(self, text: str) -> Tuple[str, int]:
        """Repair words broken by hyphenation across linebreaks."""
        matches = len(self.HYPHENATION_PATTERN.findall(text))
        fixed_text = self.HYPHENATION_PATTERN.sub(r"\1\2", text)
        return fixed_text, matches

    def remove_headers_and_footers(self, text: str) -> Tuple[str, int]:
        """Strip repetitive headers, footers, and page numbering artifacts."""
        total_removed = 0
        cleaned = text
        for pattern in self.HEADER_FOOTER_PATTERNS:
            matches = len(pattern.findall(cleaned))
            total_removed += matches
            cleaned = pattern.sub("", cleaned)
        return cleaned, total_removed

    def normalize_whitespace(self, text: str) -> str:
        """Normalize excessive horizontal spaces and multiple blank lines while preserving structural breaks."""
        lines = text.split("\n")
        normalized_lines = []
        for line in lines:
            # Replace multiple spaces/tabs with a single space, strip trailing
            norm_line = re.sub(r"[ \t]+", " ", line).strip()
            normalized_lines.append(norm_line)

        # Recombine and compress consecutive empty lines (max 2 newlines = 1 blank line)
        joined = "\n".join(normalized_lines)
        joined = re.sub(r"\n{3,}", "\n\n", joined)
        return joined.strip()

    def clean(self, text: str) -> str:
        """Execute full cleaning pipeline on input text."""
        cleaned, _ = self.clean_with_stats(text)
        return cleaned

    def clean_with_stats(self, text: str) -> Tuple[str, CleaningStats]:
        """Execute full cleaning pipeline and return cleaned text alongside comparative statistics."""
        if not text:
            stats = CleaningStats(0, 0, 0, 0, 0.0, 0.0, 0, 0)
            return "", stats

        original_chars = len(text)
        original_words = len(text.split())

        # Step 1: Unicode Normalization (NFKC)
        step1 = self.normalize_unicode(text)

        # Step 2: Fix Hyphenation across linebreaks
        step2, hyphens_count = self.fix_hyphenation(step1)

        # Step 3: Remove repetitive headers, footers, page numbers
        step3, hf_count = self.remove_headers_and_footers(step2)

        # Step 4: Normalize whitespace & blank lines
        cleaned = self.normalize_whitespace(step3)

        cleaned_chars = len(cleaned)
        cleaned_words = len(cleaned.split())

        char_red = round(((original_chars - cleaned_chars) / max(original_chars, 1)) * 100, 2)
        word_red = round(((original_words - cleaned_words) / max(original_words, 1)) * 100, 2)

        stats = CleaningStats(
            original_chars=original_chars,
            cleaned_chars=cleaned_chars,
            original_words=original_words,
            cleaned_words=cleaned_words,
            char_reduction_pct=char_red,
            word_reduction_pct=word_red,
            hyphens_fixed_count=hyphens_count,
            headers_footers_removed_count=hf_count
        )
        return cleaned, stats
