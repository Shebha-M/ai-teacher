# AI Teacher — System Architecture & Specification

## 1. Executive Summary & Challenge Context

**AI Teacher** is built for the **AI Innovation Hackathon 2026 – Build Real-World AI Solutions**.
Challenge: *"AI Teacher: Build a Human-Like AI Educator That Teaches Through Video."*

Traditional AI education systems act as passive chat interfaces:
`User Prompt → Generic LLM → Monolithic Text Response`

The AI Teacher replaces this paradigm with a stateful, pedagogical teaching loop:
$$\text{Understand} \longrightarrow \text{Plan} \longrightarrow \text{Explain} \longrightarrow \text{Demonstrate} \longrightarrow \text{Question} \longrightarrow \text{Evaluate} \longrightarrow \text{Adapt} \longrightarrow \text{Continue}$$

---

## 2. High-Level Architectural Layers

```
+-----------------------------------------------------------------------------------+
|                            FRONTEND WEB APPLICATION                               |
|   (React 19 + Vite + Vanilla CSS Glassmorphism + Audio/Visual Lesson Player)     |
|   - Learner Onboarding & Level Selection      - Checkpoint Question Console       |
|   - Topic Entry & Dynamic Curriculum Roadmap   - Diagnostic Misconception Alerts   |
|   - Section Explanations & Visual Directions   - Adaptive Progression Dashboard   |
+------------------------------------------^----------------------------------------+
                                           | REST & WebSockets
+------------------------------------------v----------------------------------------+
|                               BACKEND API SERVICE                                 |
|              (Python 3.13 + FastAPI + Async SQLAlchemy + SQLite WAL)              |
|   - Session Lifecycle Management               - Database Persistence (CRUD)       |
|   - API Validation & CORS Middleware           - State Audit Logs                  |
+------------------------------------------^----------------------------------------+
                                           | In-Process Async Calls
+------------------------------------------v----------------------------------------+
|                                AI TEACHING ENGINE                                 |
|                 (Modular Pedagogical Agents + Pydantic Contracts)                 |
|   +---------------------------------------------------------------------------+   |
|   | 1. Learner Profiler        2. Lesson Planner         3. Teaching Agent     |   |
|   | 4. Question Generator      5. Answer Evaluator       6. Misconception Det. |   |
|   | 7. Adaptation Engine       8. Session Orchestrator                         |   |
|   +---------------------------------------------------------------------------+   |
|   +---------------------------------------------------------------------------+   |
|   |                           PROVIDER ABSTRACTION LAYER                      |   |
|   |   - LLMProvider (DeterministicTeachingProvider, GeminiLLMProvider)        |   |
|   |   - EmbeddingProvider, SpeechProvider, AvatarProvider, VideoProvider      |   |
|   +---------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------+
```

---

## 3. The 8 Core AI Modules

| Module | Core Responsibility | Input Contract | Output Contract |
|---|---|---|---|
| **Learner Profiler** | Manages student knowledge state, style, strengths, weaknesses, and known misconceptions | Preferences & evaluation outcomes | `LearnerProfileSchema` |
| **Lesson Planner** | Synthesizes a structured curriculum whose section count, depth, and checkpoints adapt dynamically to available time (5m vs 20m vs 60m) | Topic, time limit, level | `LessonPlanSchema` |
| **Teaching Agent** | Translates planned sections into pedagogical explanations grounded in analogies, concrete examples, and visual directions | Section outline, learner style | `TeachingResponseSchema` |
| **Question Generator** | Generates conceptual, multiple-choice, or problem-solving questions calibrated to the section checkpoint | Section concept, difficulty | `QuestionSchema` |
| **Answer Evaluator** | Multi-dimensional scoring (0.0–1.0), extracting strengths, errors, and missing concepts | Student answer, question rubric | `EvaluationResultSchema` |
| **Misconception Detector** | Distinguishes between simple lack of knowledge vs. an active flawed mental model | Answer text, target concept | `MisconceptionReportSchema` |
| **Adaptation Engine** | Formulates pedagogical interventions (`CHANGE_ANALOGY`, `RE_EXPLAIN`, `SIMPLIFY`, `MOVE_TO_NEXT_CONCEPT`) | Evaluation & misconception data | `AdaptationDecisionSchema` |
| **Session Orchestrator** | Coordinates the full teaching cycle, maintains session state, and manages concept mastery | Session ID, student actions | `TeachingSessionStateSchema` |

---

## 4. Provider Abstraction Pattern

The platform strictly avoids vendor lock-in through abstract base classes (`LLMProvider`, `EmbeddingProvider`, `SpeechProvider`, `AvatarProvider`, `VideoProvider`).

```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate_structured(self, prompt: str, response_schema: Type[T], **kwargs) -> T:
        pass
```

- **`DeterministicTeachingProvider`**: High-fidelity local provider that generates structured lesson plans, questions, evaluations, and misconception reports offline without requiring paid API keys or internet access.
- **`GeminiLLMProvider`**: Live cloud provider interfacing with Google Gemini 1.5 Flash using structured JSON schemas, falling back gracefully to the deterministic provider on missing keys or network errors.

---

## 5. Database Architecture

The SQLite/SQLAlchemy schema supports 12 first-class educational entities:
1. `Student` & `StudentProfile`: Learner identity, preferences, known misconceptions, and strengths.
2. `LearningSession`: Session state, active topic, and section pointers.
3. `Lesson` & `LessonSection`: Time-adapted plans, objectives, and visual recommendations.
4. `Question` & `StudentResponse`: Checkpoint questions, options, rubrics, and student answers.
5. `Assessment`: Final cumulative evaluations and session feedback.
6. `LearningProgress` & `ConceptMastery`: Quantitative mastery scores (0.0–1.0) and status (`introduced`, `practicing`, `mastered`, `struggling`).
7. `Document` & `DocumentChunk`: Knowledge grounding and future RAG vector storage.

---

## 6. Document Intelligence & RAG Grounding Subsystem (Phase 3 Implemented)

The RAG subsystem enables grounded educational sessions using student-uploaded files (`PDF`, `DOCX`, `PPTX`, `TXT`, `MD`):

```
+---------------------------------------------------------------------------------+
|                    DOCUMENT INTELLIGENCE SUBSYSTEM (RAG)                        |
|                                                                                 |
|  [Uploaded File] -> [Extractor Factory] -> [Text Cleaner] -> [Semantic Chunker]  |
|                                                                                 |
|  [Semantic Chunks] -> [Deterministic / Gemini Embeddings] -> [LocalVectorStore] |
|                                                                                 |
|  [Retrieved Context & Citations] -> [Lesson Planner & Teaching Explanations]    |
+---------------------------------------------------------------------------------+
```

Key Components:
1. **Extractor Factory**: Validates formats and magic bytes (`%PDF`, `PK\x03\x04`), extracting hierarchical headings, page numbers, and slide indexes.
2. **Text Cleaner & Semantic Chunker**: Normalizes Unicode NFKC, cleans hyphens/line-breaks, and preserves paragraph/heading boundaries (~500 chars, 100 char overlap).
3. **LocalVectorStore & HybridRetriever**: Dense 256-dim embeddings fused with lexical keyword scoring ($0.7 \cdot S_{\text{vec}} + 0.3 \cdot S_{\text{lex}}$) and automatic `insufficient_grounding` confidence scoring (< 0.20 threshold).
4. **Teaching Grounding**: Injects verified source citations (`filename`, `location`, `excerpt`) directly into lesson plans, explanations, and questions.

---

## 7. AI Teaching Video & Subject-Aware Visual Subsystem (Phase 5 Implemented)

The media and visual explanation subsystem transforms structured teaching text into a synchronized interactive multimedia classroom:

```
+---------------------------------------------------------------------------------+
|               AI TEACHING VIDEO & SUBJECT-AWARE VISUAL SUBSYSTEM                |
|                                                                                 |
|  [Lesson Section] -> [Visual Planner] -> [4-Scene Video Plan: 1->2->3->4]       |
|                                                                                 |
|  [Subject Inference] -> [Tree SVG / Circuit Schematic / Code View / Math Card]   |
|                                                                                 |
|  [Web Speech API / Audio Stream] <---> [Animated Lip-Sync & Blinking Avatar]    |
|                                                                                 |
|  [Checkpoint Pause at Scene 4] -> [Misconception?] -> [Branch Scene 3-R]        |
+---------------------------------------------------------------------------------+
```

Key Components:
1. **Teaching Scene Plan**: Segments lessons into 4 atomic synchronized scenes: Introduction, Visual Explanation, Analogy Walkthrough, and Checkpoint Prompt.
2. **Subject-Aware Visual Planner**: Deterministically selects and renders specialized SVG diagrams (Binary Search Trees with traversal badges, DC circuits with Ohm's law, highlighted code blocks, mathematical derivation cards).
3. **Animated AI Teacher Avatar**: Dynamic mouth talking and eye-blinking keyframe animation reacting to emotion states (`WELCOMING`, `EXPLAINING`, `ENCOURAGING`, `THOUGHTFUL`, `CELEBRATING`).
4. **Interactive Studio Player**: Cinema timeline scrubber, playback speed selector (0.75x–1.5x), synchronized subtitles, and full-screen visual stage.
5. **Non-linear Checkpoint Interruption & Adaptive Branching**: Automatically pauses at Scene 4; if an answer displays a misconception, inserts and narrates **Remediation Scene (Scene 3-R)** with an alternative visual analogy.
6. **RAG Continuity**: Retains source document citation badges directly on the visual stage.

---

## 8. Multilingual Teaching & Natural Voice Subsystem (Phase 6 Implemented)

The Multilingual and Voice layer empowers the AI Teacher to explain complex concepts across languages with natural voice synthesis and contextual bilingual teaching:

```
+---------------------------------------------------------------------------------+
|               MULTILINGUAL TEACHING & NATURAL VOICE SUBSYSTEM                  |
|                                                                                 |
|  [Session State] -> [LanguageController] -> [Bilingual / Full / Mixed Mode]     |
|                                                                                 |
|  [Localized Narration] -> [Preserve Technical Terms: Tree, Root, Formula]       |
|                                                                                 |
|  [Speech Provider] -> [EdgeTTS: Real Neural MP3 + Word Cues] / [Mock Provider]  |
|                                                                                 |
|  [Mid-Lesson Language Switch] -> [Preserve Mastery, Section, & RAG Citations]  |
|                                                                                 |
|  [Synchronized Subtitles] <---> [Interactive Studio & Audio Streaming API]      |
+---------------------------------------------------------------------------------+
```

Key Components:
1. **Language Controller**: Supports English (`en`), Hindi (`hi`), Tamil (`ta`), Telugu (`te`), Malayalam (`ml`), and Kannada (`kn`) with script-aware localization and technical term preservation.
2. **Pedagogical Presentation Modes**: `bilingual` (native analogies with English technical terms), `full` (complete native vocabulary), and `mixed` (conversational code-switching).
3. **Context-Preserving Mid-Lesson Switch**: Seamlessly changes teaching language on an active session without resetting progress, topic, section index, question history, or RAG citations (`Binary_Trees_Lecture.md`).
4. **Speech Provider Abstraction**:
   - `EdgeTTSProvider`: Real Microsoft Edge neural TTS generating `.mp3` audio files and word-level `SubtitleSegment` boundaries.
   - `MockSpeechProvider`: Deterministic offline synthetic audio generator for CI and offline environments.
   - Client Web Speech API: Browser-side BCP-47 fallback.
5. **Multilingual Answer Normalization**: Translates native affirmations and number words before evaluation, maintaining high diagnostic accuracy.

---

## 9. Human-Like AI Teacher Avatar & Voice Synchronization Subsystem (Phase 7 Implemented)

The Avatar and Synchronization layer elevates the visual presenter into an audio-synchronized, emotion- and action-aware AI Educator Presenter:

```
+---------------------------------------------------------------------------------+
|          HUMAN-LIKE AI TEACHER AVATAR & VOICE SYNCHRONIZATION                   |
|                                                                                 |
|  [Teaching State + Scene] -> [AvatarController] -> [AvatarState Schema]         |
|                                                                                 |
|  [Audio Clock / Subtitle Cues] -> [Word-Level Visemes: REST, OPEN, HALF, NARROW]|
|                                                                                 |
|  [Teacher Actions: point_visual, ask_question] -> [Gestures: 👉 Point, 🤔 Think]|
|                                                                                 |
|  [Checkpoint Pause: Scene 4] -> [THINKING Pose] -> [Remediation: ENCOURAGE]     |
|                                                                                 |
|  [Accessibility] -> [Reduced Motion Toggle: Smooth Subdued Animation]          |
+---------------------------------------------------------------------------------+
```

Key Components:
1. **Avatar State Model (`AvatarState`)**: Encapsulates `emotion`, `speaking`, `mouth_state`, `eye_state`, `head_motion`, `gesture`, `speaking_progress`, `scene_action`, and `timing_mode`.
2. **Speech-Driven Viseme Progression**: Evaluates playback time against sub-second word boundaries (`word_cues`) and sentence boundaries (`subtitles`) to articulate natural lip movement (`REST` $\to$ `OPEN` $\to$ `HALF_OPEN` $\to$ `NARROW` $\to$ `REST`).
3. **Pedagogical Action & Directional Gestures**: Avatar physically points toward the visual stage (SVG Binary Tree, Circuit, Code) during visual explanation and traces elements in sync with narration.
4. **Checkpoint & Adaptive Remediation Postures**:
   - At Scene 4 checkpoints, speech halts and avatar enters a contemplative `THINK` pose.
   - When a student demonstrates a misconception, the avatar shifts to an `ENCOURAGING` posture with open palms before launching the alternative remediation analogy.
5. **Accessibility**: First-class `Reduced Motion` mode disabling intense transitions while preserving full educational utility.

---

## 10. Milestone Roadmap Status

- **Phase 1: Foundation & Pedagogy Contracts** [COMPLETED]
- **Phase 2: Core Teaching Intelligence Workflow** [COMPLETED]
- **Phase 3: Document Intelligence & RAG Knowledge Grounding** [COMPLETED]
- **Phase 4: Learner Memory, Concept Mastery & Adaptive Teaching 2.0** [COMPLETED]
- **Phase 5: AI Teaching Video & Subject-Aware Visual Explanation** [COMPLETED]
- **Phase 6: Multilingual Teaching & Natural Voice Engine** [COMPLETED]
- **Phase 7: Human-Like AI Teacher Avatar & Voice Synchronization** [COMPLETED]



