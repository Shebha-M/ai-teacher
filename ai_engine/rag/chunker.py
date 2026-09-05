"""Semantic chunking engine respecting structural boundaries (pages, slides, headings, paragraphs)."""
import re
import logging
from typing import List, Optional
from ai_engine.schemas.grounding import DocumentChunkSchema
from ai_engine.rag.extractors.base import ExtractedDocument, ExtractedSection
from ai_engine.rag.cleaner import TextCleaner

logger = logging.getLogger("ai_teacher.rag.chunker")


class SemanticChunker:
    """Chunks documents along semantic and natural structural boundaries."""

    def __init__(self, target_chunk_size: int = 500, chunk_overlap: int = 100, min_chunk_size: int = 100):
        self.target_chunk_size = target_chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def chunk_document(self, doc: ExtractedDocument, document_id: str) -> List[DocumentChunkSchema]:
        """Takes an ExtractedDocument and returns structured DocumentChunkSchema list."""
        all_chunks: List[DocumentChunkSchema] = []
        global_chunk_idx = 0

        for section in doc.sections:
            clean_content = TextCleaner.clean(section.content)
            if not clean_content:
                continue

            section_heading = section.title or section.metadata.get("heading") or "General"
            page_num = section.page_number
            slide_num = section.slide_number

            # Split by paragraph
            paragraphs = [p.strip() for p in clean_content.split("\n\n") if p.strip()]

            current_chunk_paragraphs: List[str] = []
            current_chunk_len = 0

            for para in paragraphs:
                para_len = len(para)

                # If single paragraph exceeds max target chunk size, split by sentences
                if para_len > (self.target_chunk_size * 1.5):
                    # Flush current accumulator first
                    if current_chunk_paragraphs:
                        chunk_text = "\n\n".join(current_chunk_paragraphs)
                        all_chunks.append(
                            self._create_chunk_schema(
                                document_id=document_id,
                                chunk_index=global_chunk_idx,
                                text=chunk_text,
                                page_number=page_num,
                                slide_number=slide_num,
                                heading=section_heading,
                                filename=doc.filename,
                            )
                        )
                        global_chunk_idx += 1
                        current_chunk_paragraphs = []
                        current_chunk_len = 0

                    # Split big paragraph into sentence chunks
                    sentence_chunks = self._chunk_large_paragraph(para)
                    for s_chunk in sentence_chunks:
                        all_chunks.append(
                            self._create_chunk_schema(
                                document_id=document_id,
                                chunk_index=global_chunk_idx,
                                text=s_chunk,
                                page_number=page_num,
                                slide_number=slide_num,
                                heading=section_heading,
                                filename=doc.filename,
                            )
                        )
                        global_chunk_idx += 1
                    continue

                if current_chunk_len + para_len > self.target_chunk_size and current_chunk_paragraphs:
                    chunk_text = "\n\n".join(current_chunk_paragraphs)
                    all_chunks.append(
                        self._create_chunk_schema(
                            document_id=document_id,
                            chunk_index=global_chunk_idx,
                            text=chunk_text,
                            page_number=page_num,
                            slide_number=slide_num,
                            heading=section_heading,
                            filename=doc.filename,
                        )
                    )
                    global_chunk_idx += 1

                    # Keep last paragraph for overlap if within limits
                    if len(current_chunk_paragraphs[-1]) <= self.chunk_overlap:
                        current_chunk_paragraphs = [current_chunk_paragraphs[-1], para]
                        current_chunk_len = len(current_chunk_paragraphs[0]) + len(para)
                    else:
                        current_chunk_paragraphs = [para]
                        current_chunk_len = len(para)
                else:
                    current_chunk_paragraphs.append(para)
                    current_chunk_len += para_len

            # Flush remaining in this section
            if current_chunk_paragraphs:
                chunk_text = "\n\n".join(current_chunk_paragraphs)
                # If tiny trailing piece and previous chunk exists in same section, could merge, else emit
                all_chunks.append(
                    self._create_chunk_schema(
                        document_id=document_id,
                        chunk_index=global_chunk_idx,
                        text=chunk_text,
                        page_number=page_num,
                        slide_number=slide_num,
                        heading=section_heading,
                        filename=doc.filename,
                    )
                )
                global_chunk_idx += 1

        return all_chunks

    def _chunk_large_paragraph(self, text: str) -> List[str]:
        """Breaks a long paragraph into sentence-delimited pieces respecting target size."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks: List[str] = []
        current: List[str] = []
        current_len = 0

        for s in sentences:
            s_clean = s.strip()
            if not s_clean:
                continue
            if current_len + len(s_clean) > self.target_chunk_size and current:
                chunks.append(" ".join(current))
                current = [s_clean]
                current_len = len(s_clean)
            else:
                current.append(s_clean)
                current_len += len(s_clean)

        if current:
            chunks.append(" ".join(current))
        return chunks

    def _create_chunk_schema(
        self,
        document_id: str,
        chunk_index: int,
        text: str,
        page_number: Optional[int],
        slide_number: Optional[int],
        heading: Optional[str],
        filename: str,
    ) -> DocumentChunkSchema:
        return DocumentChunkSchema(
            chunk_id=f"chk-{document_id[:8]}-{chunk_index}",
            document_id=document_id,
            chunk_index=chunk_index,
            text_content=text,
            page_number=page_number,
            slide_number=slide_number,
            heading=heading,
            chunk_metadata={
                "filename": filename,
                "length": len(text),
                "words": len(text.split()),
            },
        )
