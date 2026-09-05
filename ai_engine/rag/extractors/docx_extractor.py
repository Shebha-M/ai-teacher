"""DOCX extractor leveraging python-docx to extract paragraph hierarchy and headings."""
import io
import logging
from typing import List
import docx
from ai_engine.rag.extractors.base import BaseExtractor, ExtractedDocument, ExtractedSection

logger = logging.getLogger("ai_teacher.rag.docx")


class DOCXExtractor(BaseExtractor):
    """Extracts text and hierarchical headings from Word .docx documents."""

    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            sections: List[ExtractedSection] = []
            full_text_parts: List[str] = []

            current_heading: str = "Introduction"
            current_paragraphs: List[str] = []

            for p in doc.paragraphs:
                text = p.text.strip()
                if not text:
                    continue

                style_name = p.style.name if p.style else ""
                is_heading = "Heading" in style_name or "Title" in style_name

                if is_heading:
                    if current_paragraphs:
                        section_text = "\n".join(current_paragraphs)
                        sections.append(
                            ExtractedSection(
                                title=current_heading,
                                content=section_text,
                                metadata={"heading": current_heading},
                            )
                        )
                        full_text_parts.append(f"## {current_heading}\n{section_text}")
                        current_paragraphs = []
                    current_heading = text
                else:
                    current_paragraphs.append(text)

            # Flush remaining paragraphs
            if current_paragraphs:
                section_text = "\n".join(current_paragraphs)
                sections.append(
                    ExtractedSection(
                        title=current_heading,
                        content=section_text,
                        metadata={"heading": current_heading},
                    )
                )
                full_text_parts.append(f"## {current_heading}\n{section_text}")

            # Also extract table text if present
            for t_idx, table in enumerate(doc.tables):
                table_rows = []
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        table_rows.append(row_text)
                if table_rows:
                    t_text = "\n".join(table_rows)
                    sections.append(
                        ExtractedSection(
                            title=f"Table {t_idx + 1}",
                            content=t_text,
                            metadata={"type": "table"},
                        )
                    )
                    full_text_parts.append(f"### Table {t_idx + 1}\n{t_text}")

            doc_metadata = {}
            if doc.core_properties:
                doc_metadata = {
                    "title": doc.core_properties.title or None,
                    "author": doc.core_properties.author or None,
                }

            return ExtractedDocument(
                filename=filename,
                file_type="docx",
                total_pages_or_slides=max(1, len(sections)),
                full_text="\n\n".join(full_text_parts),
                sections=sections,
                metadata=doc_metadata,
            )
        except Exception as e:
            logger.error(f"Error extracting DOCX {filename}: {e}", exc_info=True)
            raise ValueError(f"Failed to process Word document '{filename}': {str(e)}") from e
