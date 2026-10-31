"""Document loader module supporting .txt, .md, and .pdf formats for Enterprise Corpus."""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

import pypdf

logger = logging.getLogger(__name__)


@dataclass
class RawDocument:
    """Represents a loaded raw document before preprocessing and chunking."""

    doc_id: str
    title: str
    category: str
    format: str
    source_file: str
    raw_text: str
    char_count: int
    word_count: int
    metadata: Dict[str, Union[str, int, float]] = field(default_factory=dict)


class DocumentLoader:
    """Enterprise document loader with support for Markdown, Plain Text, and PDF files."""

    def __init__(self, corpus_dir: Optional[Union[str, Path]] = None, manifest_path: Optional[Union[str, Path]] = None):
        self.corpus_dir = Path(corpus_dir) if corpus_dir else None
        self.manifest_path = Path(manifest_path) if manifest_path else None
        self._manifest_cache: Dict[str, dict] = {}
        if self.manifest_path and self.manifest_path.is_file():
            self._load_manifest()

    def _load_manifest(self) -> None:
        """Load manifest mapping filename/doc_id to metadata."""
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    self._manifest_cache[item.get("filename", "")] = item
                    self._manifest_cache[item.get("doc_id", "")] = item
        except Exception as e:
            logger.warning("Failed to load manifest from %s: %s", self.manifest_path, e)

    def load_text_file(self, file_path: Path) -> str:
        """Load and return text content from a .txt or .md file."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Fallback to latin-1 if utf-8 fails
            logger.warning("UTF-8 decoding failed for %s, falling back to latin-1", file_path)
            return file_path.read_text(encoding="latin-1")

    def load_pdf_file(self, file_path: Path) -> str:
        """Extract text from a PDF file using pypdf."""
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        extracted_pages = []
        try:
            reader = pypdf.PdfReader(str(file_path))
            if len(reader.pages) == 0:
                raise ValueError(f"PDF file is empty (0 pages): {file_path}")
            
            for page_idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                extracted_pages.append(page_text)
                
            return "\n\n".join(extracted_pages)
        except Exception as e:
            logger.error("Error extracting text from PDF %s: %s", file_path, e)
            raise ValueError(f"Corrupted or unreadable PDF file: {file_path}") from e

    def load_document(self, file_path: Union[str, Path]) -> RawDocument:
        """Load a single document by its file path."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document file does not exist: {path}")

        ext = path.suffix.lower().lstrip(".")
        if ext in ["txt", "md"]:
            content = self.load_text_file(path)
        elif ext == "pdf":
            content = self.load_pdf_file(path)
        else:
            raise ValueError(f"Unsupported document format '.{ext}' for file {path.name}")

        if not content.strip():
            logger.warning("Loaded document is empty: %s", path.name)

        # Lookup manifest metadata if available
        manifest_meta = self._manifest_cache.get(path.name, {})
        doc_id = manifest_meta.get("doc_id", path.stem)
        title = manifest_meta.get("title", path.stem.replace("_", " "))
        category = manifest_meta.get("category", "GENERAL")

        words = content.split()
        return RawDocument(
            doc_id=doc_id,
            title=title,
            category=category,
            format=ext,
            source_file=str(path.as_posix()),
            raw_text=content,
            char_count=len(content),
            word_count=len(words),
            metadata={
                "doc_id": doc_id,
                "title": title,
                "category": category,
                "format": ext,
                "filename": path.name,
                "source_file": str(path.as_posix()),
                "organization": manifest_meta.get("organization", "Institut Teknologi Del"),
                "created_date": manifest_meta.get("created_date", "2026-09-01"),
                "compliance": manifest_meta.get("compliance", "UU PDP No. 27/2022")
            }
        )

    def load_directory(self, dir_path: Optional[Union[str, Path]] = None) -> List[RawDocument]:
        """Load all valid .txt, .md, and .pdf documents from the specified directory."""
        target_dir = Path(dir_path) if dir_path else self.corpus_dir
        if not target_dir or not target_dir.is_dir():
            raise NotADirectoryError(f"Directory not found: {target_dir}")

        documents: List[RawDocument] = []
        supported_exts = {".txt", ".md", ".pdf"}

        files = sorted([f for f in target_dir.iterdir() if f.is_file() and f.suffix.lower() in supported_exts])
        for f in files:
            try:
                doc = self.load_document(f)
                documents.append(doc)
            except Exception as e:
                logger.error("Failed to load file %s: %s", f.name, e)

        logger.info("Successfully loaded %d documents from %s", len(documents), target_dir)
        return documents
