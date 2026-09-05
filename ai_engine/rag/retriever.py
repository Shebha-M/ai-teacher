"""Hybrid retriever combining semantic vector similarity and lexical matching with grounding contracts."""
import re
import logging
from typing import List, Optional, Set
from ai_engine.schemas.grounding import (
    KnowledgeMode,
    DocumentChunkSchema,
    RetrievedChunkSchema,
    CitationSchema,
    GroundedContextSchema,
)
from ai_engine.providers.base import EmbeddingProvider
from ai_engine.rag.vector_store import VectorStore

logger = logging.getLogger("ai_teacher.rag.retriever")


class HybridRetriever:
    """
    Retrieves educational context using hybrid vector-lexical ranking,
    formats citations, and enforces grounding sufficiency safeguards.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_provider: EmbeddingProvider,
        vector_weight: float = 0.7,
        sufficiency_threshold: float = 0.20,
    ):
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.vector_weight = vector_weight
        self.sufficiency_threshold = sufficiency_threshold

    async def retrieve(
        self,
        query: str,
        document_id: Optional[str] = None,
        top_k: int = 5,
        knowledge_mode: KnowledgeMode = KnowledgeMode.DOCUMENT,
    ) -> GroundedContextSchema:
        """
        Executes hybrid retrieval over indexed document chunks, returning a structured GroundedContextSchema.
        """
        if not query or not query.strip():
            return GroundedContextSchema(
                query=query,
                knowledge_mode=knowledge_mode,
                insufficient_grounding=True,
                document_relevance="LOW",
            )

        # 1. Compute query vector
        query_embedding = await self.embedding_provider.embed_text(query)

        # 2. Retrieve vector candidates (fetch 2x top_k to re-rank with lexical)
        vector_matches = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k * 2,
            document_id=document_id,
        )

        if not vector_matches:
            return GroundedContextSchema(
                query=query,
                knowledge_mode=knowledge_mode,
                insufficient_grounding=True,
                document_relevance="LOW",
                synthesized_context="",
            )

        # 3. Compute lexical scores and fuse hybrid ranking
        query_tokens = self._tokenize(query)
        retrieved_chunks: List[RetrievedChunkSchema] = []

        for chunk, v_sim in vector_matches:
            l_score = self._compute_lexical_score(query_tokens, chunk.text_content)
            hybrid_score = round(
                (self.vector_weight * v_sim) + ((1.0 - self.vector_weight) * l_score), 4
            )

            citation = self._format_citation_label(chunk)
            retrieved_chunks.append(
                RetrievedChunkSchema(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    filename=chunk.chunk_metadata.get("filename", "Source Document"),
                    chunk_index=chunk.chunk_index,
                    text_content=chunk.text_content,
                    page_number=chunk.page_number,
                    slide_number=chunk.slide_number,
                    heading=chunk.heading,
                    similarity_score=v_sim,
                    lexical_score=l_score,
                    hybrid_score=hybrid_score,
                    citation=citation,
                )
            )

        # Sort by hybrid score descending and trim to top_k
        retrieved_chunks.sort(key=lambda x: x.hybrid_score, reverse=True)
        top_chunks = retrieved_chunks[:top_k]

        # 4. Check Grounding Sufficiency & Relevance Tier
        max_score = top_chunks[0].hybrid_score if top_chunks else 0.0
        max_lexical = max((c.lexical_score for c in top_chunks), default=0.0)

        if max_score >= 0.35 or max_lexical >= 0.30:
            relevance = "HIGH"
            insufficient = False
        elif max_score >= self.sufficiency_threshold or max_lexical >= 0.15:
            relevance = "MEDIUM"
            insufficient = False
        else:
            relevance = "LOW"
            insufficient = True

        # 5. Extract citations and distinct source documents
        citations: List[CitationSchema] = []
        source_docs: Set[str] = set()

        for c in top_chunks:
            source_docs.add(c.document_id)
            location = "General"
            if c.slide_number:
                location = f"Slide {c.slide_number}"
            elif c.page_number:
                location = f"Page {c.page_number}"
            elif c.heading:
                location = c.heading

            excerpt = c.text_content[:150] + ("..." if len(c.text_content) > 150 else "")
            citations.append(
                CitationSchema(
                    source_id=c.chunk_id,
                    filename=c.filename,
                    location=location,
                    excerpt=excerpt,
                )
            )

        # 6. Synthesize context text for teaching prompt injection
        context_lines = []
        for idx, c in enumerate(top_chunks):
            context_lines.append(f"[{c.citation}]\n{c.text_content}")

        synthesized = "\n\n".join(context_lines)

        return GroundedContextSchema(
            query=query,
            knowledge_mode=knowledge_mode,
            retrieved_chunks=top_chunks,
            source_documents=list(source_docs),
            citations=citations,
            confidence_score=round(max_score, 4),
            insufficient_grounding=insufficient,
            document_relevance=relevance,
            synthesized_context=synthesized,
        )

    @classmethod
    def _tokenize(cls, text: str) -> Set[str]:
        return set(re.findall(r"\b\w{3,}\b", text.lower()))

    @classmethod
    def _compute_lexical_score(cls, query_tokens: Set[str], chunk_text: str) -> float:
        if not query_tokens:
            return 0.0
        chunk_tokens = set(re.findall(r"\b\w{3,}\b", chunk_text.lower()))
        intersection = query_tokens.intersection(chunk_tokens)
        return round(len(intersection) / len(query_tokens), 4)

    @classmethod
    def _format_citation_label(cls, chunk: DocumentChunkSchema) -> str:
        filename = chunk.chunk_metadata.get("filename", "Doc")
        if chunk.slide_number:
            return f"Source: {filename}, Slide {chunk.slide_number}"
        if chunk.page_number:
            return f"Source: {filename}, Page {chunk.page_number}"
        if chunk.heading:
            return f"Source: {filename}, {chunk.heading}"
        return f"Source: {filename}, Sec. {chunk.chunk_index + 1}"
