"""Pydantic contracts for Document Intelligence and RAG Knowledge Grounding."""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class KnowledgeMode(str, Enum):
    TOPIC = "topic"          # Curriculum generated from general knowledge base
    DOCUMENT = "document"    # Curriculum strictly grounded in uploaded document
    MIXED = "mixed"          # Document grounded with general curriculum enrichment


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class DocumentMetadataSchema(BaseModel):
    document_id: str = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Sanitized original filename")
    file_type: str = Field(..., description="MIME/extension, e.g. 'pdf', 'docx', 'pptx', 'txt'")
    file_size_bytes: int = Field(0, description="Size in bytes")
    page_count: int = Field(0, description="Total pages or slides")
    chunk_count: int = Field(0, description="Total semantic chunks produced")
    status: DocumentStatus = Field(DocumentStatus.UPLOADED, description="Ingestion processing status")
    error_message: Optional[str] = Field(None, description="Diagnostic error if processing failed")
    content_hash: str = Field(..., description="SHA-256 hash of file contents")
    created_at: Optional[str] = Field(None, description="ISO timestamp of upload")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extracted document properties")


class DocumentChunkSchema(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk ID e.g. 'chk-doc1-0'")
    document_id: str = Field(..., description="Parent document ID")
    chunk_index: int = Field(..., description="0-indexed position in document")
    text_content: str = Field(..., description="Cleaned chunk text content")
    page_number: Optional[int] = Field(None, description="Source page number if PDF/document")
    slide_number: Optional[int] = Field(None, description="Source slide number if PPTX")
    heading: Optional[str] = Field(None, description="Associated section heading or title")
    chunk_metadata: Dict[str, Any] = Field(default_factory=dict, description="Hierarchical context")
    embedding: Optional[List[float]] = Field(None, description="Embedding vector representation")


class CitationSchema(BaseModel):
    source_id: str = Field(..., description="Document or chunk reference ID")
    filename: str = Field(..., description="Display filename")
    location: str = Field(..., description="Location label, e.g. 'Page 3', 'Slide 4', 'Sec. 2'")
    excerpt: str = Field(..., description="Brief relevant quote or supporting excerpt")


class RetrievedChunkSchema(BaseModel):
    chunk_id: str = Field(..., description="Chunk ID")
    document_id: str = Field(..., description="Document ID")
    filename: str = Field(..., description="Source filename")
    chunk_index: int = Field(..., description="Position index")
    text_content: str = Field(..., description="Chunk text content")
    page_number: Optional[int] = None
    slide_number: Optional[int] = None
    heading: Optional[str] = None
    similarity_score: float = Field(0.0, description="Vector cosine similarity (0.0 - 1.0)")
    lexical_score: float = Field(0.0, description="BM25/token match score (0.0 - 1.0)")
    hybrid_score: float = Field(..., description="Fused hybrid ranking score")
    citation: str = Field(..., description="Formatted citation string")


class GroundedContextSchema(BaseModel):
    query: str = Field(..., description="Target query or lesson topic")
    knowledge_mode: KnowledgeMode = Field(KnowledgeMode.TOPIC, description="Grounding modality")
    retrieved_chunks: List[RetrievedChunkSchema] = Field(
        default_factory=list, description="Ranked retrieved evidence chunks"
    )
    source_documents: List[str] = Field(
        default_factory=list, description="Unique source document IDs used"
    )
    citations: List[CitationSchema] = Field(
        default_factory=list, description="Formatted citations for frontend attribution"
    )
    confidence_score: float = Field(
        0.0, ge=0.0, le=1.0, description="Aggregated grounding confidence"
    )
    insufficient_grounding: bool = Field(
        False, description="True if retrieved content lacks sufficient relevant evidence"
    )
    document_relevance: str = Field(
        "HIGH", description="Document relevance tier: 'HIGH' | 'MEDIUM' | 'LOW'"
    )
    synthesized_context: str = Field(
        "", description="Clean concatenated context block ready for pedagogical prompt injection"
    )
