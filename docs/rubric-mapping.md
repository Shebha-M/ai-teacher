# AI Teacher — Hackathon Rubric Mapping & Evidence

This document provides explicit, traceable mapping between the **AI Innovation Hackathon 2026** evaluation rubric and the actual code, tests, and architectural artifacts in this repository.

---

## Rubric Overview & Score Breakdown

| Evaluation Area | Weight | Implementation Status | Primary Code Evidence |
| :--- | :---: | :---: | :--- |
| **1. Human-Like Teaching & Adaptation** | 20 pts | **REAL IMPLEMENTATION** | `ai_engine/modules/`, `ai_engine/schemas/`, `backend/routes/teaching.py` |
| **2. AI/ML & LLM Architecture** | 15 pts | **REAL IMPLEMENTATION** | `ai_engine/providers/`, `ai_engine/modules/session_orchestrator.py` |
| **3. Document Intelligence & RAG** | 15 pts | **REAL IMPLEMENTATION** | `ai_engine/rag/`, `backend/routes/documents.py`, `tests/test_rag.py` |
| **4. AI Teaching Video & Visuals** | 15 pts | **REAL IMPLEMENTATION** | `ai_engine/modules/visual_planner.py`, `backend/routes/media.py`, `frontend/src/` |
| **5. Multilingual Teaching & Localization** | 10 pts | **REAL IMPLEMENTATION** | `ai_engine/modules/language_controller.py`, `backend/routes/media.py` |
| **6. Voice & Synchronized AI Avatar** | 10 pts | **REAL IMPLEMENTATION** | `ai_engine/providers/speech_provider.py`, `ai_engine/modules/avatar_controller.py` |
| **7. Innovation & System Architecture** | 5 pts | **REAL IMPLEMENTATION** | Multi-agent state machine, zero vendor lock-in, offline determinism |
| **8. User Experience & Studio Design** | 5 pts | **REAL IMPLEMENTATION** | `frontend/src/App.jsx`, `frontend/src/index.css` (Glassmorphic dark design) |
| **9. Engineering Quality & Documentation** | 5 pts | **REAL IMPLEMENTATION** | 67/67 tests passing, 22/22 E2E passing, comprehensive `docs/` suite |
| **Total** | **100 pts** | **VERIFIED OPERATIONAL** | Full verification verified via automated test suites & live studio |

---

## Detailed Category Evidence

### 1. Human-Like Teaching & Adaptation (20 Points)

*Requirement: The system must act as an active, empathetic tutor that diagnoses misconceptions, adapts pedagogical strategy, modifies pacing, and maintains cognitive continuity across the teaching cycle.*

* **The 8-Step Teaching Loop**:
  - Implemented in `ai_engine/modules/session_orchestrator.py`.
  - Coordinates `Understand → Plan → Explain → Demonstrate → Question → Evaluate → Adapt → Continue`.
  - Contrasts with standard chat completions (`User → LLM → Text`) by managing an explicit state machine (`TeachingSessionStateSchema` in `ai_engine/schemas/session.py`).
* **Time-Adaptive Lesson Planning**:
  - Code: `ai_engine/modules/lesson_planner.py` and `ai_engine/providers/mock_provider.py`.
  - 5–10 min: 1 focused essential sprint section.
  - 15–30 min: 3-section progressive mastery curriculum (Intuition $\to$ Mechanics $\to$ Applications).
  - 45–60+ min: 5-section masterclass exploring edge cases, internals, and system design.
* **Cognitive Misconception Detection**:
  - Code: `ai_engine/modules/misconception_detector.py`.
  - Distinguishes simple lack of knowledge from an active flawed mental model (e.g., confusing upper bound constraint with mandatory equality in Binary Trees).
  - Schema: `MisconceptionReportSchema` (`ai_engine/schemas/misconception.py`).
* **Multi-Dimensional Answer Evaluation**:
  - Code: `ai_engine/modules/answer_evaluator.py`.
  - Emits continuous score (0.0 to 1.0), identified strengths, missing components, and specific rubric feedback.
* **Pedagogical Interventions**:
  - Code: `ai_engine/modules/adaptation_engine.py`.
  - Supported interventions: `CHANGE_ANALOGY`, `RE_EXPLAIN`, `SIMPLIFY`, `GIVE_ANOTHER_EXAMPLE`, `MOVE_TO_NEXT_CONCEPT`, `INCREASE_DIFFICULTY`.
  - Safeguard: Students never advance past a section until active misconceptions are resolved.
* **Verification Evidence**:
  - `tests/test_adaptation_engine.py` (2 tests)
  - `tests/test_misconception_detector.py` (2 tests)
  - `tests/test_answer_evaluator.py` (3 tests)
  - `tests/test_lesson_planner.py` (8 tests)

---

### 2. AI/ML & LLM Architecture (15 Points)

*Requirement: Robust AI provider abstraction, structured JSON schema generation, graceful fallback mechanisms, and intelligent prompt/orchestration design.*

* **Honest Scope Notice**:
  - **This project does NOT train a foundation model from scratch.**
  - Instead, it implements application-level cognitive orchestration around existing foundation models and deterministic pedagogical modules.
* **Provider Abstraction Layer**:
  - Code: `ai_engine/providers/base.py`.
  - Abstract base classes: `LLMProvider`, `EmbeddingProvider`, `SpeechProvider`, `AvatarProvider`, `VideoProvider`.
* **Google Gemini Integration**:
  - Code: `ai_engine/providers/gemini_provider.py`.
  - Uses `gemini-1.5-flash` with structured JSON output enforcement via Pydantic V2 schemas (`generate_structured`).
* **Deterministic Local Teaching Provider**:
  - Code: `ai_engine/providers/mock_provider.py`.
  - 150 KB high-fidelity deterministic engine providing instant offline curriculum planning, teaching narrative synthesis, diagnostic questions, and misconception evaluations across multiple subjects without API keys or internet access.
* **Zero-Failure Fallback Guarantee**:
  - If `GEMINI_API_KEY` is omitted or cloud network requests fail, the system automatically falls back to the deterministic provider without interrupting the learner.
* **Verification Evidence**:
  - `tests/test_api.py` (Health and AI health verification)
  - `tests/test_final_integration.py` (`test_readiness_endpoint`)

---

### 3. Document Intelligence & RAG (15 Points)

*Requirement: Document ingestion, multi-format parsing, chunking, dense/lexical retrieval, grounding verification, and anti-hallucination safeguards.*

* **Multi-Format Extractor Factory**:
  - Code: `ai_engine/rag/extractors/factory.py`.
  - Validates magic bytes (`%PDF`, `PK\x03\x04`) and file extensions (`.pdf`, `.docx`, `.pptx`, `.txt`, `.md`).
  - Libraries: `pypdf>=5.1.0`, `python-docx>=1.1.2`, `python-pptx>=1.0.2`.
  - Rejects unsafe/executable binaries (`.exe`, `.bin`, `.sh`, `.doc`).
* **Text Cleaner & Semantic Chunker**:
  - Code: `ai_engine/rag/cleaner.py` and `ai_engine/rag/chunker.py`.
  - Applies NFKC Unicode normalization, line-wrap hyphen repair, and whitespace regularization.
  - Preserves section headings, slide boundaries, and paragraph breaks (~500 characters with 100 character overlap).
* **Vector Store & Hybrid Retrieval**:
  - Code: `ai_engine/rag/vector_store.py` and `ai_engine/rag/retriever.py`.
  - Normalized 256-dimensional semantic embeddings.
  - Hybrid scoring: $0.70 \times \text{CosineSimilarity} + 0.30 \times \text{LexicalOverlap}$.
  - SQLite WAL persistence with automatic on-demand memory store hydration (`_sync_from_sqlite`).
* **Domain-Agnostic Concept Extraction**:
  - Code: `ai_engine/rag/concept_extractor.py`.
  - Extracts authentic operational workflows, terms, and technical components from document chunks for curriculum planning rather than defaulting to generic templates.
* **Auditable Citations & Safeguards**:
  - Injects `CitationSchema` (`filename`, `location`, `excerpt`) directly into lesson sections, visual plans, and questions.
  - Flags `insufficient_grounding: true` when retrieval confidence falls below 0.20.
* **Verification Evidence**:
  - `tests/test_rag.py` (12 unit and integration tests)
  - `tests/test_document_grounded_curriculum.py` (9 comprehensive tests)
  - `scripts/verify_rag_e2e.py`

---

### 4. AI Teaching Video & Subject-Aware Visuals (15 Points)

*Requirement: Dynamic visual teaching, structured scene planning, subject-aware diagram selection, checkpoint interruption, and non-linear remediation branching.*

* **4-Scene Teaching Plan Structure**:
  - Code: `ai_engine/modules/visual_planner.py`.
  - Scene 1: `intro` (Welcoming framing).
  - Scene 2: `visual_explanation` (Domain diagram presentation).
  - Scene 3: `analogy_walkthrough` (Trace visual elements with real-world analogy).
  - Scene 4: `checkpoint_prompt` (Video pauses; teacher poses question).
* **Subject-Aware Visual Planner**:
  - Code: `ai_engine/topic_classifier.py` and `ai_engine/modules/visual_planner.py`.
  - Selects specialized visual representations based on academic discipline:
    - Data Structures: SVG Binary Search Tree with traversal highlights.
    - Recursion: Call stack frame sequence with activation records and base case badges.
    - Neural Networks: Input $\to$ Hidden $\to$ Output architecture with weighted edges and activation nodes.
    - Physics / Electronics: DC circuit schematic with Ohm's Law formula card.
    - Mathematics: Equation derivation card with variable breakdown.
    - Programming: Syntax-highlighted code viewer.
    - General / Document: Clean step-by-step workflow cards with source citations.
* **Adaptive Remediation Branching (Scene 3-R)**:
  - When an answer reveals a misconception, the orchestrator inserts an alternative visual and counter-analogy before returning to the checkpoint.
* **Interactive Frontend Player Studio**:
  - Code: `frontend/src/App.jsx`.
  - Cinema timeline scrubber, speed multiplier (0.75x–1.5x), live subtitles, interactive SVG diagram viewport.
* **Verification Evidence**:
  - `tests/test_media_visuals.py` (5 tests)
  - `scripts/verify_phase5_video.py`

---

### 5. Multilingual Teaching & Localization (10 Points)

*Requirement: Teaching in multiple languages, natural script rendering, bilingual STEM mode, and context-preserving language switching.*

* **Supported Languages**:
  - Code: `ai_engine/modules/language_controller.py`.
  - 6 languages fully supported with native script: English (`en`), Hindi (`hi`), Tamil (`ta`), Telugu (`te`), Malayalam (`ml`), Kannada (`kn`).
* **Bilingual STEM Mode**:
  - Explanations, analogies, and greetings are rendered in the learner's chosen language.
  - Core STEM technical terminology (`Binary Tree`, `Root Node`, `Left Child`, `O(log n)`) is preserved in English to reflect real-world university teaching conventions.
* **Context-Preserving Mid-Lesson Language Switch**:
  - Endpoint: `POST /api/v1/teaching/sessions/{id}/language`.
  - Switching language mid-lesson preserves:
    1. Active lesson topic and section index.
    2. Concept mastery matrix (0.0–1.0 scores).
    3. Past question attempts and diagnosed misconceptions.
    4. RAG document citations and source references.
* **Multilingual Student Answer Normalization**:
  - Normalizes native script answers (Tamil, Hindi, Telugu numbers and affirmative/negative particles) before rubric evaluation.
* **Verification Evidence**:
  - `tests/test_multilingual_voice.py` (8 tests)
  - `scripts/verify_phase6_multilingual_voice.py`

---

### 6. Voice & Synchronized AI Avatar (10 Points)

*Requirement: High-fidelity speech synthesis, sub-second timestamp cues, expressive avatar mouth and gesture synchronization, and accessibility controls.*

* **Neural Speech Engine (`EdgeTTSProvider`)**:
  - Code: `ai_engine/providers/speech_provider.py`.
  - Synthesizes natural voices using Microsoft Edge Neural TTS across all supported languages (e.g. `en-US-AriaNeural`, `ta-IN-PallaviNeural`, `hi-IN-SwaraNeural`).
  - Extracts sub-second word-boundary and sentence-boundary timestamp cues directly into structured `SubtitleSegment` records.
* **Speech-Synchronized Viseme Articulation**:
  - Code: `ai_engine/modules/avatar_controller.py`.
  - Mouth state smoothly transitions through speech visemes driven by the audio playback clock:
    - `0%–25%`: `OPEN` (vocal attack)
    - `25%–65%`: `HALF_OPEN` (vowel resonance)
    - `65%–90%`: `NARROW` (consonant closure)
    - `90%–100%`: `REST` (inter-word boundary)
* **Pedagogical Action Gestures**:
  - Directional pointing toward the visual stage during diagrams (`point_to_visual`).
  - Hand on chin during checkpoint reflection (`ask_question` $\to$ `THINK`).
  - Warm reassuring open palms during remediation (`ENCOURAGING`).
  - Celebratory pose upon mastery (`CELEBRATING`).
* **Accessibility (Reduced Motion)**:
  - Toggle in video studio softens or disables blinking, head tilts, and bouncing for motion-sensitive students.
* **Verification Evidence**:
  - `tests/test_avatar_sync.py` (10 tests)
  - `scripts/verify_phase7_avatar.py`

---

### 7. Innovation & System Architecture (5 Points)

*Requirement: Differentiating technical design, clean modular boundaries, decoupled persistence, and offline self-sufficiency.*

* **True Pedagogical Orchestration vs. Chatbot**:
  - State machine with dedicated modules for planning, questioning, evaluating, diagnosing, and adapting.
* **Offline-First Zero-Setup Determinism**:
  - The entire application runs 100% offline out-of-the-box using deterministic local intelligence, offline embeddings, and client-side speech/audio fallbacks. No API keys or credit cards required.
* **Clean Decoupled Data Model**:
  - 12 first-class educational entities persisted cleanly in SQLite WAL mode via SQLAlchemy 2.0 async engine.
* **Safe Neutral Fallbacks**:
  - General or unclassified topics deploy a domain-neutral teaching strategy with zero binary tree leaks.

---

### 8. User Experience & Studio Design (5 Points)

*Requirement: Intuitive onboarding, responsive design, visual hierarchy, polished dark mode aesthetics, and clear learning feedback.*

* **Design Aesthetic**:
  - Glassmorphic dark design system built with Vanilla CSS (`frontend/src/index.css`).
  - High visual hierarchy, custom color tokens, smooth transitions, and responsive flex/grid layouts.
* **Interactive Studio Features**:
  - Cinema video player with interactive scrub bar and speed controller.
  - Live animated avatar with real-time lip-sync and directional pointing.
  - Dynamic visual diagram stage with interactive tooltips and node highlights.
  - Embedded RAG source attribution badges with expandable excerpts.
  - Diagnostic checkpoint drawer with instant rubric feedback.
  - Comprehensive post-lesson dashboard featuring mastery percentages, revision recommendations, and next-topic roadmaps.
* **Production Build**:
  - Verified with Vite: `dist/index.html` (1.16 kB), `dist/assets/index.css` (30.81 kB), `dist/assets/index.js` (275.66 kB). Built in 1.82s with zero errors.

---

### 9. Engineering Quality & Documentation (5 Points)

*Requirement: Comprehensive automated test coverage, end-to-end verification, type safety, and clear documentation.*

* **Automated Tests**:
  - **67/67 unit and integration tests passing** (`python -m pytest`) across 13 test suites.
  - Zero test skips, zero warnings, 100% pass rate.
* **End-to-End Integration Verification**:
  - **22/22 golden demo steps passing** (`python scripts/verify_final_demo.py`).
* **Type Safety & Contracts**:
  - Strictly typed Pydantic V2 schemas across all 8 modules and REST routes.
* **Documentation Suite**:
  - Authoritative technical docs in `docs/` covering architecture, RAG, teaching intelligence, media, multilingual, avatar, third-party services, rubric mapping, and demo scripts.
