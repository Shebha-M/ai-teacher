"""Document extractors package."""
from ai_engine.rag.extractors.base import BaseExtractor, ExtractedDocument, ExtractedSection
from ai_engine.rag.extractors.pdf_extractor import PDFExtractor
from ai_engine.rag.extractors.docx_extractor import DOCXExtractor
from ai_engine.rag.extractors.pptx_extractor import PPTXExtractor
from ai_engine.rag.extractors.text_extractor import TextExtractor
from ai_engine.rag.extractors.factory import ExtractorFactory

__all__ = [
    "BaseExtractor",
    "ExtractedDocument",
    "ExtractedSection",
    "PDFExtractor",
    "DOCXExtractor",
    "PPTXExtractor",
    "TextExtractor",
    "ExtractorFactory",
]
