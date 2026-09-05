# AI Teacher — Hackathon Live Demo & Judging Guide

This guide provides a structured, step-by-step presentation script and live demonstration walkthrough for the AI Teacher platform.

---

## 1. Demo Objective

**Goal**: In **5 to 7 minutes**, demonstrate that the AI Teacher is an **active, adaptive, multi-modal human-like educator** rather than a passive text-generating chatbot.

### Core Value Proof Points:
1. **Curriculum Synthesis**: Adapts lesson depth and section count to learner available time.
2. **Document Grounding (RAG)**: Ingests real courseware, grounding lessons with auditable citations.
3. **Subject-Aware Visuals & Audio-Avatar Sync**: Renders subject-specific diagrams with a live animated teacher avatar whose lips synchronize to spoken words.
4. **Cognitive Misconception Diagnosis & Adaptive Remediation**: Distinguishes flawed mental models from lack of knowledge and branches to an alternative analogy and visual.
5. **Context-Preserving Multilingual Teaching**: Switches language mid-lesson without losing progress or mastery.
6. **Cumulative Assessment & Dashboard**: Synthesizes a diagnostic report, revision recommendations, and next-topic progression.

---

## 2. Recommended Live Demo Scenario

* **Learner Name**: Alex Chen
* **Learner Level**: Beginner
* **Available Time**: 15 Minutes (Balanced 3-Section Curriculum)
* **Teaching Style**: Analogy-Driven
* **Primary Topic**: Binary Trees (or Attendance & Time-Off via uploaded document)
* **Demo Language Flow**: Start in English (`en`) $\to$ Switch to Tamil (`ta`) or Hindi (`hi`) mid-lesson.

---

## 3. Step-by-Step Demo Sequence & Presenter Script

### Step 0: Pre-Flight Check (Before Presentation)
1. Backend running: `python -m uvicorn backend.main:app --port 8000 --reload`
2. Frontend running: `npm run dev` (in `frontend/`, port 5173)
3. Open browser to `http://localhost:5173`
4. Confirm Readiness: `http://localhost:8000/api/v1/readiness` returns `"status": "OPERATIONAL"`.

---

### Step 1: Learner Setup & Time Selection (1:00)

* **Action**: On the Landing / Setup screen:
  - Enter Learner Name: **Alex Chen**
  - Select Level: **Beginner**
  - Select Time: **15 Minutes**
  - Select Style: **Analogy-Driven**
  - Select Topic: **Binary Trees**
* **Presenter Script**:
  > *"Judges, traditional digital courses force every learner through a static video wall or text outline. The AI Teacher begins by profiling the student. Notice I've chosen 15 minutes. Instead of simply trimming a transcript, the Lesson Planner adapts the actual curriculum structure: generating a 3-section mastery progression from foundational intuition, through mechanics, to real-world trade-offs."*

---

### Step 2: Ingesting Educational Courseware (RAG) (1:00)

* **Action**:
  - In the Document Upload section, upload `Binary_Trees_Lecture.md` (or a PDF/DOCX file).
  - Click **Ingest Material**.
  - Show the ingestion badge: `READY: 2 chunks indexed`.
* **Presenter Script**:
  > *"The AI Teacher is document-grounded. It accepts PDFs, Word documents, PowerPoints, or Markdown. Our RAG engine extracts layout text, applies semantic chunking along section boundaries, and generates dense vector embeddings. Notice the persistent grounding badge—the lesson plan and every subsequent scene are now grounded directly in our uploaded syllabus with full source citations."*

---

### Step 3: Launch Teaching Studio — Visuals & Lip-Synchronized Avatar (1:30)

* **Action**:
  - Click **Start Interactive Lesson**.
  - Highlight the Cinema Video Studio:
    - **Teacher Avatar**: Points directionally at the visual stage; lips articulate speech visemes (`OPEN`, `HALF_OPEN`, `NARROW`, `REST`) synchronized to the audio.
    - **Visual Stage**: Renders a dynamic SVG Binary Tree with glowing root (50), left child (25), and right child (75).
    - **Live Karaoke Subtitles**: Text words highlight in sync with the spoken voice.
    - **RAG Citation Badge**: Click the badge to reveal the source excerpt from the uploaded lecture.
* **Presenter Script**:
  > *"Welcome to the Teaching Studio. The AI Teacher is not a chat box. It generates atomic 4-scene video sequences. Notice two critical features: First, the avatar is lip-synchronized to neural speech using sub-second word boundaries. Second, the visual stage is subject-aware—because our topic is Data Structures, it automatically generates an interactive SVG tree diagram rather than generic clip art."*

---

### Step 4: Interactive Checkpoint & Misconception Diagnosis (1:30)

* **Action**:
  - Let playback reach **Scene 4 (Checkpoint Prompt)** or click **Jump to Checkpoint**.
  - Observe the video pause automatically: the avatar enters a `THINK` gesture with a tilted head.
  - The Question is displayed: *"What is the maximum number of children any single node can have in a Binary Tree?"*
  - **Deliberately select the incorrect misconception**: **"Option C: Must always have exactly 2 children"**.
  - Click **Submit Answer**.
* **Presenter Script**:
  > *"Now watch what happens at the checkpoint. The video halts automatically. Traditional e-learning would simply mark this answer as 'Wrong, 0/1'. But our Misconception Detector analyzes the cognitive root cause: it diagnoses that Alex has overgeneralized the word 'binary' into mandatory equality, forgetting that leaf nodes have zero children."*

---

### Step 5: Adaptive Remediation Scene (Scene 3-R) (1:00)

* **Action**:
  - Show the **Adaptive Remediation Alert**: The engine branches to **Scene 3-R**.
  - Avatar shifts to `ENCOURAGING` posture with open supportive palms.
  - The teacher narrates a concrete counter-analogy: *"Think of a bicycle rack built for at most two bikes. It can hold zero, one, or two bikes—it does not collapse if only one bike is parked!"*
  - Student re-evaluates by selecting **"Option B: At most 2 children (0, 1, or 2)"**.
  - System awards mastery and advances to Section 2.
* **Presenter Script**:
  > *"Notice that the system dynamically injected a brand new remediation scene into the video timeline before allowing the student to advance. It replaced the abstract formula with a tangible bicycle rack analogy. When Alex corrects their understanding, concept mastery updates immediately."*

---

### Step 6: Mid-Lesson Multilingual Switch (0:45)

* **Action**:
  - In the studio header, open the Language Selector and choose **Tamil (🇮🇳 தமிழ்)** or **Hindi (🇮🇳 हिन्दी)**.
  - Play the scene: The avatar immediately speaks in the chosen language with native script subtitles and neural voice (`ta-IN-PallaviNeural` or `hi-IN-SwaraNeural`).
  - Point out that **English technical terms** (`Binary Tree`, `Root Node`) are preserved in Bilingual STEM mode, and the current section index and mastery scores did not reset.
* **Presenter Script**:
  > *"Education is global. With one click, I can switch our teaching language to Tamil. Notice that the session did not restart. We are still on Section 2, Alex's mastery scores are preserved, and in bilingual STEM mode, core technical terms like 'Binary Tree' remain in English so students retain global engineering fluency."*

---

### Step 7: Final Assessment & Comprehensive Learning Dashboard (0:45)

* **Action**:
  - Click **Complete Lesson / Final Assessment**.
  - Submit the 3-question diagnostic assessment.
  - Showcase the **Learning Report & Dashboard**:
    - Concept Mastery Gauge.
    - Understood Concepts vs. Concepts Needing Revision.
    - Concrete Revision Recommendations with pedagogical rationales.
    - Next-Topic Roadmap: *"Binary Search Trees (BST) & Self-Balancing Trees"*.
* **Presenter Script**:
  > *"At lesson completion, the AI Teacher generates a diagnostic learning report and updates the student's persistent mastery vector in our SQLite database. It pinpoints exactly what Alex understood, what needs revision, and prescribes the next topic on their learning journey. This closes the full pedagogical loop: Understand, Plan, Explain, Demonstrate, Question, Evaluate, Adapt, and Progress."*

---

## 4. What to Explicitly Highlight to Judges

1. **Not a Wrapper**: This is a multi-agent state machine orchestrating 8 specialized pedagogical modules, not an unconstrained ChatGPT prompt.
2. **Offline-First Zero-Cost Architecture**: Every single feature runs 100% offline out-of-the-box using deterministic local intelligence and offline embeddings.
3. **Sub-Second Lip-Sync**: Show that mouth visemes (`OPEN`, `HALF_OPEN`, `NARROW`, `REST`) track actual word timestamps.
4. **Pedagogical Invariant**: Students cannot skip or bypass active misconceptions; the system always intervenes with counter-analogies.
5. **Domain-Agnostic RAG Grounding**: Uploading any technical or non-technical document dynamically extracts authentic concepts without leaking unrelated templates.

---

## 5. Edge Cases to Avoid During Presentation

* **Do NOT upload unsupported file types**: Avoid legacy `.doc` or `.ppt` files (use modern `.docx`, `.pptx`, `.pdf`, `.md`, or `.txt`).
* **Do NOT close the backend terminal**: Ensure the Uvicorn server stays active in the background.
* **Do NOT disconnect the browser tab**: If you refresh the browser, your session ID is stored in memory; use the setup wizard to start fresh.

---

## 6. Backup Demo Path (If Cloud or Network Fails)

The AI Teacher is engineered with **100% offline resilience**:

* **If Gemini API times out or internet drops**:
  - The system automatically engages the **Deterministic Teaching Provider** (`ai_engine/providers/mock_provider.py`). All lesson planning, explanations, and questions continue instantly with zero UI errors.
* **If Microsoft Edge TTS cannot connect**:
  - The system automatically falls back to **MockSpeechProvider** (`ai_engine/providers/speech_provider.py`), generating local synthetic WAV audio and word timings.
  - Concurrently, the frontend falls back to the browser's built-in **Web Speech API** (`window.speechSynthesis`), ensuring voice narration plays regardless of internet access.
* **If no browser audio output device is present**:
  - The visual karaoke subtitle bar displays the exact synchronized text cues alongside the avatar mouth animations.
