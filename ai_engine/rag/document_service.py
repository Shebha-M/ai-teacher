"""Document ingestion and RAG service coordinating extraction, cleaning, chunking, and indexing."""
import os
import hashlib
import logging
from typing import List, Optional
from datetime import datetime, timezone

from ai_engine.schemas.grounding import (
    DocumentStatus,
    DocumentMetadataSchema,
    DocumentChunkSchema,
    GroundedContextSchema,
    KnowledgeMode,
)
from ai_engine.rag.extractors.factory import ExtractorFactory
from ai_engine.rag.chunker import SemanticChunker
from ai_engine.rag.vector_store import VectorStore, LocalVectorStore
from ai_engine.rag.retriever import HybridRetriever
from ai_engine.providers.base import EmbeddingProvider
from ai_engine.providers import get_teaching_provider

logger = logging.getLogger("ai_teacher.rag.service")


class DocumentIngestionService:
    """
    Coordinates the document intelligence pipeline:
    Validation -> Extraction -> Cleaning -> Chunking -> Embedding -> Indexing.
    """

    MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB security limit

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_provider: Optional[EmbeddingProvider] = None,
    ):
        self.vector_store = vector_store or LocalVectorStore()
        self.embedding_provider = embedding_provider or get_teaching_provider()
        self.chunker = SemanticChunker()
        self.retriever = HybridRetriever(
            vector_store=self.vector_store,
            embedding_provider=self.embedding_provider,
        )

    async def ingest_document(
        self,
        filename: str,
        file_bytes: bytes,
        document_id: Optional[str] = None,
    ) -> DocumentMetadataSchema:
        """
        Executes end-to-end ingestion pipeline for an uploaded educational document.
        """
        # 1. Validation: Size
        if len(file_bytes) > self.MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"File size exceeds maximum allowed limit of {self.MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
            )
        if len(file_bytes) == 0:
            raise ValueError("Uploaded file is empty (0 bytes).")

        # 2. Sanitize filename & calculate SHA-256
        clean_filename = os.path.basename(filename).replace(" ", "_")
        content_hash = hashlib.sha256(file_bytes).hexdigest()
        doc_id = document_id or f"doc-{content_hash[:8]}"
        ext = os.path.splitext(clean_filename.lower())[1].lstrip(".")

        logger.info(f"Ingesting document '{clean_filename}' ({len(file_bytes)} bytes) as {doc_id}")

        try:
            # 3. Extraction
            extractor = ExtractorFactory.get_extractor(clean_filename, file_bytes)
            extracted_doc = extractor.extract(file_bytes, clean_filename)

            if not extracted_doc.full_text.strip():
                raise ValueError("No readable text content could be extracted from this document.")

            # 4. Semantic Chunking
            chunks = self.chunker.chunk_document(extracted_doc, doc_id)

            if not chunks:
                raise ValueError("Semantic chunking produced zero valid chunks.")

            # 5. Embeddings
            chunk_texts = [c.text_content for c in chunks]
            embeddings = await self.embedding_provider.embed_batch(chunk_texts)

            # 6. Store in Vector Store
            await self.vector_store.add_chunks(chunks, embeddings)

            doc_meta = DocumentMetadataSchema(
                document_id=doc_id,
                filename=clean_filename,
                file_type=ext,
                file_size_bytes=len(file_bytes),
                page_count=extracted_doc.total_pages_or_slides,
                chunk_count=len(chunks),
                status=DocumentStatus.READY,
                content_hash=content_hash,
                created_at=datetime.now(timezone.utc).isoformat(),
                metadata=extracted_doc.metadata,
            )
            logger.info(f"Successfully indexed document {doc_id}: {len(chunks)} chunks, {extracted_doc.total_pages_or_slides} pages/slides")
            return doc_meta

        except Exception as e:
            logger.error(f"Failed to ingest document '{clean_filename}': {e}", exc_info=True)
            return DocumentMetadataSchema(
                document_id=doc_id,
                filename=clean_filename,
                file_type=ext,
                file_size_bytes=len(file_bytes),
                page_count=0,
                chunk_count=0,
                status=DocumentStatus.FAILED,
                error_message=str(e),
                content_hash=content_hash,
                created_at=datetime.now(timezone.utc).isoformat(),
            )

    async def retrieve_grounded_context(
        self,
        query: str,
        document_id: Optional[str] = None,
        top_k: int = 5,
        knowledge_mode: KnowledgeMode = KnowledgeMode.DOCUMENT,
    ) -> GroundedContextSchema:
        """Retrieves verified context to ground teaching decisions."""
        return await self.retriever.retrieve(
            query=query,
            document_id=document_id,
            top_k=top_k,
            knowledge_mode=knowledge_mode,
        )


# Global singleton ingestion service
_GLOBAL_DOCUMENT_SERVICE: Optional[DocumentIngestionService] = None


def get_document_service() -> DocumentIngestionService:
    global _GLOBAL_DOCUMENT_SERVICE
    if _GLOBAL_DOCUMENT_SERVICE is None:
        _GLOBAL_DOCUMENT_SERVICE = DocumentIngestionService()
    return _GLOBAL_DOCUMENT_SERVICE
