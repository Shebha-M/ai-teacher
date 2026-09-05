"""Extractor factory routing raw documents to secure format-specific extractors."""
import os
import logging
from typing import Dict, Type
from ai_engine.rag.extractors.base import BaseExtractor
from ai_engine.rag.extractors.pdf_extractor import PDFExtractor
from ai_engine.rag.extractors.docx_extractor import DOCXExtractor
from ai_engine.rag.extractors.pptx_extractor import PPTXExtractor
from ai_engine.rag.extractors.text_extractor import TextExtractor

logger = logging.getLogger("ai_teacher.rag.factory")


class ExtractorFactory:
    """Routes uploaded files to validated extractors based on signature and extension."""

    SUPPORTED_EXTENSIONS = {
        ".pdf": PDFExtractor,
        ".docx": DOCXExtractor,
        ".pptx": PPTXExtractor,
        ".txt": TextExtractor,
        ".md": TextExtractor,
    }

    # Security signatures (magic bytes)
    MAGIC_SIGNATURES = {
        b"%PDF": ".pdf",
        b"PK\x03\x04": (".docx", ".pptx"),  # OOXML zip packages
    }

    @classmethod
    def get_extractor(cls, filename: str, file_bytes: bytes) -> BaseExtractor:
        """
        Validates the file signature and extension, returning the appropriate extractor.
        Raises ValueError if unsupported or corrupted.
        """
        ext = os.path.splitext(filename.lower())[1]

        # Check unsupported legacy formats explicitly to provide clean feedback
        if ext == ".doc":
            raise ValueError(
                "Legacy Microsoft Word (.doc) binary format is not supported. "
                "Please save or export as modern .docx format."
            )
        if ext == ".ppt":
            raise ValueError(
                "Legacy PowerPoint (.ppt) binary format is not supported. "
                "Please save or export as modern .pptx format."
            )

        if ext not in cls.SUPPORTED_EXTENSIONS:
            supported = ", ".join(cls.SUPPORTED_EXTENSIONS.keys())
            raise ValueError(f"Unsupported file format '{ext}'. Supported formats: {supported}")

        # Magic byte signature verification where applicable
        if ext == ".pdf":
            if not file_bytes.startswith(b"%PDF"):
                raise ValueError("Corrupted or invalid PDF file: missing %PDF signature.")

        elif ext in (".docx", ".pptx"):
            if not file_bytes.startswith(b"PK\x03\x04"):
                raise ValueError(f"Corrupted or invalid {ext.upper()} file: missing OOXML package header.")

        extractor_cls = cls.SUPPORTED_EXTENSIONS[ext]
        return extractor_cls()
