# AI Teacher — Third-Party Services, Providers & Libraries

This document provides a comprehensive inventory of all third-party services, APIs, engines, and major libraries integrated into the AI Teacher platform.

For each component, this specification documents its purpose, location in the codebase, whether it is required or optional, credentials needed, cost expectations, and its fallback behavior.

---

## Quick Reference Matrix

| Service / Library | Role | Required? | Fallback When Unavailable | Credentials / Config | Cost |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **Google Gemini API** | Cloud LLM Intelligence | **Optional** | Deterministic Local Teaching Provider | `GEMINI_API_KEY` in `.env` | Free tier / Pay-per-token |
| **Microsoft Edge TTS** | Neural Speech Synthesis | **Optional** | Mock WAV Audio + Browser Web Speech API | None (Zero keys required) | Free |
| **Web Speech API** | Client-Side Speech Fallback | Built-in | Text-only subtitles and visual cues | None (Native browser API) | Free |
| **FastAPI + Uvicorn** | Backend REST Core | **Required** | None (Core runtime) | Python 3.10+ | Free (Open Source) |
| **SQLAlchemy + aiosqlite** | Async Relational Persistence | **Required** | None (Core runtime) | `DATABASE_URL` (defaults to local SQLite) | Free (Open Source) |
| **pypdf** | PDF Document Parser | **Required for PDF** | Graceful rejection with user message | None | Free (Open Source) |
| **python-docx** | Word Document Parser | **Required for DOCX** | Graceful rejection with user message | None | Free (Open Source) |
| **python-pptx** | PowerPoint Parser | **Required for PPTX** | Graceful rejection with user message | None | Free (Open Source) |
| **React 19 + Vite 6** | Interactive Web Studio | **Required** | None (Core UI) | Node.js 18+ | Free (Open Source) |
| **Pydantic V2** | Data Contracts & Validation | **Required** | None (Core runtime) | None | Free (Open Source) |

---

## Detailed Service Specifications

### 1. Google Gemini API (`google-generativeai`)

* **Purpose**: Provides generative AI capabilities for dynamic lesson planning, teaching narrative synthesis, question generation, and freeform answer evaluation.
* **Model Used**: `gemini-1.5-flash`
* **Codebase Location**: `ai_engine/providers/gemini_provider.py`
* **Requirement Level**: **Optional** (Non-blocking)
* **Configuration**:
  - Environment variable: `GEMINI_API_KEY` in root `.env` or system environment.
  - If omitted or empty, `GeminiLLMProvider.is_available()` returns `False`.
* **Fallback Behavior**:
  - When `GEMINI_API_KEY` is not present, or if network requests to Google time out or hit rate limits, the `SessionOrchestrator` automatically routes all requests to `DeterministicTeachingProvider` (`ai_engine/providers/mock_provider.py`).
  - The application operates with 100% functionality offline without throwing errors or halting the user session.
* **Cost / Tier**:
  - Operates comfortably within the free tier rate limits of Google AI Studio.

---

### 2. Microsoft Edge TTS (`edge-tts`)

* **Purpose**: Generates high-fidelity neural speech audio files (`.mp3`) across multiple languages (English, Hindi, Tamil, Telugu, Malayalam, Kannada) and extracts exact sub-second word-boundary and sentence-boundary timestamp cues for synchronized mouth articulation and live karaoke subtitles.
* **Codebase Location**: `ai_engine/providers/speech_provider.py` (`EdgeTTSProvider`)
* **Requirement Level**: **Optional** (Requires internet access; no API key needed)
* **Configuration**:
  - No API key or credit card required. Uses the open WebSocket protocol provided by Microsoft Edge.
* **Fallback Behavior**:
  - If the host machine is offline, or if the Edge TTS endpoint is unreachable, `EdgeTTSProvider` automatically catches the exception and falls back to `MockSpeechProvider`.
  - `MockSpeechProvider` generates a valid standard `.wav` audio file with computed syllable durations using Python's standard library `wave` module, ensuring audio playback and test suites succeed in CI/CD.
  - Concurrently, the frontend Video Studio falls back to the client-side **Web Speech API** for spoken audio if desired.
* **Cost**: Free.

---

### 3. Web Speech API (`window.speechSynthesis`)

* **Purpose**: Provides client-side, zero-latency text-to-speech directly in modern web browsers (Chrome, Edge, Firefox, Safari).
* **Codebase Location**: `frontend/src/App.jsx`
* **Requirement Level**: **Built-in Browser Feature**
* **Configuration**:
  - Enabled automatically in browser. Uses BCP-47 language codes (`en-US`, `hi-IN`, `ta-IN`, `te-IN`, `ml-IN`, `kn-IN`).
* **Fallback Behavior**:
  - If the browser does not support the Web Speech API (e.g. headless browser environments), the player still renders full synchronized text subtitles, visual diagrams, and avatar gestures.
* **Cost**: Free.

---

### 4. FastAPI & Uvicorn

* **Purpose**: High-performance asynchronous backend web server hosting all REST API endpoints for session orchestration, document ingestion, RAG search, speech synthesis, and avatar state evaluation.
* **Codebase Location**: `backend/main.py`, `backend/routes/`
* **Requirement Level**: **Required**
* **Configuration**:
  - `python -m uvicorn backend.main:app --reload --port 8000`
  - CORS middleware configured to allow communication with `http://localhost:5173` and `http://127.0.0.1:5173`.
* **Cost**: Free (Open Source, BSD-3-Clause).

---

### 5. SQLAlchemy 2.0 & aiosqlite (SQLite with WAL Mode)

* **Purpose**: Asynchronous Object Relational Mapping (ORM) and local relational persistence for all 12 core educational data models (students, profiles, sessions, lessons, sections, questions, responses, assessments, mastery records, documents, and chunks).
* **Codebase Location**: `backend/database/connection.py`, `backend/database/models.py`, `backend/database/crud.py`
* **Requirement Level**: **Required**
* **Configuration**:
  - Environment variable: `DATABASE_URL=sqlite+aiosqlite:///./ai_teacher.db`
  - Pragma configuration: Enables Write-Ahead Logging (`PRAGMA journal_mode=WAL`) and foreign key constraints (`PRAGMA foreign_keys=ON`) for high-concurrency read/write safety.
* **Cost**: Free (Open Source).

---

### 6. Document Parsing Libraries (`pypdf`, `python-docx`, `python-pptx`)

* **Purpose**: Extracts clean text, hierarchical section titles, page numbers, and slide markers from uploaded educational courseware for RAG grounding.
* **Codebase Location**:
  - `pypdf>=5.1.0`: `ai_engine/rag/extractors/pdf_extractor.py`
  - `python-docx>=1.1.2`: `ai_engine/rag/extractors/docx_extractor.py`
  - `python-pptx>=1.0.2`: `ai_engine/rag/extractors/pptx_extractor.py`
* **Requirement Level**: **Required for Respective File Formats**
* **Fallback Behavior**:
  - If an unsupported or corrupted file is uploaded, the `ExtractorFactory` safely rejects the upload with an HTTP 400 Bad Request error and an explanatory message, preventing server crashes.
* **Cost**: Free (Open Source).

---

### 7. React 19 & Vite 6

* **Purpose**: Reactive single-page application providing the student onboarding wizard, interactive cinema video studio, live avatar presenter, interactive SVG visualizer, checkpoint drawer, and learner progress dashboard.
* **Codebase Location**: `frontend/src/`
* **Requirement Level**: **Required for Web UI**
* **Configuration**:
  - Configured via `frontend/vite.config.js`.
  - Development server runs on port 5173 with proxy forwarding `/api` requests to backend port 8000.
* **Cost**: Free (Open Source, MIT).

---

### 8. Pydantic V2

* **Purpose**: Strictly enforces all input/output data schemas, JSON serialization/deserialization, and type safety between the frontend, backend, AI engine, and database.
* **Codebase Location**: `ai_engine/schemas/`
* **Requirement Level**: **Required**
* **Cost**: Free (Open Source, MIT).
