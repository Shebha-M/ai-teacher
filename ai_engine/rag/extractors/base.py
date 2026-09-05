"""Base interface and data contracts for document extraction."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ExtractedSection:
    """Represents an atomic structural unit (page, slide, or heading-section)."""
    title: Optional[str] = None
    content: str = ""
    page_number: Optional[int] = None
    slide_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedDocument:
    """Complete structured output from an extraction operation."""
    filename: str
    file_type: str
    total_pages_or_slides: int
    full_text: str
    sections: List[ExtractedSection]
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseExtractor(ABC):
    """Abstract base class for all file format extractors."""

    @abstractmethod
    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        """Extract structured content and metadata from raw bytes."""
        pass
