"""Comprehensive test suite for Phase 3: Document Intelligence and RAG Knowledge Grounding."""
import io
import pytest
import pypdf
import docx
import pptx

from ai_engine.schemas.grounding import KnowledgeMode, DocumentStatus
from ai_engine.schemas.learner import LearnerProfileSchema, LearnerLevel, TeachingStyle
from ai_engine.rag.extractors import (
    ExtractorFactory,
    TextExtractor,
    PDFExtractor,
    DOCXExtractor,
    PPTXExtractor,
)
from ai_engine.rag.cleaner import TextCleaner
from ai_engine.rag.chunker import SemanticChunker
from ai_engine.rag.vector_store import LocalVectorStore
from ai_engine.rag.retriever import HybridRetriever
from ai_engine.rag.document_service import DocumentIngestionService, get_document_service
from ai_engine.providers.mock_provider import DeterministicTeachingProvider
from ai_engine.modules.session_orchestrator import TeachingSessionOrchestrator
from ai_engine.modules.learner_profiler import LearnerProfiler


@pytest.fixture
def provider():
    return DeterministicTeachingProvider()


@pytest.fixture
def sample_binary_tree_text():
    return (
        "# Binary Search Tree Lecture Notes\n\n"
        "## Introduction to Binary Trees\n"
        "A Binary Tree is a hierarchical data structure where each node has at most two children, "
        "referred to as the left child and the right child. The topmost node is called the root node.\n\n"
        "## Invariant Rule\n"
        "In a Binary Search Tree (BST), for every node N, all values in its left subtree are strictly less than N, "
        "and all values in its right subtree are strictly greater than N.\n\n"
        "## Traversal Operations\n"
        "There are three depth-first traversal paradigms: In-order (Left, Root, Right), "
        "Pre-order (Root, Left, Right), and Post-order (Left, Right, Root). "
        "In-order traversal of a BST yields elements in sorted ascending order."
    )


def test_file_validation_unsupported_formats():
    """Verify that unsupported or legacy binary formats are rejected cleanly."""
    with pytest.raises(ValueError, match="Legacy Microsoft Word"):
        ExtractorFactory.get_extractor("syllabus.doc", b"fake_doc_bytes")

    with pytest.raises(ValueError, match="Legacy PowerPoint"):
        ExtractorFactory.get_extractor("slides.ppt", b"fake_ppt_bytes")

    with pytest.raises(ValueError, match="Unsupported file format"):
        ExtractorFactory.get_extractor("malicious.exe", b"fake_exe_bytes")


def test_text_extractor(sample_binary_tree_text):
    """Test text/markdown extraction preserving heading hierarchy."""
    extractor = TextExtractor()
    doc = extractor.extract(sample_binary_tree_text.encode("utf-8"), "tree_notes.md")

    assert doc.filename == "tree_notes.md"
    assert doc.file_type == "md"
    assert len(doc.sections) >= 3
    headings = [s.title for s in doc.sections]
    assert any("Binary Trees" in h for h in headings)
    assert any("Invariant Rule" in h for h in headings)


def test_pdf_extractor():
    """Test PDF text extraction with page tracking using pypdf."""
    # Synthesize an in-memory PDF
    writer = pypdf.PdfWriter()
    page1 = writer.add_blank_page(width=300, height=300)
    # Write some stream content
    buf = io.BytesIO()
    writer.write(buf)
    pdf_bytes = buf.getvalue()

    extractor = PDFExtractor()
    doc = extractor.extract(pdf_bytes, "test.pdf")
    assert doc.file_type == "pdf"
    assert doc.total_pages_or_slides >= 1


def test_docx_extractor():
    """Test Word DOCX extraction with paragraphs and headings."""
    doc_file = docx.Document()
    doc_file.add_heading("Chapter 1: Binary Trees", level=1)
    doc_file.add_paragraph("A tree where every node has at most two children.")
    doc_file.add_heading("Chapter 2: Tree Balance", level=1)
    doc_file.add_paragraph("AVL trees maintain a balance factor of -1, 0, or 1.")

    buf = io.BytesIO()
    doc_file.save(buf)
    docx_bytes = buf.getvalue()

    extractor = DOCXExtractor()
    extracted = extractor.extract(docx_bytes, "lecture.docx")
    assert extracted.file_type == "docx"
    assert len(extracted.sections) == 2
    assert "Chapter 1: Binary Trees" in extracted.sections[0].title
    assert "Chapter 2: Tree Balance" in extracted.sections[1].title


def test_pptx_extractor():
    """Test PowerPoint PPTX extraction with slide titles and shapes."""
    prs = pptx.Presentation()
    # Slide 1: Title slide
    blank_slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_slide_layout)
    tx_box = slide.shapes.add_textbox(100, 100, 300, 200)
    tf = tx_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Slide 1: Binary Tree Fundamentals\nA node has at most two children."

    buf = io.BytesIO()
    prs.save(buf)
    pptx_bytes = buf.getvalue()

    extractor = PPTXExtractor()
    extracted = extractor.extract(pptx_bytes, "trees.pptx")
    assert extracted.file_type == "pptx"
    assert extracted.total_pages_or_slides == 1
    assert len(extracted.sections) == 1
    assert extracted.sections[0].slide_number == 1
    assert "Binary Tree Fundamentals" in extracted.sections[0].content


def test_text_cleaner():
    """Verify whitespace normalization, hyphen repair, and line ending cleaning."""
    dirty_text = "Algo-\nrithm\r\n\r\n\r\nwith   lots   of    spaces   and\t\ttabs."
    cleaned = TextCleaner.clean(dirty_text)
    assert "Algorithm" in cleaned
    assert "   " not in cleaned
    assert "\r" not in cleaned


def test_semantic_chunker(sample_binary_tree_text):
    """Verify that chunking preserves headings, paragraph integrity, and metadata."""
    extractor = TextExtractor()
    doc = extractor.extract(sample_binary_tree_text.encode("utf-8"), "trees.md")

    chunker = SemanticChunker(target_chunk_size=300, chunk_overlap=50)
    chunks = chunker.chunk_document(doc, "doc-test-123")

    assert len(chunks) >= 3
    for chunk in chunks:
        assert chunk.document_id == "doc-test-123"
        assert len(chunk.text_content) > 0
        assert chunk.chunk_index >= 0
        assert chunk.heading is not None
        assert chunk.chunk_metadata["filename"] == "trees.md"


@pytest.mark.asyncio
async def test_deterministic_embedding_properties(provider):
    """Verify that deterministic embeddings produce normalized vectors with semantic distance."""
    emb1 = await provider.embed_text("Binary Search Tree root node left child right child")
    emb2 = await provider.embed_text("Binary Search Tree traversal left node")
    emb3 = await provider.embed_text("French cooking recipe chocolate soufflé baking")

    assert len(emb1) == 256
    # Unit norm check
    norm1 = sum(x * x for x in emb1) ** 0.5
    assert 0.99 <= norm1 <= 1.01

    # Dot product / cosine similarity
    sim_related = sum(a * b for a, b in zip(emb1, emb2))
    sim_unrelated = sum(a * b for a, b in zip(emb1, emb3))

    assert sim_related > sim_unrelated
    assert sim_related > 0.3
    assert sim_unrelated < 0.25


@pytest.mark.asyncio
async def test_local_vector_store_operations(provider, sample_binary_tree_text):
    """Test vector store chunk insertion, similarity search, and document deletion."""
    extractor = TextExtractor()
    doc = extractor.extract(sample_binary_tree_text.encode("utf-8"), "trees.md")
    chunker = SemanticChunker()
    chunks = chunker.chunk_document(doc, "doc-vec-test")

    embeddings = await provider.embed_batch([c.text_content for c in chunks])
    store = LocalVectorStore()
    await store.add_chunks(chunks, embeddings)

    # Search for BST traversal
    q_vec = await provider.embed_text("In-order traversal ascending order")
    results = await store.search(q_vec, top_k=2)

    assert len(results) > 0
    top_chunk, sim = results[0]
    assert sim > 0.2
    assert "doc-vec-test" == top_chunk.document_id

    # Test deletion
    await store.delete_document("doc-vec-test")
    empty_results = await store.search(q_vec, top_k=2)
    assert len(empty_results) == 0


@pytest.mark.asyncio
async def test_hybrid_retriever(provider, sample_binary_tree_text):
    """Test hybrid retrieval scoring, citations formatting, and sufficiency flag."""
    extractor = TextExtractor()
    doc = extractor.extract(sample_binary_tree_text.encode("utf-8"), "trees.md")
    chunker = SemanticChunker()
    chunks = chunker.chunk_document(doc, "doc-ret-test")
    embeddings = await provider.embed_batch([c.text_content for c in chunks])

    store = LocalVectorStore()
    await store.add_chunks(chunks, embeddings)

    retriever = HybridRetriever(vector_store=store, embedding_provider=provider)

    # 1. Relevant query
    grounded = await retriever.retrieve(
        query="What is the invariant rule in a binary search tree?",
        document_id="doc-ret-test",
        top_k=2,
    )

    assert grounded.insufficient_grounding is False
    assert len(grounded.retrieved_chunks) > 0
    assert len(grounded.citations) > 0
    assert "trees.md" in grounded.citations[0].filename
    assert grounded.confidence_score > 0.2
    assert "Invariant Rule" in grounded.synthesized_context

    # 2. Out-of-scope query triggers insufficient grounding flag
    empty_grounded = await retriever.retrieve(
        query="Quantum gravity string theory spacetime curvature",
        document_id="doc-ret-test",
        top_k=2,
    )
    assert empty_grounded.insufficient_grounding is True or empty_grounded.confidence_score < 0.2


@pytest.mark.asyncio
async def test_document_ingestion_service_end_to_end(sample_binary_tree_text):
    """Test full ingestion service: raw bytes -> chunks -> indexed vector store."""
    service = DocumentIngestionService()
    meta = await service.ingest_document(
        filename="lecture_trees.md",
        file_bytes=sample_binary_tree_text.encode("utf-8"),
    )

    assert meta.status == DocumentStatus.READY
    assert meta.chunk_count >= 3
    assert meta.page_count >= 1

    grounded = await service.retrieve_grounded_context(
        query="Binary search tree left child right child rule",
        document_id=meta.document_id,
    )
    assert not grounded.insufficient_grounding
    assert len(grounded.retrieved_chunks) > 0


@pytest.mark.asyncio
async def test_grounded_teaching_session_integration(sample_binary_tree_text):
    """
    Test end-to-end grounded teaching loop:
    1. Ingest document
    2. Initialize session with knowledge_mode=DOCUMENT and document_id
    3. Plan lesson (grounded in document)
    4. Teach section (cites document)
    5. Checkpoint question (cites source)
    """
    # 1. Ingest document
    service = get_document_service()
    doc_meta = await service.ingest_document(
        filename="bst_textbook.md",
        file_bytes=sample_binary_tree_text.encode("utf-8"),
    )
    assert doc_meta.status == DocumentStatus.READY

    # 2. Initialize Session
    orchestrator = TeachingSessionOrchestrator()
    profile = LearnerProfiler.create_profile(
        name="Jordan",
        educational_level=LearnerLevel.BEGINNER,
        available_learning_time=15,
        preferred_teaching_style=TeachingStyle.ANALOGY_DRIVEN,
    )

    session = orchestrator.initialize_session(
        topic="Binary Search Trees",
        learner_profile=profile,
        knowledge_mode=KnowledgeMode.DOCUMENT,
        document_id=doc_meta.document_id,
    )
    assert session.knowledge_mode == KnowledgeMode.DOCUMENT
    assert session.document_id == doc_meta.document_id

    # 3. Plan Lesson (retrieves grounded context)
    session = await orchestrator.plan_session(session)
    assert session.lesson_plan is not None
    assert session.grounded_context is not None
    assert "bst_textbook.md" in session.lesson_plan.lesson_title

    # 4. Teach current section (cites source document)
    teaching = await orchestrator.teach_current_section(session)
    assert "bst_textbook.md" in teaching.explanation

    # 5. Checkpoint question (references source)
    question = await orchestrator.get_checkpoint_question(session)
    assert any("bst_textbook.md" in h for h in question.hints)
