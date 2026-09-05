"""PDF extractor leveraging pypdf for page-by-page text and metadata extraction."""
import io
import logging
from typing import List
import pypdf
from ai_engine.rag.extractors.base import BaseExtractor, ExtractedDocument, ExtractedSection

logger = logging.getLogger("ai_teacher.rag.pdf")


class PDFExtractor(BaseExtractor):
    """Extracts text, page numbers, and metadata from PDF files."""

    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            total_pages = len(reader.pages)
            sections: List[ExtractedSection] = []
            full_text_parts: List[str] = []
            doc_metadata = {}

            if reader.metadata:
                doc_metadata = {
                    "title": str(reader.metadata.title) if reader.metadata.title else None,
                    "author": str(reader.metadata.author) if reader.metadata.author else None,
                    "subject": str(reader.metadata.subject) if reader.metadata.subject else None,
                }

            for idx, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text() or ""
                except Exception as e:
                    logger.warning(f"Failed to extract page {idx + 1} from {filename}: {e}")
                    page_text = ""

                if page_text.strip():
                    sections.append(
                        ExtractedSection(
                            title=f"Page {idx + 1}",
                            content=page_text,
                            page_number=idx + 1,
                            metadata={"page": idx + 1},
                        )
                    )
                    full_text_parts.append(page_text)

            return ExtractedDocument(
                filename=filename,
                file_type="pdf",
                total_pages_or_slides=total_pages,
                full_text="\n\n".join(full_text_parts),
                sections=sections,
                metadata=doc_metadata,
            )
        except Exception as e:
            logger.error(f"Error extracting PDF {filename}: {e}", exc_info=True)
            raise ValueError(f"Failed to process PDF document '{filename}': {str(e)}") from e
