"""Plain text and Markdown extractor for lecture notes and study guides."""
import re
from typing import List
from ai_engine.rag.extractors.base import BaseExtractor, ExtractedDocument, ExtractedSection


class TextExtractor(BaseExtractor):
    """Extracts content from plain text (.txt) and Markdown (.md) documents."""

    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        try:
            # Try utf-8 first, fallback to latin-1
            try:
                raw_text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                raw_text = file_bytes.decode("latin-1", errors="replace")

            sections: List[ExtractedSection] = []
            # Split by markdown headers if present, else by double newline paragraphs
            header_pattern = re.compile(r"^(#{1,3}\s+.+)$", re.MULTILINE)
            splits = header_pattern.split(raw_text)

            if len(splits) > 1:
                # First chunk before any header
                intro = splits[0].strip()
                if intro:
                    sections.append(ExtractedSection(title="Overview", content=intro, metadata={"heading": "Overview"}))

                for i in range(1, len(splits), 2):
                    header = splits[i].strip().lstrip("#").strip()
                    body = splits[i + 1].strip() if (i + 1) < len(splits) else ""
                    if body or header:
                        sections.append(ExtractedSection(title=header, content=body, metadata={"heading": header}))
            else:
                # Group by paragraph clusters
                paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
                for idx, p in enumerate(paragraphs):
                    sections.append(
                        ExtractedSection(
                            title=f"Section {idx + 1}",
                            content=p,
                            page_number=(idx // 3) + 1,
                            metadata={"section_index": idx + 1},
                        )
                    )

            total_pages = max(1, len(sections) // 3)
            return ExtractedDocument(
                filename=filename,
                file_type="txt" if filename.endswith(".txt") else "md",
                total_pages_or_slides=total_pages,
                full_text=raw_text,
                sections=sections,
                metadata={"format": "plain_text"},
            )
        except Exception as e:
            raise ValueError(f"Failed to process text document '{filename}': {str(e)}") from e
