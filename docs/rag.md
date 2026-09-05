# Document Intelligence & RAG Knowledge Grounding Subsystem

## 1. Architectural Overview

The **AI Teacher Document Intelligence and RAG Grounding Subsystem** bridges the gap between static educational materials (textbooks, lecture slides, syllabus documents) and dynamic, adaptive teaching intelligence.

Instead of operating as an isolated Question-Answering chatbot that merely quotes raw excerpts, the RAG subsystem is deeply integrated into the pedagogical teaching loop:

```
Uploaded Material (PDF / DOCX / PPTX / TXT)
                  │
                  ▼
         Extractor Factory
   (Magic Bytes & Extension Check)
                  │
                  ▼
         Modular Extractor
  (Page / Slide / Heading Metadata)
                  │
                  ▼
        Text Cleaning & Normalization
  (NFKC, Line Reconstruction, Hyphen Repair)
                  │
                  ▼
         Semantic Chunker
 (Paragraph & Heading Boundaries, Overlap)
                  │
                  ▼
       Dense Vector Embedding
(256-Dim Normalized Semantic Projections)
                  │
                  ▼
         Local Vector Store
     (Cosine Similarity Index)
                  │
                  ▼
          Hybrid Retriever
(0.7 × Cosine Similarity + 0.3 × BM25 Lexical)
                  │
                  ▼
        Grounded Context Schema
 (Attributions, Location Tags, Sufficiency)
                  │
                  ▼
    Pedagogical Teaching Engines
(Lesson Planner → Teaching Agent → Question Generator)
```

---

## 2. Supported Formats & Extraction Libraries

| Format | Extension | Library | Extraction Strategy & Capabilities |
| :--- | :--- | :--- | :--- |
| **Portable Document Format** | `.pdf` | `pypdf>=5.1.0` | Iterates over `reader.pages`, preserves page numbers (`Page 1`, `Page 2`), extracts layout text, falls back gracefully on blank pages. Magic byte check: `%PDF`. |
| **Microsoft Word** | `.docx` | `python-docx>=1.1.2` | Extracts paragraphs and tables. Tracks hierarchical heading levels (`Heading 1`, `Heading 2`) to assign structural context to body content. Magic byte check: `PK\x03\x04`. |
| **PowerPoint Presentations** | `.pptx` | `python-pptx>=1.0.2` | Slide-by-slide extraction. Captures slide titles, text frames, shape text, and presenter notes (`Slide 1`, `Slide 2`). Magic byte check: `PK\x03\x04`. |
| **Markdown / Text** | `.md`, `.txt` | Native Python standard library | Hierarchical heading parser (`#`, `##`, `###`), preserving section titles and paragraph boundaries. |

> **Security & Validation Constraint**: Legacy binary formats (`.doc`, `.ppt`, `.xls`) and executables (`.exe`, `.bin`, `.sh`) are strictly blocked at ingestion time with explicit rejection errors to prevent arbitrary code execution or parser vulnerabilities.

---

## 3. Cleaning & Semantic Chunking Strategy

### Cleaning Pipeline (`TextCleaner`)
1. **Unicode Normalization**: Applies `unicodedata.normalize("NFKC")` to eliminate non-standard glyphs, ligatures, and encoding variations.
2. **Line-Break Reconstruction**: Detects hyphenated words broken across line wraps (e.g., `algo-\nrithm` → `algorithm`) and fuses them.
3. **Control Character Elimination**: Strips null bytes, non-printable characters, and carriage returns (`\r\n` → `\n`).
4. **Whitespace Regularization**: Collapses repeated spaces and tabs while preserving double newlines denoting semantic paragraph breaks.

### Semantic Chunking (`SemanticChunker`)
- **Boundary Preservation**: Rather than splitting blindly at fixed character offsets (which tears apart sentences and code blocks), chunks are built along **section**, **slide**, **heading**, and **paragraph** boundaries.
- **Target Size**: ~500 characters (~100 tokens), with an adaptive overlap of 100 characters to prevent loss of context across boundaries.
- **Metadata Enriched**: Each chunk retains:
  - `document_id`: Unique document reference.
  - `chunk_id`: Deterministic ID (`chk-{doc_id_short}-{index}`).
  - `page_number` / `slide_number`: Explicit page or slide anchor.
  - `heading`: Immediate parent section title (e.g., `AVL Balance Factor Definition`).
  - `filename`: Original uploaded filename.

---

## 4. Dense Vector Embeddings & Vector Storage

### Embedding Implementation
- Implements `EmbeddingProvider` contract with asynchronous batching (`embed_text`, `embed_batch`).
- **Deterministic 256-Dimensional Offline Embeddings**: Projects n-grams and token hashes into a dense unit sphere ($\|\mathbf{v}\| = 1.0$), ensuring reproducible cosine similarities offline without external API costs or rate-limiting.
- **Provider Interchangeability**: Can be hot-swapped to Google Gemini (`text-embedding-004` or `embedding-001`) by supplying `GEMINI_API_KEY`.

### Local Vector Store (`LocalVectorStore`)
- Stores normalized dense vectors with document metadata.
- Implements fast vector dot-product scoring:
  $$\text{CosineSimilarity}(\mathbf{u}, \mathbf{v}) = \sum_{i=1}^{d} u_i \cdot v_i$$
- Supports metadata filtering (e.g., scoping search to `document_id`).
- Supports persistence and idempotent re-indexing (`delete_document`).

---

## 5. Hybrid Retrieval & Grounding Safeguards

### Hybrid Scoring Engine
Retrieval quality is maximized by combining dense semantic similarity with exact lexical keyword matching:
$$\text{Score}_{\text{hybrid}} = 0.70 \cdot S_{\text{vector}} + 0.30 \cdot S_{\text{lexical}}$$

- $S_{\text{vector}}$: Cosine similarity between query embedding and chunk embedding.
- $S_{\text{lexical}}$: Token overlap ratio between query keywords and chunk text content.

### Anti-Hallucination & Sufficiency Safeguards
1. **Grounding Confidence Threshold**: If the top retrieved chunk score is below $0.20$, the system flags `insufficient_grounding: true`.
2. **Pedagogical Fallback**: When `insufficient_grounding` is true, the teacher explicitly admits that the uploaded document lacks specific information on the topic, falling back to foundational pedagogical analogies without inventing false source facts.
3. **Auditable Citations**: Each retrieved chunk is converted into a `CitationSchema`:
   - `filename`: Source file (e.g., `Binary_Trees_Lecture.md`).
   - `location`: Specific anchor (e.g., `Page 3`, `Slide 2`, or `AVL Balance Factor Definition`).
   - `excerpt`: Verbatim quotation confirming the source fact.

---

## 6. Teaching Intelligence Integration

Retrieved knowledge is directly injected into the core pedagogical agents:

1. **Lesson Planner**: Injects verified source sections into curriculum objectives, titling lessons as `Topic (Grounded in Filename)`.
2. **Teaching Agent**: Emits explicit citation headers:
   > 📖 **Directly from your uploaded course material (Binary_Trees_Lecture.md (AVL Balance Factor Definition)):**
   > *"In self-balancing binary search trees (AVL Trees), the Balance Factor of any node N is defined as the height of its left subtree minus the height of its right subtree..."*
3. **Question Generator**: Grounds multiple-choice and conceptual questions in document definitions, adding source review hints to assist struggling learners.

---

## 7. REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/documents/upload` | Multipart file upload (`.pdf`, `.docx`, `.pptx`, `.txt`). Extracts, chunks, embeds, indexes, and returns `DocumentMetadataSchema`. |
| `GET` | `/api/v1/documents` | Lists all uploaded documents with status, chunk counts, page counts, and sizes. |
| `GET` | `/api/v1/documents/{document_id}` | Retrieves detailed metadata and chunk status for a specific document. |
| `POST` | `/api/v1/documents/query` | Direct hybrid search query against an ingested document, returning `GroundedContextSchema`. |
| `POST` | `/api/v1/teaching/sessions` | Accepts `knowledge_mode: "topic" \| "document" \| "mixed"` and `document_id`. |
