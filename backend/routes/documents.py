"""Document Intelligence and RAG REST API endpoints."""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.database import crud
from ai_engine.schemas.grounding import (
    DocumentMetadataSchema,
    DocumentStatus,
    GroundedContextSchema,
    KnowledgeMode,
)
from ai_engine.rag.document_service import get_document_service

logger = logging.getLogger("ai_teacher.routes.documents")

router = APIRouter(prefix="/documents", tags=["Documents & RAG"])


class DocumentQueryRequest(BaseModel):
    query: str = Field(..., description="Query to search against indexed documents")
    document_id: Optional[str] = Field(None, description="Optional document ID to scope search")
    top_k: int = Field(5, ge=1, le=20, description="Maximum chunks to retrieve")
    knowledge_mode: KnowledgeMode = Field(KnowledgeMode.DOCUMENT, description="Retrieval mode")


@router.post(
    "/upload",
    response_model=DocumentMetadataSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest an educational document (PDF, DOCX, PPTX, TXT)",
)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Securely uploads, validates, extracts, chunks, embeds, and indexes an educational document.
    Supported formats: .pdf, .docx, .pptx, .txt, .md.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing from upload.")

    try:
        file_bytes = await file.read()
        doc_service = get_document_service()
        doc_meta = await doc_service.ingest_document(
            filename=file.filename,
            file_bytes=file_bytes,
        )

        # Persist to database
        await crud.save_document(db, doc_meta)
        if doc_meta.status == DocumentStatus.READY:
            chunks = await doc_service.vector_store.get_document_chunks(doc_meta.document_id)
            await crud.save_document_chunks(db, doc_meta.document_id, chunks)

        return doc_meta

    except ValueError as ve:
        logger.warning(f"Validation failure for upload '{file.filename}': {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error during upload of '{file.filename}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to process educational document: {str(e)}"
        )


@router.get(
    "",
    response_model=List[DocumentMetadataSchema],
    summary="List all uploaded documents and their processing status",
)
async def list_documents(db: AsyncSession = Depends(get_db)):
    """Retrieve all uploaded documents, processing status, and page/chunk counts."""
    docs = await crud.list_documents(db)
    return [
        DocumentMetadataSchema(
            document_id=d.id,
            filename=d.filename,
            file_type=d.file_type,
            file_size_bytes=d.file_size_bytes,
            page_count=d.page_count,
            chunk_count=d.chunk_count,
            status=DocumentStatus(d.status) if d.status in DocumentStatus.__members__.values() else DocumentStatus.READY,
            error_message=d.error_message,
            content_hash=d.content_hash,
            created_at=d.created_at.isoformat() if d.created_at else None,
            metadata=d.document_metadata or {},
        )
        for d in docs
    ]


@router.get(
    "/{document_id}",
    response_model=DocumentMetadataSchema,
    summary="Get details and status for a specific document",
)
async def get_document_details(document_id: str, db: AsyncSession = Depends(get_db)):
    doc = await crud.get_document(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=404, detail=f"Document '{document_id}' not found."
        )

    return DocumentMetadataSchema(
        document_id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size_bytes=doc.file_size_bytes,
        page_count=doc.page_count,
        chunk_count=doc.chunk_count,
        status=DocumentStatus(doc.status) if doc.status in DocumentStatus.__members__.values() else DocumentStatus.READY,
        error_message=doc.error_message,
        content_hash=doc.content_hash,
        created_at=doc.created_at.isoformat() if doc.created_at else None,
        metadata=doc.document_metadata or {},
    )


@router.post(
    "/query",
    response_model=GroundedContextSchema,
    summary="Search and retrieve relevant context chunks with hybrid scoring and citations",
)
async def query_documents(request: DocumentQueryRequest):
    """
    Performs hybrid vector-lexical retrieval and packages ranked evidence chunks with source citations.
    """
    doc_service = get_document_service()
    grounded = await doc_service.retrieve_grounded_context(
        query=request.query,
        document_id=request.document_id,
        top_k=request.top_k,
        knowledge_mode=request.knowledge_mode,
    )
    return grounded
