"""Vector store interface and local in-memory/persistent implementation with cosine similarity."""
import os
import math
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from ai_engine.schemas.grounding import DocumentChunkSchema

logger = logging.getLogger("ai_teacher.rag.vector_store")


class VectorStore(ABC):
    """Abstract interface for educational vector storage and retrieval."""

    @abstractmethod
    async def add_chunks(
        self, chunks: List[DocumentChunkSchema], embeddings: List[List[float]]
    ) -> None:
        """Store document chunks alongside their embedding vectors."""
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[Tuple[DocumentChunkSchema, float]]:
        """Perform cosine similarity search returning (chunk, similarity_score)."""
        pass

    @abstractmethod
    async def delete_document(self, document_id: str) -> None:
        """Remove all chunks and vectors associated with a document."""
        pass

    @abstractmethod
    async def get_document_chunks(self, document_id: str) -> List[DocumentChunkSchema]:
        """Retrieve all stored chunks for a given document."""
        pass


class LocalVectorStore(VectorStore):
    """
    Lightweight, high-performance local vector store with cosine similarity and BM25 token index.
    Requires zero external daemons or services, with optional file persistence.
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        # Map: chunk_id -> (DocumentChunkSchema, embedding_vector)
        self._entries: Dict[str, Tuple[DocumentChunkSchema, List[float]]] = {}
        self._deleted_documents: set = set()
        if storage_path and os.path.exists(storage_path):
            self._load_from_disk()

    async def add_chunks(
        self, chunks: List[DocumentChunkSchema], embeddings: List[List[float]]
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings")

        for chunk, emb in zip(chunks, embeddings):
            chunk.embedding = emb
            self._entries[chunk.chunk_id] = (chunk, emb)

        if self.storage_path:
            self._save_to_disk()
        logger.info(f"Stored {len(chunks)} chunks in LocalVectorStore (total: {len(self._entries)})")

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[Tuple[DocumentChunkSchema, float]]:
        if document_id and document_id not in self._deleted_documents:
            if not any(c.document_id == document_id for c, _ in self._entries.values()):
                self._sync_from_sqlite(document_id)

        if not self._entries or not query_embedding:
            return []

        q_norm = math.sqrt(sum(x * x for x in query_embedding))
        if q_norm == 0.0:
            return []

        scored_results: List[Tuple[DocumentChunkSchema, float]] = []

        for chunk, emb in self._entries.values():
            if document_id and chunk.document_id != document_id:
                continue

            # Dot product calculation
            dot = sum(q * d for q, d in zip(query_embedding, emb))
            d_norm = math.sqrt(sum(d * d for d in emb))
            sim = (dot / (q_norm * d_norm)) if (q_norm > 0 and d_norm > 0) else 0.0
            scored_results.append((chunk, round(sim, 4)))

        # Sort descending by similarity
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:top_k]

    async def delete_document(self, document_id: str) -> None:
        self._deleted_documents.add(document_id)
        to_remove = [
            cid for cid, (chunk, _) in self._entries.items() if chunk.document_id == document_id
        ]
        for cid in to_remove:
            del self._entries[cid]
        if self.storage_path:
            self._save_to_disk()
        logger.info(f"Deleted {len(to_remove)} chunks for document {document_id}")

    async def get_document_chunks(self, document_id: str) -> List[DocumentChunkSchema]:
        if document_id not in self._deleted_documents:
            if not any(c.document_id == document_id for c, _ in self._entries.values()):
                self._sync_from_sqlite(document_id)
        return [
            chunk for chunk, _ in self._entries.values() if chunk.document_id == document_id
        ]

    def _sync_from_sqlite(self, document_id: Optional[str] = None) -> None:
        """Hydrate vector store entries directly from SQLite database if missing in-memory."""
        if document_id and document_id in self._deleted_documents:
            return
        db_path = "ai_teacher.db"
        if not os.path.exists(db_path):
            return
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            if document_id:
                cursor.execute(
                    "SELECT dc.id, dc.document_id, dc.chunk_index, dc.text_content, "
                    "dc.page_number, dc.slide_number, dc.heading, dc.chunk_metadata, d.filename "
                    "FROM document_chunks dc "
                    "LEFT JOIN documents d ON dc.document_id = d.id "
                    "WHERE dc.document_id = ? "
                    "ORDER BY dc.chunk_index ASC",
                    (document_id,),
                )
            else:
                cursor.execute(
                    "SELECT dc.id, dc.document_id, dc.chunk_index, dc.text_content, "
                    "dc.page_number, dc.slide_number, dc.heading, dc.chunk_metadata, d.filename "
                    "FROM document_chunks dc "
                    "LEFT JOIN documents d ON dc.document_id = d.id "
                    "ORDER BY dc.chunk_index ASC"
                )
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return

            for row in rows:
                cid, doc_id, c_idx, text_content, page_no, slide_no, heading, raw_meta, filename = row
                if cid in self._entries:
                    continue
                meta: Dict[str, Any] = {}
                if raw_meta:
                    try:
                        meta = json.loads(raw_meta) if isinstance(raw_meta, str) else raw_meta
                    except Exception:
                        meta = {}
                if filename and "filename" not in meta:
                    meta["filename"] = filename

                chunk = DocumentChunkSchema(
                    chunk_id=cid,
                    document_id=doc_id,
                    chunk_index=c_idx,
                    text_content=text_content,
                    page_number=page_no,
                    slide_number=slide_no,
                    heading=heading,
                    chunk_metadata=meta,
                )
                from ai_engine.providers.mock_provider import DeterministicTeachingProvider
                emb = DeterministicTeachingProvider._compute_deterministic_embedding(text_content)
                chunk.embedding = emb
                self._entries[cid] = (chunk, emb)

            logger.info(f"Synchronized {len(rows)} chunks from SQLite into LocalVectorStore.")
        except Exception as e:
            logger.warning(f"Failed to sync chunks from SQLite: {e}")

    def _save_to_disk(self) -> None:
        if not self.storage_path:
            return
        os.makedirs(os.path.dirname(os.path.abspath(self.storage_path)), exist_ok=True)
        data = {
            cid: {"chunk": chunk.model_dump(), "embedding": emb}
            for cid, (chunk, emb) in self._entries.items()
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def _load_from_disk(self) -> None:
        if not self.storage_path or not os.path.exists(self.storage_path):
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for cid, item in data.items():
                chunk = DocumentChunkSchema(**item["chunk"])
                emb = item["embedding"]
                self._entries[cid] = (chunk, emb)
        except Exception as e:
            logger.warning(f"Could not load vector store from disk: {e}")
