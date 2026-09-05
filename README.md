# 🎓 AI Teacher — Human-Like AI Educator

> **AI Innovation Hackathon 2026 – Build Real-World AI Solutions**  
> **Challenge:** *“AI Teacher: Build a Human-Like AI Educator That Teaches Through Video.”*

---

## 📌 Problem Statement

Most modern AI tutoring tools are merely thin wrappers around conversational chat completions (`User → LLM → Text`). They act as passive answer engines rather than proactive educators:
- They do not assess student mental models or diagnose *why* a student answered incorrectly.
- They lack pedagogical pacing, delivering walls of unstructured text.
- They do not dynamically restructure curriculum based on available learning time.
- They treat errors as binary `true/false` instead of cognitive misconceptions.

## 💡 Proposed Solution

**AI Teacher** is a human-like educational platform structured around the complete teaching cycle:

$$\textbf{Understand} \longrightarrow \textbf{Plan} \longrightarrow \textbf{Explain} \longrightarrow \textbf{Demonstrate} \longrightarrow \textbf{Question} \longrightarrow \textbf{Evaluate} \longrightarrow \textbf{Adapt} \longrightarrow \textbf{Continue}$$

### Key Capabilities (Phase 1, 2, & 3):
1. **Dynamic Time-Adapted Lesson Planning**: The curriculum structure itself transforms based on available time (5 min sprint vs 20 min curriculum vs 60 min masterclass).
2. **Document Intelligence & RAG Grounding (Phase 3)**: Ingests PDF, DOCX, PPTX, and TXT files, preserving headings, page/slide numbers, and paragraph boundaries to eliminate hallucinations.
3. **Hybrid Dense + Lexical Retrieval**: Combines 256-dim dense vector embeddings with lexical keyword matching ($0.7 \times \text{vec} + 0.3 \times \text{lex}$) and confidence scoring.
4. **Verified Source Attributions**: Generates explicit citation headers and excerpts in lesson plans, explanations, and questions.
5. **Cognitive Misconception Detection**: Differentiates between lack of knowledge and flawed mental models (e.g. inverse relation confusion in Ohm's Law or node overgeneralization in Binary Trees).
6. **Multi-Dimensional Answer Evaluation**: Evaluates answers with continuous scores (0.0 to 1.0), extracting strengths, missing concepts, and tailored rubric feedback.
7. **Pedagogical Adaptation Engine**: Formulates structured teaching interventions (`CHANGE_ANALOGY`, `RE_EXPLAIN`, `SIMPLIFY`, `MOVE_TO_NEXT_CONCEPT`) rather than raw text.
8. **Provider Abstraction**: Fully operable offline via a high-fidelity `DeterministicTeachingProvider` or connected to Google Gemini via `GeminiLLMProvider`.
9. **SQLAlchemy 2.0 Persistence**: Database tracking for 12 key educational entities with SQLite WAL-mode concurrency.

---

## 🏗️ High-Level Architecture

```
AI_TEACHER/
├── ai_engine/                    # Intelligence Layer (Pure Python, Provider Abstracted)
│   ├── schemas/                  # Pydantic V2 Contracts (Learner, Lesson, Teaching, Question, Eval, Misconception, Adapt)
│   ├── providers/                # LLMProvider, MockProvider, GeminiProvider
│   └── modules/                  # Profiler, Planner, TeachingAgent, Questioner, Evaluator, Detector, Adapter, Orchestrator
├── backend/                      # Application / API Service (FastAPI + Async SQLAlchemy)
│   ├── database/                 # Connection, SQLite WAL Engine, Models, and CRUD Operations
│   ├── routes/                   # RESTful Teaching Endpoints (/sessions, /plan, /explain, /question, /evaluate, /advance)
│   ├── config.py                 # Pydantic Settings
│   └── main.py                   # FastAPI Application Entrypoint
├── frontend/                     # Student-Facing Web Application (React 19 + Vite + Vanilla CSS)
│   ├── src/                      # App.jsx, index.css (Glassmorphic Dark Mode Design System)
│   └── package.json
├── docs/                         # In-Depth Architectural & Pedagogical Specifications
│   ├── architecture.md           # System Architecture, Schemas, & Data Flow
│   └── teaching_intelligence.md  # Cognitive Misconception Modeling & Adaptive Strategies
├── tests/                        # Comprehensive Pytest Suite (15 Unit & Integration Tests)
├── .env.example                  # Environment Template
└── requirements.txt              # Production Python Dependencies
```

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Python 3.11+ (Python 3.13 tested)
- Node.js 18+ (Node v22 tested) & npm

### 1. Backend & AI Engine Setup
```bash
# Clone the repository
cd AI_TEACHER

# Install Python dependencies
python -m pip install -r requirements.txt

# Run the Pytest test suite (15 tests passing)
python -m pytest

# Start the FastAPI backend server (port 8000)
uvicorn backend.main:app --reload --port 8000
```
- Interactive API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`
- AI Engine Status: `http://localhost:8000/api/v1/ai/health`

### 2. Frontend Web App Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite development server (port 5173)
npm run dev
```
- Open your browser to `http://localhost:5173`

---

## 🧪 Automated Testing

The intelligence layer, RAG subsystem, adaptive memory, visual studio, multilingual voice engine, and synchronized avatar presenter are thoroughly covered by automated unit and integration tests:
```bash
python -m pytest -v
```
All **50 test cases** pass cleanly with 100% success:
- `tests/test_lesson_planner.py`: Structural time adaptation (5m, 20m, 60m)
- `tests/test_question_generator.py`: Diagnostic checkpoint questions and rubrics
- `tests/test_answer_evaluator.py`: Correct, partial, and misconception scoring
- `tests/test_misconception_detector.py`: Cognitive flawed mental models vs lack of knowledge
- `tests/test_adaptation_engine.py`: Pedagogical interventions and safeguards
- `tests/test_session_orchestrator.py`: Complete teaching loop progression
- `tests/test_api.py`: FastAPI endpoints and async database persistence
- `tests/test_rag.py`: Multi-format document extractors (PDF, DOCX, PPTX, TXT), text cleaner, chunker, vector store, hybrid retriever, and grounding citations
- `tests/test_media_visuals.py`: Subject-aware visual planning (Tree, Circuit, Code, Equation), 4-scene video plans, RAG citation preservation, adaptive remediation branching (Scene 3-R), and media REST API endpoints
- `tests/test_multilingual_voice.py`: Multilingual resolution, voice catalog, technical terminology preservation, context-preserving mid-lesson language switch, native answer evaluation, and real TTS audio synthesis with subtitle timing cues
- `tests/test_avatar_sync.py`: Avatar state model, emotion profiles, action-to-gesture mapping, word-cue viseme timing, sentence-cue fallback, pause/resume snap to REST, checkpoint thinking pose, adaptive remediation posture, and reduced-motion accessibility

---

## 🗺️ Project Phases Roadmap

- [x] **Phase 1: Foundation & Architecture** (Tech stack, modular structure, database schema, health APIs)
- [x] **Phase 2: Core Teaching Intelligence** (Learner profiler, time-adaptive planner, teaching agent, question generator, answer evaluator, misconception detector, adaptation engine, frontend prototype)
- [x] **Phase 3: Document Intelligence & RAG Knowledge Grounding** (PDF, DOCX, PPTX, TXT extractors, semantic chunking, dense+lexical hybrid retriever, citation grounding)
- [x] **Phase 4: Learner Memory, Concept Mastery & Adaptive Teaching 2.0** (Cross-session learner profile, historical concept mastery tracking, learning curve pattern detection, adaptive difficulty)
- [x] **Phase 5: AI Teaching Video & Subject-Aware Visual Explanation** (4-scene video plans, subject-aware deterministic SVG trees, circuits, code & equations, animated lip-sync avatar, Web Speech API narration, interactive video studio player, non-linear checkpoint pause, and adaptive remediation branching)
- [x] **Phase 6: Multilingual Teaching & Natural Voice Engine** (Native scripts for Hindi, Tamil, Telugu, Malayalam, Kannada; Bilingual STEM mode preserving technical terms; Microsoft Edge Neural TTS audio assets; subtitle cue sync; context-preserving mid-lesson language switch)
- [x] **Phase 7: Human-Like AI Teacher Avatar & Voice Synchronization** (Stateful AvatarState, word-cue viseme progression REST->OPEN->HALF->NARROW, directional gestures pointing to visual stage, checkpoint thinking pose, remediation reassurance posture, modular React presenter components, and reduced-motion accessibility)

---

## 🎭 Phase 7 Human-Like AI Teacher Avatar Features
1. **Audio-Synchronized Speech Visemes**:
   - Driven directly by the real audio playback clock and word/sentence timing cues from Microsoft Edge Neural TTS.
   - Distinct mouth positions for vocal attack (`OPEN`), vocal body (`HALF_OPEN`), consonant release (`NARROW`), and inter-word silence (`REST`).
2. **Pedagogical Action & Directional Gestures**:
   - The avatar physically points toward the visual stage (`👉 Pointing to Visual`) during visual explanations and traces tree/circuit components.
   - Poses with hand-to-chin contemplation (`🤔 Posing Question`) when questioning the learner.
3. **Checkpoint & Adaptive Remediation Postures**:
   - At assessment checkpoints, speech halts and avatar enters a contemplative `THINKING` state.
   - If a student demonstrates a misconception, the avatar visibly shifts into an `ENCOURAGING` posture with open palms before guiding them through the alternative analogy.
4. **Multilingual Stability**:
   - Changing the language mid-lesson (English $\leftrightarrow$ Tamil $\leftrightarrow$ Hindi) preserves teacher identity ("Prof. Sophia"), topic, section index, concept mastery, and RAG citations while synchronizing visemes to the native audio stream.
5. **Accessibility (Reduced Motion)**:
   - Built-in `⚡ Motion: Reduced` toggle softens or disables head tilts, nodding, and eye-blinking keyframes for learners with motion sensitivities.



